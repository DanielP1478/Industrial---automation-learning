import time
import random
import os
from datetime import datetime

DOWNTIME_COST_PER_MINUTE = 500.00

# Dynamic threshold tracking parameters
system_thresholds = {
    "max_temp": 100,
    "min_voltage": 225.0
}

def check_sensors_once():
    """Runs a single live query check and returns true if an error logged"""
    machine_id = "CNC_Assembly_Robot_1"
    temperature = random.randint(50, 110)
    voltage = random.uniform(220.0, 245.0)

    print(f"\n[TELEMETRY SCAN] Asset: {machine_id}")
    print(f" Voltage: {voltage:.2f}V | Temperature: {temperature}°C")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = ""

    if temperature > system_thresholds["max_temp"]:
        loss = 15 * DOWNTIME_COST_PER_MINUTE
        log_message = f"[{timestamp}] CRITICAL: {machine_id} Overheating ({temperature}°C). Loss: £{loss:,.2f}\n"
        print(f" ⚠️ ALERT: High Thermal Threshold Exceeded! Loss: £{loss:,.2f}")
    elif voltage < system_thresholds["min_voltage"]:
        loss = 5 * DOWNTIME_COST_PER_MINUTE
        log_message = f"[{timestamp}] WARNING: {machine_id} Voltage Drop ({voltage:.2f}V). Loss: £{loss:,.2f}\n"
        print(f" ⚠️ ALERT: Low Line Voltage Stability Warning! Loss: £{loss:,.2f}")
    else:
        print(" ✅ Status: Nominal. Output optimal.")

    if log_message:
        with open("machine_errors.log", "a") as log_file:
            log_file.write(log_message)
    print("-" * 40)

def run_autonomous_loop():
    """NEW: Runs a continuous automated scan loop until the user breaks it"""
    print("\n==========================================")
    print("   LAUNCHING AUTONOMOUS MONITORING MODE   ")
    print("   [Press Ctrl + C to exit back to menu]  ")
    print("==========================================\n")
    time.sleep(1.5)

    try:
        while True:
            check_sensors_once()
            # ⏱️ Pauses the script for 2 seconds before automatically scanning again
            time.sleep(2) 
    except KeyboardInterrupt:
        print("\n[INFO] Autonomous mode suspended by operator.")

def display_historical_logs():
    print("\n--- RETRIEVING HISTORICAL FAULT LOGS ---")
    if os.path.exists("machine_errors.log"):
        with open("machine_errors.log", "r") as log_file:
            records = log_file.readlines()
            for record in records[-10:]:
                print(record.strip())
    else:
        print("No machine_errors.log file found on disk.")
    print("----------------------------------------\n")

def update_threshold_limits():
    print("\n--- CONFIGURE SAFETY BOUNDARIES ---")
    print(f" Current Max Temp: {system_thresholds['max_temp']}°C | Min Volt: {system_thresholds['min_voltage']}V\n")
    try:
        new_temp = input("Enter new Max Temp limit (or hit ENTER to skip): ")
        if new_temp.strip():
            system_thresholds["max_temp"] = int(new_temp)
            print(f" ✅ Temp limit adjusted to {system_thresholds['max_temp']}°C")

        new_volt = input("Enter new Min Volt limit (or hit ENTER to skip): ")
        if new_volt.strip():
            system_thresholds["min_voltage"] = float(new_volt)
            print(f" ✅ Voltage limit adjusted to {system_thresholds['min_voltage']}V")
    except ValueError:
        print("\n❌ INPUT ERROR: Invalid numerical format. Override aborted.")
    print("-----------------------------------\n")

def launch_control_panel():
    while True:
        print("\n=== SCADA MASTER CONTROL PANEL ===")
        print(" 1. Manual Single Telemetry Check")
        print(" 2. Launch Continuous Autonomous Mode [NEW]")
        print(" 3. Print Saved Historical Fault Logs")
        print(" 4. Adjust Safety Threshold Parameters")
        print(" 5. Safe System Shutdown & Exit")
        print("==================================")

        user_choice = input("Enter option (1-5): ")

        if user_choice == "1":
            check_sensors_once()
            input("Press ENTER to return to menu...")
        elif user_choice == "2":
            run_autonomous_loop()
            input("Press ENTER to return to menu...")
        elif user_choice == "3":
            display_historical_logs()
            input("Press ENTER to return to menu...")
        elif user_choice == "4":
            update_threshold_limits()
            input("Press ENTER to return to menu...")
        elif user_choice == "5":
            print("\nShutting down SCADA network tracking... Goodbye.")
            break
        else:
            print("\n❌ INVALID CHOICE. Input 1-5.")
            time.sleep(1)

if __name__ == "__main__":
    launch_control_panel()