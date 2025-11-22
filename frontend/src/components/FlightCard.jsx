import React from 'react';

// (ฟังก์ชันตัวช่วย สามารถวางไว้นอก Component หรือในไฟล์ helpers.js ก็ได้)
// 1. ฟังก์ชันจัดรูปแบบเวลา (เช่น 2025-11-20T10:30:00 -> 10:30)
const formatTime = (isoString) => {
  if (!isoString) return '';
  try {
    return new Date(isoString).toLocaleTimeString('th-TH', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    });
  } catch (error) {
    return isoString;
  }
};

// 2. ฟังก์ชันจัดรูปแบบระยะเวลา (เช่น PT2H30M -> 2h 30m)
const formatDuration = (duration) => {
  if (!duration) return '';
  return duration
    .replace('PT', '')
    .replace('H', 'h ')
    .replace('M', 'm');
};

export default function FlightCard({ flight }) {
  // `flight` คือ object ที่มี 'price' และ 'segments' จาก main.py

  // เราจะแสดงข้อมูลของ segment แรกสุด (สำหรับการ์ดสรุป)
  const firstSegment = flight.segments[0];
  // และ segment สุดท้าย
  const lastSegment = flight.segments[flight.segments.length - 1];
  
  // นับจำนวนการต่อเครื่อง
  const stops = flight.segments.length - 1;

  return (
    <div className="flight-card">
      
      {/* ส่วนราคา (Header) */}
      <div className="flight-card-header">
        <span className="flight-price">{flight.price}</span>
        <span className="flight-stops">
          {stops === 0 ? 'Direct (บินตรง)' : `${stops} Stop(s)`}
        </span>
      </div>

      {/* ส่วนรายละเอียดการบิน */}
      <div className="flight-card-body">
        <div className="flight-airline">
          ✈️ {firstSegment.airline}
        </div>
        <div className="flight-departure">
          <div className="flight-time">{formatTime(firstSegment.departure.time)}</div>
          <div className="flight-airport">{firstSegment.departure.airport}</div>
        </div>
        <div className="flight-arrow">
          <div className="flight-duration">{formatDuration(firstSegment.duration)}</div>
          <div className="arrow-line"></div>
          <div className="arrow-plane">→</div>
        </div>
        <div className="flight-arrival">
          <div className="flight-time">{formatTime(firstSegment.arrival.time)}</div>
          <div className="flight-airport">{firstSegment.arrival.airport}</div>
        </div>
      </div>
      
      {/* ถ้ามีหลาย segments (ต่อเครื่อง) ให้แสดงข้อมูลสรุปการเดินทางทั้งหมด */}
      {stops > 0 && (
        <div className="flight-card-footer">
          <span>
            <b>การเดินทางทั้งหมด:</b> {firstSegment.departure.airport} → {lastSegment.arrival.airport}
          </span>
        </div>
      )}

    </div>
  );
}