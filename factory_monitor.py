import time
import random
import os
from datetime import datetime

# Global Default Setting
DOWNTIME_COST_PER_MINUTE = 500.00

def run_sensor_query():
    """Runs a single active machine sensor scan pass"""
    machine_id = "CNC_Assembly_Robot_1"
    temperature = random.randint(50, 110)
    voltage = random.uniform(220.0, 245.0)

    print("\n[LIVE MONITORING] Querying Sensor Array...")
    print(f" Asset ID: {machine_id}")
    print(f" Line Voltage: {voltage:.2f}V | Core Temp: {temperature}°C")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = ""

    # Operational status evaluation parameters
    if temperature > 100:
        minutes_offline = 15
        loss = minutes_offline * DOWNTIME_COST_PER_MINUTE
        log_message = f"[{timestamp}] CRITICAL: {machine_id} Overheating ({temperature}°C). Loss: £{loss:,.2f}\n"
        print(f" ⚠️ ALERT: High Thermal Threshold Exceeded! Loss: £{loss:,.2f}")
    elif voltage < 225.0:
        minutes_offline = 5
        loss = minutes_offline * DOWNTIME_COST_PER_MINUTE
        log_message = f"[{timestamp}] WARNING: {machine_id} Voltage Drop ({voltage:.2f}V). Loss: £{loss:,.2f}\n"
        print(f" ⚠️ ALERT: Low Line Voltage Stability Warning! Loss: £{loss:,.2f}")
    else:
        print(" ✅ Status: Nominal. Systems operating at optimal output efficiency.")

    # Write log telemetry if an issue occurs
    if log_message:
        with open("machine_errors.log", "a") as log_file:
            log_file.write(log_message)
    print("-" * 50)

def display_historical_logs():
    """Reads and displays the saved system log file directly onto the terminal screen"""
    print("\n=========================================")
    print("  RETRIEVING HISTORICAL EXCEPTION LOGS   ")
    print("=========================================")

    if os.path.exists("machine_errors.log"):
        with open("machine_errors.log", "r") as log_file:
            records = log_file.readlines()
            if records:
                # Print the last 10 errors to prevent screen cluttering
                for record in records[-10:]:
                    print(record.strip())
            else:
                print("Log file is currently empty. No system errors recorded.")
    else:
        print("No machine_errors.log file found on disk yet.")
    print("=========================================\n")

def launch_control_panel():
    """Launches the master interactive application dashboard interface"""
    while True:
        print("\n=========================================")
        print("   SCADA SIMULATION MASTER CONTROL PANEL   ")
        print("=========================================")
        print(" [1] Execute Live Machine Telemetry Pass")
        print(" [2] Print Saved Historical Fault Logs")
        print(" [3] Safe System Shutdown & Exit")
        print("=========================================")

        user_choice = input("Enter operational command choice (1-3): ")

        if user_choice == "1":
            run_sensor_query()
            input("\nPress ENTER to return to main dashboard menu...")
        elif user_choice == "2":
            display_historical_logs()
            input("Press ENTER to return to main dashboard menu...")
        elif user_choice == "3":
            print("\n=========================================")
            print(" SHUTTING DOWN SCADA MONITOR SYSTEM... ")
            print(" Disconnecting core telemetry arrays. Goodbye.")
            print("=========================================")
            break
        else:
            print("\n❌ INVALID COMMAND: Please input a valid option number (1-3).")
            time.sleep(1)

if __name__ == "__main__":
    launch_control_panel()