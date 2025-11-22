from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import os
import google.generativeai as genai
from amadeus import Client, ResponseError
import re
import json
from datetime import datetime, date, timedelta

load_dotenv()

app = FastAPI(title="AI Travel Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize APIs
print("🚀 Initializing Gemini...")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('models/gemini-flash-latest') # (โมเดลที่ถูกต้อง)
print("✅ Gemini initialized")

print("🚀 Initializing Amadeus...")
amadeus = Client(
    client_id=os.getenv("AMADEUS_API_KEY"),
    client_secret=os.getenv("AMADEUS_API_SECRET")
)
print("✅ Amadeus initialized")

# System Prompt (เหมือนเดิม)
SYSTEM_PROMPT = """คุณเป็นผู้ช่วยวางแผนการเดินทางและจองตั๋วที่เป็นมิตร ชื่อว่า "AI Travel Agent"

คุณสามารถ:
- ช่วยค้นหาเที่ยวบิน (flights) จากเมืองหนึ่งไปอีกเมืองหนึ่ง
- ช่วยหาที่พัก โรงแรม (hotels) ในเมืองต่างๆ
- ช่วยค้นหารถเช่า (car rentals)
- แนะนำสถานที่ท่องเที่ยว
- ให้คำแนะนำการเดินทาง
- คุยเรื่องทั่วไปได้ตามปกติ แต่พยายามนำกลับมาที่การเดินทางอย่างเป็นธรรมชาติ

สไตล์การสื่อสาร:
- เป็นกันเอง ใช้ภาษาไทยผสมอังกฤษได้
- กระชับ ไม่ยาวเกินไป (2-4 ประโยค)
- เป็นธรรมชาติ ไม่เป็นทางการจนเกินไป
- ใช้อิโมจิให้น่ารัก เช่น ✈️ 🏨 🚗 🌍 😊
- ถ้าผู้ใช้ถามเรื่องอื่น ตอบได้ปกติ แล้วค่อยนำกลับมาถามว่า "ต้องการความช่วยเหลือเรื่องการเดินทางไหมคะ?"

ตัวอย่าง:
- User: "สวัสดี" → ตอบ: "สวัสดีค่ะ! 😊 ยินดีต้อนรับสู่ AI Travel Agent วันนี้อยากวางแผนเที่ยวที่ไหนดีคะ?"
- User: "อากาศวันนี้ยังไง" → ตอบ: "อากาศดีนะคะ! เหมาะกับการออกเดินทางเลย 🌤️ มีแผนจะไปเที่ยวที่ไหนไหมคะ?"
- User: "อยากไปญี่ปุ่น" → ตอบ: "ญี่ปุ่นน่าไปมากเลยค่ะ! 🇯🇵 อยากไปเมืองไหนคะ? โตเกียว โอซาก้า หรือเกียวโต? บอกวันที่ไปด้วยนะคะ แล้วหาเที่ยวบินให้"
"""

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = []

class ChatResponse(BaseModel):
    response: str
    has_travel_intent: bool
    travel_data: Optional[Dict[str, Any]] = None
    search_results: Optional[Dict[str, Any]] = None

# (ฟังก์ชัน search_flights เหมือนเดิม)
async def search_flights(origin: str, destination: str, departure_date: str):
    """Search flights using Amadeus API"""
    try:
        if not departure_date:
            departure_date = (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        print(f"✈️ Searching flights: {origin} → {destination} on {departure_date}")
        
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=departure_date,
            adults=1,
            max=5
        )
        
        flights = []
        for offer in response.data[:5]:
            flight = {
                'price': f"{offer['price']['total']} {offer['price']['currency']}",
                'segments': []
            }
            
            for itinerary in offer['itineraries']:
                for segment in itinerary['segments']:
                    flight['segments'].append({
                        'departure': {
                            'airport': segment['departure']['iataCode'],
                            'time': segment['departure']['at']
                        },
                        'arrival': {
                            'airport': segment['arrival']['iataCode'],
                            'time': segment['arrival']['at']
                        },
                        'airline': segment['carrierCode'],
                        'duration': segment['duration']
                    })
            
            flights.append(flight)
        
        print(f"✅ Found {len(flights)} flights")
        return flights
    
    except ResponseError as error:
        print(f"❌ Amadeus Error: {error}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# --- (นี่คือ Bug 1 ที่แก้ไขแล้ว) ---
async def search_hotels(city_code: str, check_in: str, check_out: str):
    """Search hotels using Amadeus API"""
    try:
        if not check_in:
            check_in = (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        if not check_out:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d')
            check_out = (check_in_date + timedelta(days=2)).strftime('%Y-%m-%d')
        
        print(f"🏨 Searching hotels in {city_code}: {check_in} to {check_out}")
        
        hotel_list = amadeus.reference_data.locations.hotels.by_city.get(
            cityCode=city_code
        )
        
        if not hotel_list.data:
            print("❌ No hotels found")
            return None
        
        hotel_ids = [h['hotelId'] for h in hotel_list.data[:5]]
        
        offers = amadeus.shopping.hotel_offers_search.get(
            hotelIds=','.join(hotel_ids),
            checkInDate=check_in,
            checkOutDate=check_out,
            adults=1
        )
        
        hotels = []
        # (แก้ไข) เพิ่ม .get() เพื่อป้องกัน 'NoneType' Error
        for hotel_data in offers.data[:5]:
            hotel_info = hotel_data.get('hotel')
            offers_info = hotel_data.get('offers')

            if not hotel_info or not offers_info:
                continue # ข้ามโรงแรมนี้ไป ถ้าข้อมูลไม่ครบ

            hotel = {
                'name': hotel_info.get('name', 'N/A'),
                'offers': []
            }
            
            for offer in offers_info[:2]:
                offer_price = offer.get('price', {})
                offer_room = offer.get('room', {}).get('typeEstimated', {})
                
                hotel['offers'].append({
                    'price': f"{offer_price.get('total', 'N/A')} {offer_price.get('currency', '')}",
                    'room': offer_room.get('category', 'N/A')
                })
            
            hotels.append(hotel)
        
        print(f"✅ Found {len(hotels)} hotels")
        return hotels
    
    except ResponseError as error:
        print(f"❌ Amadeus Error: {error}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
# --- (จบส่วนแก้ไข Bug 1) ---

# --- (นี่คือ Bug 2 ที่แก้ไขแล้ว) ---
async def search_car_rentals(city_code: str, pick_up_date: str, drop_off_date: str):
    """Search car rentals using Amadeus API"""
    try:
        if not pick_up_date:
            pick_up_date = (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        if not drop_off_date:
            pick_up_date_obj = datetime.strptime(pick_up_date, '%Y-%m-%d')
            drop_off_date = (pick_up_date_obj + timedelta(days=2)).strftime('%Y-%m-%d')
        
        print(f"🚗 Searching car rentals in {city_code}: {pick_up_date} to {drop_off_date}")
        
        # (แก้ไข) นี่คือชื่อ SDK ที่ถูกต้อง (car_rental_offers.get)
        response = amadeus.shopping.car_rental_offers.get(
            cityCode=city_code,
            pickUpDate=pick_up_date,
            dropOffDate=drop_off_date,
            lang='EN'
        )
        # ---
        
        if not response.data:
            print("❌ No car rentals found")
            return None

        cars = []
        # (แก้ไข) เพิ่ม .get() เพื่อป้องกัน Error
        for offer_data in response.data[:5]:
            provider = offer_data.get('provider', {})
            car = offer_data.get('car', {})
            price = offer_data.get('price', {})
            
            cars.append({
                'provider_name': provider.get('name', 'N/A'),
                'car_type': car.get('type', 'N/A'),
                'category': car.get('category', 'N/A'),
                'price': f"{price.get('total', 'N/A')} {price.get('currency', '')}"
            })
        
        print(f"✅ Found {len(cars)} car rental offers")
        return cars
    
    except ResponseError as error:
        print(f"❌ Amadeus Error (Car Rental): {error}")
        return None
    except Exception as e:
        print(f"❌ Error in search_car_rentals: {e}")
        return None
# --- (จบส่วนแก้ไข Bug 2) ---

@app.get("/")
async def root():
    return {"message": "AI Travel Agent API is running"}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        print(f"\n📨 Received: {request.message}")
        
        message_lower = request.message.lower()
        search_results = None
        
        # --- (Prompt อัจฉริยะ ทำงานได้ดีมาก!) ---
        # Step 1: Let AI analyze intent
        analysis_prompt = f"""วิเคราะห์ข้อความของผู้ใช้ และสร้าง "แผนการทำงาน" (Plan) เป็น List ของ JSON
    
ข้อความ: "{request.message}"
วันนี้คือวันที่: {date.today().strftime('%Y-%m-%d')}

"Plan" คือ List ของ Tool ที่ต้องเรียกใช้ตามลำดับ
Tool ที่มี: "search_flights", "search_hotels", "search_car_rentals"

ตอบเป็น JSON เท่านั้น ที่มี key "plan":
{{
  "plan": [
    {{
      "tool": "search_flights",
      "origin": "รหัสสนามบิน 3 ตัว",
      "destination": "รหัสสนามบิน 3 ตัว",
      "departure_date": "YYYY-MM-DD",
      "return_date": "YYYY-MM-DD" // (ถ้ามี)
    }},
    {{
      "tool": "search_hotels",
      "city": "รหัสเมือง 3 ตัว",
      "check_in_date": "YYYY-MM-DD",
      "check_out_date": "YYYY-MM-DD"
    }},
    {{
      "tool": "search_car_rentals",
      "city": "รหัสเมือง 3 ตัว",
      "pick_up_date": "YYYY-MM-DD",
      "drop_off_date": "YYYY-MM-DD"
    }}
  ]
}}

- ต้องสกัด "origin", "destination", และ "city" ออกมาให้ถูกต้อง
- **สำคัญมาก:** ต้องสกัด "วันที่" (departure_date, check_in_date, etc.) ออกมาเป็น YYYY-MM-DD ให้ถูกต้อง ถ้าผู้ใช้บอก "25 ธ.ค." (ปีนี้คือ {date.today().year}) ให้แปลงเป็น {date.today().year}-12-25
- ถ้าผู้ใช้แค่ทักทาย (intent "none") ให้ตอบ: {{"plan": []}}
- ถ้าข้อมูลไม่พอ (เช่น "อยากไปโตเกียว" แต่ไม่บอกต้นทาง) ให้ตอบ: {{"plan": [], "needs_more_info": "flight", "missing": ["origin", "date"]}}

Airport codes:
Bangkok=BKK, Tokyo=NRT, New York=JFK, London=LHR, Paris=CDG, Singapore=SIN, 
Dubai=DXB, Los Angeles=LAX, Hong Kong=HKG, Seoul=ICN, Osaka=KIX, Phuket=HKT,
Chiang Mai=CNX, San Francisco=SFO, Sydney=SYD, Melbourne=MEL

City codes:
Bangkok=BKK, Tokyo=TYO, New York=NYC, London=LON, Paris=PAR, Singapore=SIN,
Dubai=DXB, Los Angeles=LAX, Hong Kong=HKG, Seoul=SEL, Osaka=OSA

ตัวอย่าง:
- "สวัสดี" → {{"plan": []}}
- "หาเที่ยวบิน BKK ไป NRT วันที่ 2025-12-25" → {{"plan": [{{"tool": "search_flights", "origin": "BKK", "destination": "NRT", "departure_date": "2025-12-25"}}]}}
- "หาโรงแรมที่นิวยอร์ก วันที่ 10 ธ.ค. ถึง 15 ธ.ค." → {{"plan": [{{"tool": "search_hotels", "city": "NYC", "check_in_date": "{date.today().year}-12-10", "check_out_date": "{date.today().year}-12-15"}}]}}
- "หาเที่ยวบิน BKK-NRT วันที่ 2025-10-30, โรงแรมใน TYO, และรถเช่าใน TYO" → {{"plan": [{{"tool": "search_flights", "origin": "BKK", "destination": "NRT", "departure_date": "2025-10-30"}}, {{"tool": "search_hotels", "city": "TYO", "check_in_date": "2025-10-30"}}, {{"tool": "search_car_rentals", "city": "TYO", "pick_up_date": "2025-10-30"}}]}}
- "อยากไปเที่ยว" → {{"plan": [], "needs_more_info": "general", "missing": ["destination", "date"]}}
"""

        print("🔍 AI analyzing intent...")
        analysis_response = gemini_model.generate_content(analysis_prompt)
        analysis_text = analysis_response.text.strip()
        
        try:
            if "```json" in analysis_text:
                analysis_text = analysis_text.split("```json")[1].split("```")[0].strip()
            elif "```" in analysis_text:
                analysis_text = analysis_text.split("```")[1].split("```")[0].strip()
            
            intent_data = json.loads(analysis_text)
            print(f"🤖 Intent (Plan): {intent_data}")
        except Exception as e:
            print(f"⚠️ Parse error: {e}")
            intent_data = {"plan": [], "needs_more_info": False}
        
        # --- (ตรรกะ Step 2 เหมือนเดิม) ---
        # Step 2: Execute search
        plan = intent_data.get("plan", [])
        
        all_search_results = {
            "flights": None,
            "hotels": None,
            "cars": None
        }
        
        if plan:
            print(f"🤖 Executing plan with {len(plan)} steps...")
            for step in plan:
                tool_name = step.get("tool")
                
                if tool_name == "search_flights":
                    origin = step.get("origin")
                    destination = step.get("destination")
                    departure_date = step.get("departure_date")
                    
                    if origin and destination:
                        flights = await search_flights(origin, destination, departure_date)
                        if flights:
                            all_search_results["flights"] = {
                                'data': flights,
                                'query': {
                                    'origin': origin,
                                    'destination': destination,
                                    'departure_date': departure_date or (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
                                }
                            }

                elif tool_name == "search_hotels":
                    city = step.get("city")
                    check_in = step.get("check_in_date")
                    check_out = step.get("check_out_date")
                    
                    if city:
                        hotels = await search_hotels(city, check_in, check_out)
                        if hotels:
                            all_search_results["hotels"] = {
                                'data': hotels,
                                'query': {
                                    'city_code': city,
                                    'check_in_date': check_in,
                                    'check_out_date': check_out
                                }
                            }

                elif tool_name == "search_car_rentals":
                    city = step.get("city")
                    pick_up = step.get("pick_up_date")
                    drop_off = step.get("drop_off_date")
                    
                    if city:
                        cars = await search_car_rentals(city, pick_up, drop_off)
                        if cars:
                            all_search_results["cars"] = {
                                'data': cars,
                                'query': {
                                    'city_code': city,
                                    'pick_up_date': pick_up,
                                    'drop_off_date': drop_off
                                }
                            }
        
        # Step 3: Generate response (เหมือนเดิม)
        has_results = any(all_search_results.values())
        
        if has_results:
            summary_parts = []
            if all_search_results["flights"]:
                summary_parts.append(f"พบเที่ยวบิน {len(all_search_results['flights']['data'])} เที่ยว ✈️")
            if all_search_results["hotels"]:
                summary_parts.append(f"พบโรงแรม {len(all_search_results['hotels']['data'])} แห่ง 🏨")
            if all_search_results["cars"]:
                summary_parts.append(f"พบรถเช่า {len(all_search_results['cars']['data'])} คัน 🚗")
            
            summary = " และ ".join(summary_parts)
            
            prompt = f"""{SYSTEM_PROMPT}

ฉันทำงานตามแผนที่วางไว้ และได้ผลลัพธ์ดังนี้:
{summary}

ข้อความเดิม: "{request.message}"

ตอบ:
1. สรุปผลลัพธ์ที่เจอ (เช่น: "เจอ 5 เที่ยวบิน และ 3 โรงแรมค่ะ!")
2. แนะนำให้ดูรายละเอียดด้านล่าง
3. ถามว่าต้องการช่วยอะไรเพิ่ม

2-3 ประโยค มีอิโมจิ"""

        elif intent_data.get("needs_more_info"):
            missing = ", ".join(intent_data.get("missing", []))
            prompt = f"""{SYSTEM_PROMPT}

ผู้ใช้ต้องการบางอย่าง แต่ข้อมูลไม่ครบ
ขาดข้อมูล: {missing}

ข้อความ: "{request.message}"

ตอบ:
1. รับทราบ
2. ถามข้อมูลที่ขาด
3. ให้ตัวอย่าง

2-3 ประโยค มีอิโมจิ"""
        
        else: # (กรณี intent "none" หรือ plan: [])
            prompt = f"""{SYSTEM_PROMPT}

ข้อความ: "{request.message}"

ตอบอย่างเป็นธรรมชาติ:
- ถ้าทักทาย → ทักทายและแนะนำตัว
- ถ้าถามอื่น → ตอบแล้วถามเรื่องเดินทาง
- ถ้าถามเดินทาง → ให้ข้อมูลและชวนค้นหา

2-4 ประโยค มีอิโมจิ"""
        
        print("🤖 Generating response...")
        response = gemini_model.generate_content(prompt)
        ai_text = response.text
        print(f"✅ Done: {ai_text[:80]}...")
        
        return {
            "response": ai_text,
            "has_travel_intent": has_results,
            "travel_data": None,
            "search_results": all_search_results
        }
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting AI Travel Agent Backend...")
    print("📍 Backend: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)