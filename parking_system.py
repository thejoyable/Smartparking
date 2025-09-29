from datetime import datetime, timedelta
import pandas as pd
import os

class ParkingSystem:
    def __init__(self, filename):
        self.filename = filename
        self.holidays = pd.read_csv("West_Bengal_Holidays_2025.csv")
        self.holidays['Date'] = pd.to_datetime(self.holidays['Date'], format='%d-%m-%Y')
        
        expected_columns = [
            "Slot", "VehicleType", "VehicleNumber", "ArrivalDate", 
            "ArrivalTime", "ExpectedPickupDate", "ExpectedPickupTime", 
            "Weekday", "Charge"
        ]
        
        try:
            self.df = pd.read_csv(filename)
            self.df = self.df.reindex(columns=expected_columns)
        except FileNotFoundError:
            self.df = pd.DataFrame(columns=expected_columns)
            # Initialize with 20 slots
            for i in range(1, 21):
                self.df.loc[i-1] = [i, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, 0.0]
        self.df.to_csv(filename, index=False)

    def park_vehicle(self):
        print("\nEnter vehicle details:")
        vehicle_type = input("Enter vehicle type (1 for Car, 2 for Bike, 3 for Truck or Car/Bike/Truck):  ").strip()
        vehicle_type = {"1": "Car", "2": "Bike", "3": "Truck"}.get(vehicle_type, vehicle_type)
        
        vehicle_number = input("Enter vehicle number:  ").strip().upper()
        arrival_date = input("Enter arrival date (dd-mm-yy):  ").strip()
        arrival_time = input("Enter arrival time (HH:MM):  ").strip()
        expected_pickup_date = input("Enter expected pickup date (dd-mm-yy):  ").strip()
        expected_pickup_time = input("Enter expected pickup time (HH:MM):  ").strip()

        arrival_datetime = datetime.strptime(f"{arrival_date} {arrival_time}", "%d-%m-%y %H:%M")
        weekday = arrival_datetime.strftime("%a")

        empty_slots = self.df[self.df["VehicleType"].isna()]
        if empty_slots.empty:
            print("No available slots!")
            return
        
        slot_index = empty_slots['Slot'].idxmax() if vehicle_type == "Truck" else empty_slots['Slot'].idxmin()

        self.df.loc[slot_index] = [
            slot_index + 1, vehicle_type, vehicle_number, arrival_date, arrival_time,
            expected_pickup_date, expected_pickup_time, weekday, 0.0
        ]
        self.df.to_csv(self.filename, index=False)
        print(f"Vehicle parked at slot {slot_index + 1}")

    def remove_vehicle(self):
        slot = int(input("Enter slot number to remove vehicle from:  ")) - 1
        if slot < 0 or slot >= len(self.df):
            print("Invalid slot number!")
            return
            
        if pd.notna(self.df.loc[slot, "VehicleType"]):
            arrival_str = f"{self.df.loc[slot, 'ArrivalDate']} {self.df.loc[slot, 'ArrivalTime']}"
            arrival = datetime.strptime(arrival_str, "%d-%m-%y %H:%M")
            
            current_date = input("Enter current date (dd-mm-yy):  ").strip()
            current_time = input("Enter current time (HH:MM):  ").strip()
            current = datetime.strptime(f"{current_date} {current_time}", "%d-%m-%y %H:%M")
            
            vehicle_type = self.df.loc[slot, "VehicleType"]
            charge_info = self.calculate_charge(arrival, current, vehicle_type)
            
            print("\n========== BILL ==========")
            print(f"Vehicle Type: {vehicle_type}")
            print(f"Vehicle Number: {self.df.loc[slot, 'VehicleNumber']}")
            print(f"Arrival: {arrival_str}")
            print(f"Departure: {current.strftime('%d-%m-%y %H:%M')}")
            print(f"Total Hours: {charge_info['hours_parked']:.1f}")
            print("--------------------------")
            print(f"Standard Hours ({charge_info['standard_hours']} hrs): Rs.{charge_info['standard_charge']:.2f}")
            if charge_info['rush_hours'] > 0:
                print(f"Rush Hours ({charge_info['rush_hours']} hrs): Rs.{charge_info['rush_charge']:.2f}")
            print(f"Night Hours ({charge_info['night_hours']} hrs): Rs.{charge_info['night_charge']:.2f}")
            print("--------------------------")
            print(f"TOTAL CHARGE: Rs.{charge_info['total']:.2f}")
            print("==========================\n")
            
            self.df.loc[slot, "Charge"] = charge_info['total']
            self.df.loc[slot] = [slot + 1] + [pd.NA]*(len(self.df.columns)-1)
            self.df.to_csv(self.filename, index=False)
        else:
            print("Slot is already empty!")

    def calculate_charge(self, arrival, current, vehicle_type):
        standard_rate = {"Car": 200, "Bike": 150, "Truck": 300}
        rush_extra = {"Car": 50, "Bike": 30, "Truck": 70}
        night_rate = 100

        delta = current - arrival
        total_seconds = delta.total_seconds()
        full_hours = int(total_seconds // 3600)
        partial_hour = total_seconds % 3600 > 0

        standard_hours = rush_hours = night_hours = 0

        for hour in range(full_hours):
            current_time = arrival + timedelta(hours=hour)
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

            # Updated night hours condition (11 PM to 5 AM)
            if current_hour >= 23 or current_hour < 5:
                night_hours += 1
            else:
                standard_hours += 1

        standard_charge = standard_hours * standard_rate[vehicle_type]
        rush_charge = rush_hours * (standard_rate[vehicle_type] + rush_extra[vehicle_type])
        night_charge = night_hours * night_rate
        total = standard_charge + rush_charge + night_charge

        return {
            "total": total,
            "standard_hours": standard_hours,
            "rush_hours": rush_hours,
            "night_hours": night_hours,
            "standard_charge": standard_charge,
            "rush_charge": rush_charge,
            "night_charge": night_charge,
            "hours_parked": full_hours + (0.5 if partial_hour else 0)
        }

    def view_status(self):
        print("\nParking Status:")
        print(self.df.fillna("").to_string(index=False))

    def run(self):
        print("Smart Parking System")
        print("Charges Information:")
        print("Standard Charges per Hour: Car: Rs.200, Bike: Rs.150, Truck: Rs.300")
        print("Rush Hour Charges (Fridays 5PM-midnight, Weekends 11AM-midnight, and holidays as per schedule):")
        print("  Car: Extra Rs.50 per hour, Bike: Extra Rs.30 per hour, Truck: Extra Rs.70 per hour")
        print("Night Charge (11 PM to 5 AM): Rs.100 per hour for all vehicles\n")
        
        while True:
            print("1. Park Vehicle")
            print("2. Remove Vehicle")
            print("3. View Status")
            print("4. Exit")
            choice = input("Enter choice: ").strip()

            if choice == "1":
                self.park_vehicle()
            elif choice == "2":
                self.remove_vehicle()
            elif choice == "3":
                self.view_status()
            elif choice == "4":
                print("Exiting...")
                break
            else:
                print("Invalid choice!")

# Create instance and run if executed directly
if __name__ == "__main__":
    parking_system = ParkingSystem("parking_data.csv")
    parking_system.run()
