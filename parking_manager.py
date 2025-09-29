from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import uuid
import json
import pandas as pd
from dataclasses import dataclass, asdict
from enum import Enum

class SlotStatus(Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"

@dataclass
class ParkingSlot:
    slot_id: str
    status: SlotStatus
    vehicle_type: Optional[str] = None
    vehicle_number: Optional[str] = None
    arrival_time: Optional[datetime] = None
    pickup_time: Optional[datetime] = None
    reservation_time: Optional[datetime] = None

@dataclass
class Transaction:
    id: str
    slot_id: str
    vehicle_type: str
    vehicle_number: str
    arrival_time: datetime
    departure_time: datetime
    amount: float
    timestamp: datetime

class ParkingManager:
    def __init__(self, total_slots: int = 20):
        self.total_slots = total_slots
        self.slots: Dict[str, ParkingSlot] = {}
        self.transactions: List[Transaction] = []
        self.total_revenue: float = 0.0
        
        # Initialize slots
        for i in range(1, total_slots + 1):
            slot_id = f"slot_{i}"
            self.slots[slot_id] = ParkingSlot(
                slot_id=slot_id,
                status=SlotStatus.AVAILABLE
            )
        
        # Load holidays data from CSV
        try:
            self.holidays = pd.read_csv("West_Bengal_Holidays_2025.csv")
            self.holidays['Date'] = pd.to_datetime(self.holidays['Date'], format='%d-%m-%Y')
        except FileNotFoundError:
            print("Warning: West_Bengal_Holidays_2025.csv not found. Using default holiday data.")
            # Fallback to default holidays
            self.holidays = pd.DataFrame([
                {'Date': '01-01-2025', 'Holiday Name': 'New Year\'s Day', 'Rush Hr From': '00:00', 'Rush Hr To': '23:59'},
                {'Date': '26-01-2025', 'Holiday Name': 'Republic Day', 'Rush Hr From': '08:00', 'Rush Hr To': '14:00'},
                {'Date': '02-02-2025', 'Holiday Name': 'Vasant Panchami', 'Rush Hr From': '09:00', 'Rush Hr To': '17:00'},
                {'Date': '26-02-2025', 'Holiday Name': 'Maha Shivaratri', 'Rush Hr From': '09:00', 'Rush Hr To': '17:00'},
                {'Date': '13-03-2025', 'Holiday Name': 'Holika Dahana', 'Rush Hr From': '09:00', 'Rush Hr To': '22:00'},
                {'Date': '14-03-2025', 'Holiday Name': 'Holi', 'Rush Hr From': '09:00', 'Rush Hr To': '20:00'},
                {'Date': '28-03-2025', 'Holiday Name': 'Jamat Ul-Vida', 'Rush Hr From': '09:00', 'Rush Hr To': '17:00'},
                {'Date': '30-03-2025', 'Holiday Name': 'Chaitra Sukhladi / Ugadi / Gudi Padwa', 'Rush Hr From': '09:00', 'Rush Hr To': '17:00'},
                {'Date': '31-03-2025', 'Holiday Name': 'Eid-ul-Fitr', 'Rush Hr From': '08:00', 'Rush Hr To': '21:00'},
                {'Date': '06-04-2025', 'Holiday Name': 'Rama Navami', 'Rush Hr From': '09:00', 'Rush Hr To': '17:00'},
                {'Date': '10-04-2025', 'Holiday Name': 'Mahavir Jayanti', 'Rush Hr From': '09:00', 'Rush Hr To': '17:00'},
                {'Date': '18-04-2025', 'Holiday Name': 'Good Friday', 'Rush Hr From': '08:00', 'Rush Hr To': '16:00'},
                {'Date': '12-05-2025', 'Holiday Name': 'Buddha Purnima', 'Rush Hr From': '09:00', 'Rush Hr To': '18:00'},
                {'Date': '07-06-2025', 'Holiday Name': 'Eid ul-Adha (Bakrid)', 'Rush Hr From': '08:00', 'Rush Hr To': '21:00'},
                {'Date': '06-07-2025', 'Holiday Name': 'Muharram', 'Rush Hr From': '07:00', 'Rush Hr To': '19:00'},
                {'Date': '09-08-2025', 'Holiday Name': 'Raksha Bandhan', 'Rush Hr From': '10:00', 'Rush Hr To': '18:00'},
                {'Date': '15-08-2025', 'Holiday Name': 'Independence Day', 'Rush Hr From': '08:00', 'Rush Hr To': '14:00'},
                {'Date': '16-08-2025', 'Holiday Name': 'Janmashtami', 'Rush Hr From': '08:00', 'Rush Hr To': '23:00'},
                {'Date': '27-08-2025', 'Holiday Name': 'Ganesh Chaturthi', 'Rush Hr From': '08:00', 'Rush Hr To': '21:00'},
                {'Date': '05-09-2025', 'Holiday Name': 'Milad-un-Nabi / Onam', 'Rush Hr From': '09:00', 'Rush Hr To': '17:00'},
                {'Date': '29-09-2025', 'Holiday Name': 'Maha Saptami', 'Rush Hr From': '06:00', 'Rush Hr To': '23:59'},
                {'Date': '30-09-2025', 'Holiday Name': 'Maha Ashtami', 'Rush Hr From': '06:00', 'Rush Hr To': '23:59'},
                {'Date': '01-10-2025', 'Holiday Name': 'Maha Navami', 'Rush Hr From': '06:00', 'Rush Hr To': '23:59'},
                {'Date': '02-10-2025', 'Holiday Name': 'Mahatma Gandhi Jayanti / Dussehra', 'Rush Hr From': '08:00', 'Rush Hr To': '17:00'},
                {'Date': '07-10-2025', 'Holiday Name': 'Maharishi Valmiki Jayanti', 'Rush Hr From': '09:00', 'Rush Hr To': '17:00'},
                {'Date': '20-10-2025', 'Holiday Name': 'Diwali', 'Rush Hr From': '10:00', 'Rush Hr To': '23:59'},
                {'Date': '22-10-2025', 'Holiday Name': 'Govardhan Puja', 'Rush Hr From': '09:00', 'Rush Hr To': '18:00'},
                {'Date': '23-10-2025', 'Holiday Name': 'Bhai Duj', 'Rush Hr From': '10:00', 'Rush Hr To': '18:00'},
                {'Date': '05-11-2025', 'Holiday Name': 'Guru Nanak Jayanti', 'Rush Hr From': '09:00', 'Rush Hr To': '19:00'},
                {'Date': '24-11-2025', 'Holiday Name': 'Guru Tegh Bahadur\'s Martyrdom Day', 'Rush Hr From': '09:00', 'Rush Hr To': '17:00'},
                {'Date': '25-12-2025', 'Holiday Name': 'Christmas Day', 'Rush Hr From': '09:00', 'Rush Hr To': '22:00'},
                {'Date': '31-12-2025', 'Holiday Name': 'New Year\'s Eve', 'Rush Hr From': '00:00', 'Rush Hr To': '23:59'}
            ])
            self.holidays['Date'] = pd.to_datetime(self.holidays['Date'])
        
        # Pricing configuration - Updated to match new system
        self.standard_rate = {"Car": 200, "Bike": 150, "Truck": 300}
        self.rush_extra = {"Car": 50, "Bike": 30, "Truck": 70}
        self.night_rate = 100
    
    def calculate_parking_fee(self, vehicle_type: str, arrival_dt: datetime, departure_dt: datetime) -> Dict:
        """Calculate parking fee using the new datetime-based logic"""
        delta = departure_dt - arrival_dt
        total_seconds = delta.total_seconds()
        full_hours = int(total_seconds // 3600)
        partial_hour = total_seconds % 3600 > 0

        standard_hours = rush_hours = night_hours = 0

        for hour in range(full_hours):
            current_time = arrival_dt + timedelta(hours=hour)
            current_date = current_time.date()
            current_weekday = current_time.strftime("%a")
            current_hour = current_time.hour

            # Check for holidays
            holiday = self.holidays[self.holidays['Date'] == pd.Timestamp(current_date)]
            is_holiday = not holiday.empty
            
            if is_holiday:
                rush_start = datetime.strptime(holiday['Rush Hr From'].values[0], "%H:%M").hour
                rush_end = datetime.strptime(holiday['Rush Hr To'].values[0], "%H:%M").hour
                if rush_start <= current_hour < rush_end:
                    rush_hours += 1
                    continue
            else:
                # Regular rush hours
                if (current_weekday == "Fri" and current_hour >= 17) or \
                   (current_weekday in ["Sat", "Sun"] and current_hour >= 11):
                    rush_hours += 1
                    continue

            # Night hours condition (11 PM to 5 AM)
            if current_hour >= 23 or current_hour < 5:
                night_hours += 1
            else:
                standard_hours += 1
            
        standard_charge = standard_hours * self.standard_rate[vehicle_type]
        rush_charge = rush_hours * (self.standard_rate[vehicle_type] + self.rush_extra[vehicle_type])
        night_charge = night_hours * self.night_rate
        total = standard_charge + rush_charge + night_charge
        
        return {
            'duration_hours': full_hours + (0.5 if partial_hour else 0),
            'regular_hours': standard_hours,
            'rush_hours': rush_hours,
            'night_hours': night_hours,
            'base_rate': self.standard_rate[vehicle_type],
            'rush_surcharge': self.rush_extra[vehicle_type],
            'night_rate': self.night_rate,
            'total_cost': round(total, 2),
            'standard_charge': standard_charge,
            'rush_charge': rush_charge,
            'night_charge': night_charge
        }
    
    def get_available_slots(self) -> List[str]:
        """Get list of available parking slots"""
        return [slot_id for slot_id, slot in self.slots.items() 
                if slot.status == SlotStatus.AVAILABLE]
    
    def get_occupied_slots(self) -> List[str]:
        """Get list of occupied parking slots"""
        return [slot_id for slot_id, slot in self.slots.items() 
                if slot.status == SlotStatus.OCCUPIED]
    
    def get_reserved_slots(self) -> List[str]:
        """Get list of reserved parking slots"""
        return [slot_id for slot_id, slot in self.slots.items() 
                if slot.status == SlotStatus.RESERVED]
    
    def park_vehicle(self, vehicle_type: str, vehicle_number: str, 
                    arrival_dt: datetime, pickup_dt: datetime) -> tuple[bool, str]:
        """Park a vehicle using automatic slot assignment"""
        available_slots = self.get_available_slots()
        
        if not available_slots:
            return False, ""
        
        # Smart slot assignment logic
        if vehicle_type == "Truck":
            # Trucks get the highest available slot number (for larger vehicles)
            slot_numbers = [int(slot.split('_')[1]) for slot in available_slots]
            selected_slot_num = max(slot_numbers)
        else:
            # Cars and Bikes get the lowest available slot number (efficient space usage)
            slot_numbers = [int(slot.split('_')[1]) for slot in available_slots]
            selected_slot_num = min(slot_numbers)
        
        slot_id = f"slot_{selected_slot_num}"
        
        self.slots[slot_id] = ParkingSlot(
            slot_id=slot_id,
            status=SlotStatus.OCCUPIED,
            vehicle_type=vehicle_type,
            vehicle_number=vehicle_number.upper(),
            arrival_time=arrival_dt,
            pickup_time=pickup_dt
        )
        
        return True, slot_id
    
    def reserve_slot(self, vehicle_type: str, vehicle_number: str, 
                    reservation_dt: datetime, duration_hours: int) -> tuple[bool, str]:
        """Reserve a parking slot using automatic slot assignment"""
        available_slots = self.get_available_slots()
        
        if not available_slots:
            return False, ""
        
        # Smart slot assignment logic (same as park_vehicle)
        if vehicle_type == "Truck":
            # Trucks get the highest available slot number
            slot_numbers = [int(slot.split('_')[1]) for slot in available_slots]
            selected_slot_num = max(slot_numbers)
        else:
            # Cars and Bikes get the lowest available slot number
            slot_numbers = [int(slot.split('_')[1]) for slot in available_slots]
            selected_slot_num = min(slot_numbers)
        
        slot_id = f"slot_{selected_slot_num}"
        pickup_dt = reservation_dt + timedelta(hours=duration_hours)
        
        self.slots[slot_id] = ParkingSlot(
            slot_id=slot_id,
            status=SlotStatus.RESERVED,
            vehicle_type=vehicle_type,
            vehicle_number=vehicle_number.upper(),
            pickup_time=pickup_dt,
            reservation_time=reservation_dt
        )
        
        return True, slot_id
    
    def remove_vehicle(self, slot_id: str, departure_dt: datetime) -> Optional[Dict]:
        """Remove a vehicle and generate bill"""
        if slot_id not in self.slots or self.slots[slot_id].status != SlotStatus.OCCUPIED:
            return None
        
        slot = self.slots[slot_id]
        
        bill_data = self.calculate_parking_fee(
            slot.vehicle_type,
            slot.arrival_time,
            departure_dt
        )
        
        transaction = Transaction(
            id=str(uuid.uuid4()),
            slot_id=slot_id,
            vehicle_type=slot.vehicle_type,
            vehicle_number=slot.vehicle_number,
            arrival_time=slot.arrival_time,
            departure_time=departure_dt,
            amount=bill_data['total_cost'],
            timestamp=datetime.now()
        )
        
        self.transactions.append(transaction)
        self.total_revenue += bill_data['total_cost']
        
        # Clear the slot
        self.slots[slot_id] = ParkingSlot(
            slot_id=slot_id,
            status=SlotStatus.AVAILABLE
        )
        
        return {**bill_data, **asdict(transaction)}
    
    def search_vehicle(self, query: str) -> List[Tuple[str, ParkingSlot]]:
        """Search for vehicle by number"""
        results = []
        for slot_id, slot in self.slots.items():
            if (slot.vehicle_number and 
                query.upper() in slot.vehicle_number.upper()):
                results.append((slot_id, slot))
        return results
    
    def get_slot_data(self, slot_id: str) -> Optional[ParkingSlot]:
        """Get slot data"""
        return self.slots.get(slot_id)
    
    def get_statistics(self) -> Dict:
        """Get parking statistics"""
        available_count = len(self.get_available_slots())
        occupied_count = len(self.get_occupied_slots())
        reserved_count = len(self.get_reserved_slots())
        occupancy_rate = (occupied_count / self.total_slots) * 100
        
        return {
            'total_slots': self.total_slots,
            'available_count': available_count,
            'occupied_count': occupied_count,
            'reserved_count': reserved_count,
            'occupancy_rate': round(occupancy_rate, 1),
            'total_revenue': self.total_revenue,
            'total_transactions': len(self.transactions)
        }
    
    def get_recent_transactions(self, limit: int = 10) -> List[Dict]:
        """Get recent transactions"""
        sorted_transactions = sorted(
            self.transactions,
            key=lambda x: x.departure_time,
            reverse=True
        )
        
        return [asdict(t) for t in sorted_transactions[:limit]]
    
    def clear_all_data(self):
        """Clear all parking data (admin function)"""
        for i in range(1, self.total_slots + 1):
            slot_id = f"slot_{i}"
            self.slots[slot_id] = ParkingSlot(
                slot_id=slot_id,
                status=SlotStatus.AVAILABLE
            )
        
        self.transactions = []
        self.total_revenue = 0.0

# Global instance
parking_manager = ParkingManager()
