import time
import random
from datetime import datetime

#Local Industry Downtime Metric: What a factory loss costs per minute
DOWNTIME_COST_PER_MINUTE = 500.00 

def check_machine_status(machine_id):
    temperature = random.randint(50, 110)
    voltage = random.uniform(220.0, 245.0)

    print(f"--- Monitoring: {machine_id} ---")
    print(f"Voltage Reading: {voltage:.2f}V")
    print(f"Core Heat Level: {temperature}°C")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = ""

    if temperature > 100:
        minutes_offline = 15
        financial_loss = minutes_offline * DOWNTIME_COST_PER_MINUTE
        log_message = f"[{timestamp}] CRITICAL: {machine_id} Overheating ({temperature}°C). System Offline for {minutes_offline}m. Estimated Revenue Loss: £{financial_loss:,.2f}\n"
        print(f"ALERT: Overheating! Estimated Loss: £{financial_loss:,.2f}")

    elif voltage < 225.0:
        minutes_offline = 5
        financial_loss = minutes_offline * DOWNTIME_COST_PER_MINUTE
        log_message = f"[{timestamp}] WARNING: {machine_id} Voltage Drop ({voltage:.2f}V). Reboot Cycle: {minutes_offline}m. Estimated Revenue Loss: £{financial_loss:,.2f}\n"
        print(f"ALERT: Voltage drop! Estimated Loss: £{financial_loss:,.2f}")

    else:
        print("System Status: Nominal. Revenue output optimal.")

    if log_message:
        with open("machine_errors.log", "a") as log_file:
            log_file.write(log_message)

    return "-" * 40

for i in range(3):
    status_report = check_machine_status("CNC_Assembly_Robot_1")
    print(status_report)
    time.sleep(1)
