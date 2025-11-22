import React from 'react';

// ฟังก์ชันตัวช่วย: แปลง 'category' เป็นไอคอน
const getCarCategoryIcon = (category) => {
  switch (category) {
    case 'MINI':
    case 'ECONOMY':
      return '🚗'; // รถเล็ก
    case 'COMPACT':
    case 'INTERMEDIATE':
    case 'STANDARD':
      return '🚙'; // รถขนาดกลาง
    case 'FULLSIZE':
    case 'LUXURY':
      return '🚘'; // รถขนาดใหญ่/หรู
    case 'SUV':
      return ' SUV';
    case 'VAN':
      return '🚐'; // รถตู้
    default:
      return '🚗';
  }
};

export default function CarCard({ car }) {
  // `car` คือ object จาก main.py

  return (
    <div className="car-card">
      
      {/* ส่วน Header (ผู้ให้บริการ) */}
      <div className="car-card-header">
        <span className="car-provider">{car.provider_name}</span>
        <span className="car-price">{car.price}</span>
      </div>

      {/* ส่วน Body (รายละเอียดรถ) */}
      <div className="car-card-body">
        <div className="car-icon">
          {getCarCategoryIcon(car.category)}
        </div>
        <div className="car-details">
          <h5 className="car-type">{car.car_type}</h5>
          <span className="car-category">{car.category}</span>
        </div>
      </div>

    </div>
  );
}