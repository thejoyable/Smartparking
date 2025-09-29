#!/usr/bin/env python3

import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import os
from parking_manager import ParkingManager, SlotStatus, ParkingSlot

class CSVDataManager:
    """Manages parking data in CSV format compatible with the original ParkingSystem"""
    
    def __init__(self, csv_filename: str = "parking_data.csv"):
        self.csv_filename = csv_filename
        self.expected_columns = [
            "Slot", "VehicleType", "VehicleNumber", "ArrivalDate", 
            "ArrivalTime", "ExpectedPickupDate", "ExpectedPickupTime", 
            "Weekday", "Charge"
        ]
        self.parking_manager = ParkingManager()
        self._load_from_csv()
    
    def _load_from_csv(self):
        """Load parking data from CSV file into ParkingManager"""
        try:
            if os.path.exists(self.csv_filename):
                df = pd.read_csv(self.csv_filename)
                print(f"Loading parking data from {self.csv_filename}...")
                
                # Clear existing data
                self.parking_manager = ParkingManager()
                
                # Load data from CSV
                for _, row in df.iterrows():
                    slot_num = int(row['Slot'])
                    slot_id = f"slot_{slot_num}"
                    
                    # Check if slot has vehicle data
                    if pd.notna(row['VehicleType']) and pd.notna(row['VehicleNumber']):
                        # Parse dates and times
                        arrival_date = row['ArrivalDate']
                        arrival_time = row['ArrivalTime']
                        pickup_date = row['ExpectedPickupDate']
                        pickup_time = row['ExpectedPickupTime']
                        
                        try:
                            arrival_dt = datetime.strptime(f"{arrival_date} {arrival_time}", "%d-%m-%y %H:%M")
                            pickup_dt = datetime.strptime(f"{pickup_date} {pickup_time}", "%d-%m-%y %H:%M")
                            
                            # Create occupied slot
                            self.parking_manager.slots[slot_id] = ParkingSlot(
                                slot_id=slot_id,
                                status=SlotStatus.OCCUPIED,
                                vehicle_type=row['VehicleType'],
                                vehicle_number=row['VehicleNumber'],
                                arrival_time=arrival_dt,
                                pickup_time=pickup_dt
                            )
                            
                        except (ValueError, TypeError) as e:
                            print(f"Warning: Could not parse datetime for slot {slot_num}: {e}")
                            continue
                
                print(f"Loaded {len(self.parking_manager.get_occupied_slots())} occupied slots from CSV")
            else:
                print(f"CSV file {self.csv_filename} not found. Starting with empty parking lot.")
                self._initialize_empty_csv()
                
        except Exception as e:
            print(f"Error loading CSV data: {e}")
            self._initialize_empty_csv()
    
    def _initialize_empty_csv(self):
        """Initialize empty CSV file with 20 slots"""
        data = []
        for i in range(1, 21):
            data.append({
                'Slot': i,
                'VehicleType': '',
                'VehicleNumber': '',
                'ArrivalDate': '',
                'ArrivalTime': '',
                'ExpectedPickupDate': '',
                'ExpectedPickupTime': '',
                'Weekday': '',
                'Charge': ''
            })
        
        df = pd.DataFrame(data)
        df.to_csv(self.csv_filename, index=False)
        print(f"Initialized empty CSV file: {self.csv_filename}")
    
    def save_to_csv(self):
        """Save current parking data to CSV file"""
        try:
            data = []
            
            for i in range(1, 21):  # 20 slots
                slot_id = f"slot_{i}"
                slot_data = self.parking_manager.get_slot_data(slot_id)
                
                if slot_data and slot_data.status == SlotStatus.OCCUPIED:
                    # Format dates in dd-mm-yy format
                    arrival_date = slot_data.arrival_time.strftime("%d-%m-%y")
                    arrival_time = slot_data.arrival_time.strftime("%H:%M")
                    pickup_date = slot_data.pickup_time.strftime("%d-%m-%y")
                    pickup_time = slot_data.pickup_time.strftime("%H:%M")
                    weekday = slot_data.arrival_time.strftime("%a")
                    
                    data.append({
                        'Slot': i,
                        'VehicleType': slot_data.vehicle_type,
                        'VehicleNumber': slot_data.vehicle_number,
                        'ArrivalDate': arrival_date,
                        'ArrivalTime': arrival_time,
                        'ExpectedPickupDate': pickup_date,
                        'ExpectedPickupTime': pickup_time,
                        'Weekday': weekday,
                        'Charge': 0.0  # Will be calculated on removal
                    })
                else:
                    # Empty slot
                    data.append({
                        'Slot': i,
                        'VehicleType': '',
                        'VehicleNumber': '',
                        'ArrivalDate': '',
                        'ArrivalTime': '',
                        'ExpectedPickupDate': '',
                        'ExpectedPickupTime': '',
                        'Weekday': '',
                        'Charge': ''
                    })
            
            df = pd.DataFrame(data)
            df.to_csv(self.csv_filename, index=False)
            print(f"Parking data saved to {self.csv_filename}")
            
        except Exception as e:
            print(f"Error saving to CSV: {e}")
    
    def park_vehicle(self, vehicle_type: str, vehicle_number: str, 
                    arrival_dt: datetime, pickup_dt: datetime) -> tuple[bool, str]:
        """Park a vehicle and save to CSV"""
        success, slot_id = self.parking_manager.park_vehicle(
            vehicle_type, vehicle_number, arrival_dt, pickup_dt
        )
        
        if success:
            self.save_to_csv()
        
        return success, slot_id
    
    def remove_vehicle(self, slot_id: str, departure_dt: datetime) -> Optional[Dict]:
        """Remove a vehicle, calculate charges, and save to CSV"""
        bill_info = self.parking_manager.remove_vehicle(slot_id, departure_dt)
        
        if bill_info:
            # Update CSV with final charge before saving
            self._update_slot_charge_in_csv(slot_id, bill_info['total_cost'])
            self.save_to_csv()
        
        return bill_info
    
    def _update_slot_charge_in_csv(self, slot_id: str, charge: float):
        """Update the charge for a specific slot in the CSV data"""
        try:
            if os.path.exists(self.csv_filename):
                df = pd.read_csv(self.csv_filename)
                slot_num = int(slot_id.split('_')[1])
                slot_index = slot_num - 1  # Convert to 0-based index
                
                if 0 <= slot_index < len(df):
                    df.at[slot_index, 'Charge'] = charge
                    df.to_csv(self.csv_filename, index=False)
        except Exception as e:
            print(f"Error updating charge in CSV: {e}")
    
    def get_parking_manager(self) -> ParkingManager:
        """Get the underlying ParkingManager instance"""
        return self.parking_manager
    
    def get_csv_data(self) -> pd.DataFrame:
        """Get current CSV data as DataFrame"""
        try:
            return pd.read_csv(self.csv_filename)
        except Exception as e:
            print(f"Error reading CSV data: {e}")
            return pd.DataFrame()
    
    def export_csv_data(self, filename: str = None) -> str:
        """Export current parking data to a CSV file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"parking_export_{timestamp}.csv"
        
        try:
            self.save_to_csv()  # Ensure latest data is saved
            df = self.get_csv_data()
            df.to_csv(filename, index=False)
            return filename
        except Exception as e:
            print(f"Error exporting CSV data: {e}")
            return ""

# Global instance
csv_data_manager = CSVDataManager()
