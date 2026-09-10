import time
import random
from datetime import datetime

def check_machine_status(machine_id):
    temperature = random.randint(50, 110)
    voltage = random.uniform(220.0, 245.0)

    print(f"--- Monitoring: {machine_id} ---")
    print(f"Voltage Reading: {voltage:.2f}V")
    print(f"Core Heat Level: {temperature}°C")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = ""

    if temperature > 100:
        log_message = f"[{timestamp}] CRITICAL: {machine_id} Overheating at {temperature}°C!\n"
        print("ALERT: Overheating!")
    elif voltage < 225.0:
        log_message = f"[{timestamp}] WARNING: {machine_id} Voltage Drop detected ({voltage:.2f}V).\n"
        print("ALERT: Voltage drop detected.")
    else:
        print("System Status: Nominal.")

    if log_message:
        with open("machine_errors.log", "a") as log_file:
            log_file.write(log_message)

    return "-" * 40

for i in range(3):
    status_report = check_machine_status("CNC_Assembly_Robot_1")
    print(status_report)
    time.sleep(1)
