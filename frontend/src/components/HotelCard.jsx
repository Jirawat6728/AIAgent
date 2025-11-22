import React from 'react';

export default function HotelCard({ hotel }) {
  // `hotel` คือ object ที่มี 'name' และ 'offers' จาก main.py

  return (
    <div className="hotel-card">
      
      {/* ส่วน Header (ชื่อโรงแรม) */}
      <div className="hotel-card-header">
        <span className="hotel-icon">🏨</span>
        <h4 className="hotel-name">{hotel.name}</h4>
      </div>

      {/* ส่วน Body (รายการข้อเสนอห้องพัก) */}
      <div className="hotel-card-body">
        {hotel.offers.length > 0 ? (
          hotel.offers.map((offer, index) => (
            <div className="hotel-offer" key={index}>
              <span className="hotel-room-type">
                {/* Amadeus อาจส่ง 'category' มาเป็น 'STANDARD', 'DELUXE' ฯลฯ */}
                {offer.room || 'Standard Room'}
              </span>
              <span className="hotel-price">
                {offer.price}
              </span>
            </div>
          ))
        ) : (
          <div className="hotel-offer-none">
            <p>ไม่พบราคาสำหรับข้อเสนอนี้</p>
          </div>
        )}
      </div>

    </div>
  );
}