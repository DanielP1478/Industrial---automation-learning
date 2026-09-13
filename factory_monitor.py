import time
import random
import os
from datetime import datetime

DOWNTIME_COST_PER_MINUTE = 500.00

system_thresholds = {
    "max_temp": 100,
    "min_voltage": 225.0
}

shift_metrics = {
    "highest_temp": None, "lowest_temp": None,
    "highest_volt": None, "lowest_volt": None,
    "total_scans": 0
}

def update_shift_analytics(temp, volt):
    shift_metrics["total_scans"] += 1
    if shift_metrics["highest_temp"] is None or temp > shift_metrics["highest_temp"]:
        shift_metrics["highest_temp"] = temp
    if shift_metrics["lowest_temp"] is None or temp < shift_metrics["lowest_temp"]:
        shift_metrics["lowest_temp"] = temp
    if shift_metrics["highest_volt"] is None or volt > shift_metrics["highest_volt"]:
        shift_metrics["highest_volt"] = volt
    if shift_metrics["lowest_volt"] is None or volt < shift_metrics["lowest_volt"]:
        shift_metrics["lowest_volt"] = volt

def check_sensors_once():
    machine_id = "CNC_Assembly_Robot_1"
    temperature = random.randint(50, 110)
    voltage = random.uniform(220.0, 245.0)

    update_shift_analytics(temperature, voltage)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_code = "[OK-200]"  # Default industry nominal state code
    log_message = ""

    if temperature > system_thresholds["max_temp"]:
        status_code = "[ERR-500]"  # Critical Hardware Thermal Fault Code
        loss = 15 * DOWNTIME_COST_PER_MINUTE
        log_message = f"[{timestamp}] {status_code} CRITICAL: Overheating ({temperature}°C). Loss: £{loss:,.2f}\n"
        print(f" ⚠️ ALERT {status_code}: High Thermal Limit Exceeded! Loss: £{loss:,.2f}")
    elif voltage < system_thresholds["min_voltage"]:
        status_code = "[WARN-404]"  # Line Voltage Drop Warning Code
        loss = 5 * DOWNTIME_COST_PER_MINUTE
        log_message = f"[{timestamp}] {status_code} WARNING: Voltage Drop ({voltage:.2f}V). Loss: £{loss:,.2f}\n"
        print(f" ⚠️ ALERT {status_code}: Low Line Voltage Instability! Loss: £{loss:,.2f}")
    else:
        # ❤️ Silent system heartbeat signal confirmation text
        print(f" STATUS: {status_code} - Sensor Node Active. Status: Nominal.")


        if log_message:
             with open("machine_errors.log", "a") as log_file:
                    log_file.write(log_message)

# Always log the operational heartbeat data block for external database audits
        with open("heartbeat.log", "a") as hb_file:
            hb_file.write(f"[{timestamp}] NODE_OK | CODE: {status_code} | T: {temperature}°C | V: {voltage:.2f}V\n")

def run_autonomous_loop():
    print("\n==========================================")
    print("   LAUNCHING AUTONOMOUS MONITORING MODE   ")
    print("   [Press Ctrl + C to exit back to menu]  ")
    print("==========================================\n")
    time.sleep(1)
    try:
        while True:
            check_sensors_once()
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[INFO] Autonomous mode suspended by operator.")

def display_shift_analytics():
    print("\n==========================================")
    print("      FACTORY SHIFT ANALYTICS REPORT      ")
    print("==========================================")
    print(f" Total Active Sensor Queries Executed: {shift_metrics['total_scans']}")
    print("------------------------------------------")
    if shift_metrics["total_scans"] > 0:
        print(f" Temperature -> Max High: {shift_metrics['highest_temp']}°C | Min Low: {shift_metrics['lowest_temp']}°C")
        print(f" Line Voltage -> Max High: {shift_metrics['highest_volt']:.2f}V | Min Low: {shift_metrics['lowest_volt']:.2f}V")
    else:
        print(" No metrics accumulated yet.")
    print("==========================================\n")

def display_historical_logs():
    print("\n--- RETRIEVING HISTORICAL FAULT LOGS ---")
    if os.path.exists("machine_errors.log"):
        with open("machine_errors.log", "r") as log_file:
            for record in log_file.readlines()[-10:]:
                print(record.strip())
    else:
        print("No machine_errors.log file found on disk.")
    print("----------------------------------------\n")

def update_threshold_limits():
    print("\n--- CONFIGURE SAFETY BOUNDARIES ---")
    try:
        new_temp = input("Enter new Max Temp limit (or hit ENTER to skip): ")
        if new_temp.strip(): system_thresholds["max_temp"] = int(new_temp)
        new_volt = input("Enter new Min Volt limit (or hit ENTER to skip): ")
        if new_volt.strip(): system_thresholds["min_voltage"] = float(new_volt)
        print(" ✅ Safety boundaries updated successfully.")
    except ValueError:
        print("\n❌ INPUT ERROR: Invalid format. Override aborted.")

def launch_control_panel():
    while True:
        print("\n=== SCADA MASTER CONTROL PANEL ===")
        print(" 1. Manual Single Telemetry Check")
        print(" 2. Launch Continuous Autonomous Mode")
        print(" 3. Print Shift Performance Analytics")
        print(" 4. Print Saved Historical Fault Logs")
        print(" 5. Adjust Safety Threshold Parameters")
        print(" 6. Safe System Shutdown & Exit")
        print("==================================")

        user_choice = input("Enter option (1-6): ")

        if user_choice == "1":
            check_sensors_once()
            input("Press ENTER to return to menu...")
        elif user_choice == "2":
            run_autonomous_loop()
            input("Press ENTER to return to menu...")
        elif user_choice == "3":
            display_shift_analytics()
            input("Press ENTER to return to menu...")
        elif user_choice == "4":
            display_historical_logs()
            input("Press ENTER to return to menu...")
        elif user_choice == "5":
            update_threshold_limits()
            input("Press ENTER to return to menu...")
        elif user_choice == "6":
            print("\nShutting down SCADA network tracking... Goodbye.")
            break
        else:
            print("\n❌ INVALID CHOICE. Input 1-6.")
            time.sleep(1)

if __name__ == "__main__":
    launch_control_panel()