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
gemini_model = genai.GenerativeModel('models/gemini-2.0-flash-exp')
print("✅ Gemini initialized")

print("🚀 Initializing Amadeus...")
amadeus = Client(
    client_id=os.getenv("AMADEUS_API_KEY"),
    client_secret=os.getenv("AMADEUS_API_SECRET")
)
print("✅ Amadeus initialized")

# System Prompt
SYSTEM_PROMPT = """คุณเป็นผู้ช่วยวางแผนการเดินทางและจองตั๋วที่เป็นมิตร ชื่อว่า "AI Travel Agent"

คุณสามารถ:
- ช่วยค้นหาเที่ยวบิน (flights) จากเมืองหนึ่งไปอีกเมืองหนึ่ง
- ช่วยหาที่พัก โรงแรม (hotels) ในเมืองต่างๆ
- แนะนำสถานที่ท่องเที่ยว
- ให้คำแนะนำการเดินทาง
- คุยเรื่องทั่วไปได้ตามปกติ แต่พยายามนำกลับมาที่การเดินทางอย่างเป็นธรรมชาติ

สไตล์การสื่อสาร:
- เป็นกันเอง ใช้ภาษาไทยผสมอังกฤษได้
- กระชับ ไม่ยาวเกินไป (2-4 ประโยค)
- เป็นธรรมชาติ ไม่เป็นทางการจนเกินไป
- ใช้อิโมจิให้น่ารัก เช่น ✈️ 🏨 🌍 😊
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

async def search_hotels(city_code: str, check_in: str, check_out: str):
    """Search hotels using Amadeus API"""
    try:
        if not check_in or not check_out:
            check_in = (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
            check_out = (date.today() + timedelta(days=9)).strftime('%Y-%m-%d')
        
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
        for hotel_data in offers.data[:5]:
            hotel = {
                'name': hotel_data['hotel']['name'],
                'offers': []
            }
            
            for offer in hotel_data['offers'][:2]:
                hotel['offers'].append({
                    'price': f"{offer['price']['total']} {offer['price']['currency']}",
                    'room': offer['room']['typeEstimated']['category']
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

@app.get("/")
async def root():
    return {"message": "AI Travel Agent API is running"}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        print(f"\n📨 Received: {request.message}")
        
        message_lower = request.message.lower()
        search_results = None
        
        # Step 1: Let AI analyze intent
        analysis_prompt = f"""วิเคราะห์ข้อความของผู้ใช้ว่าต้องการค้นหาเที่ยวบินหรือโรงแรมหรือไม่

ข้อความ: "{request.message}"

ตอบเป็น JSON เท่านั้น:
{{
  "intent": "flight" หรือ "hotel" หรือ "none",
  "origin": "รหัสสนามบิน 3 ตัว",
  "destination": "รหัสสนามบิน 3 ตัว",
  "city": "รหัสเมือง 3 ตัว",
  "has_date": true/false,
  "needs_more_info": true/false
}}

Airport codes:
Bangkok=BKK, Tokyo=NRT, New York=JFK, London=LHR, Paris=CDG, Singapore=SIN, 
Dubai=DXB, Los Angeles=LAX, Hong Kong=HKG, Seoul=ICN, Osaka=KIX, Phuket=HKT,
Chiang Mai=CNX, San Francisco=SFO, Sydney=SYD, Melbourne=MEL

City codes:
Bangkok=BKK, Tokyo=TYO, New York=NYC, London=LON, Paris=PAR, Singapore=SIN,
Dubai=DXB, Los Angeles=LAX, Hong Kong=HKG, Seoul=SEL, Osaka=OSA

ตัวอย่าง:
- "อยากไปโตเกียว" → {{"intent":"flight","origin":"BKK","destination":"NRT","has_date":false,"needs_more_info":true}}
- "I want to fly from Bangkok to Tokyo" → {{"intent":"flight","origin":"BKK","destination":"NRT","has_date":false,"needs_more_info":false}}
- "หาโรงแรมในนิวยอร์ก" → {{"intent":"hotel","city":"NYC","has_date":false,"needs_more_info":false}}
- "สวัสดี" → {{"intent":"none","needs_more_info":false}}

ถ้าข้อมูลครบพอที่จะค้นหา ให้ needs_more_info = false"""

        print("🔍 AI analyzing intent...")
        analysis_response = gemini_model.generate_content(analysis_prompt)
        analysis_text = analysis_response.text.strip()
        
        try:
            if "```json" in analysis_text:
                analysis_text = analysis_text.split("```json")[1].split("```")[0].strip()
            elif "```" in analysis_text:
                analysis_text = analysis_text.split("```")[1].split("```")[0].strip()
            
            intent_data = json.loads(analysis_text)
            print(f"🤖 Intent: {intent_data}")
        except Exception as e:
            print(f"⚠️ Parse error: {e}")
            intent_data = {"intent": "none", "needs_more_info": False}
        
        # Step 2: Execute search
        if intent_data.get("intent") == "flight" and not intent_data.get("needs_more_info"):
            origin = intent_data.get("origin")
            destination = intent_data.get("destination")
            
            if origin and destination:
                date_match = re.search(r'\d{4}-\d{2}-\d{2}', request.message)
                departure_date = date_match.group(0) if date_match else None
                
                flights = await search_flights(origin, destination, departure_date or (date.today() + timedelta(days=7)).strftime('%Y-%m-%d'))
                
                if flights:
                    search_results = {
                        'type': 'flights',
                        'data': flights,
                        'query': {
                            'origin': origin,
                            'destination': destination,
                            'departure_date': departure_date or (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
                        }
                    }
        
        elif intent_data.get("intent") == "hotel" and not intent_data.get("needs_more_info"):
            city = intent_data.get("city")
            
            if city:
                dates = re.findall(r'\d{4}-\d{2}-\d{2}', request.message)
                check_in = dates[0] if len(dates) > 0 else (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
                check_out = dates[1] if len(dates) > 1 else (date.today() + timedelta(days=9)).strftime('%Y-%m-%d')
                
                hotels = await search_hotels(city, check_in, check_out)
                
                if hotels:
                    search_results = {
                        'type': 'hotels',
                        'data': hotels,
                        'query': {
                            'city_code': city,
                            'check_in_date': check_in,
                            'check_out_date': check_out
                        }
                    }
        
        # Step 3: Generate response
        if search_results:
            if search_results['type'] == 'flights':
                num = len(search_results['data'])
                origin = search_results['query']['origin']
                dest = search_results['query']['destination']
                date_str = search_results['query']['departure_date']
                
                prompt = f"""{SYSTEM_PROMPT}

พบเที่ยวบิน {num} เที่ยว จาก {origin} ไป {dest} วันที่ {date_str}

ข้อความ: "{request.message}"

ตอบ:
1. บอกว่าเจอเที่ยวบิน {num} เที่ยว
2. แนะนำให้ดูรายละเอียดด้านล่าง
3. ถามว่าต้องการช่วยอะไรเพิ่ม

2-3 ประโยค มีอิโมจิ ✈️"""

            else:
                num = len(search_results['data'])
                city = search_results['query']['city_code']
                
                prompt = f"""{SYSTEM_PROMPT}

พบโรงแรม {num} แห่ง ใน {city}

ข้อความ: "{request.message}"

ตอบ:
1. บอกว่าเจอโรงแรม {num} แห่ง
2. แนะนำให้ดูรายละเอียด
3. ถามว่าต้องการค้นหาเพิ่มไหม

2-3 ประโยค มีอิโมจิ 🏨"""
        
        elif intent_data.get("needs_more_info"):
            if intent_data.get("intent") == "flight":
                missing = []
                if not intent_data.get("origin"):
                    missing.append("ต้นทาง")
                if not intent_data.get("destination"):
                    missing.append("ปลายทาง")
                if not intent_data.get("has_date"):
                    missing.append("วันที่")
                
                prompt = f"""{SYSTEM_PROMPT}

ผู้ใช้อยากหาเที่ยวบิน แต่ขาด: {', '.join(missing)}

ข้อความ: "{request.message}"

ตอบ:
1. รับว่าจะช่วยหา
2. ถามข้อมูลที่ขาดอย่างเป็นธรรมชาติ
3. ให้ตัวอย่าง

2-3 ประโยค มีอิโมจิ"""

            else:
                prompt = f"""{SYSTEM_PROMPT}

ผู้ใช้อยากหาโรงแรม แต่ยังขาดข้อมูล

ข้อความ: "{request.message}"

ตอบ:
1. รับว่าจะช่วยหา
2. ถามเมืองและวันที่
3. ให้ตัวอย่าง

2-3 ประโยค มีอิโมจิ"""
        
        else:
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
            "has_travel_intent": bool(search_results),
            "travel_data": search_results.get('query') if search_results else None,
            "search_results": search_results
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