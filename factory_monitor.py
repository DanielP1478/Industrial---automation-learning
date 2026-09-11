import time
import random
from datetime import datetime

DOWNTIME_COST_PER_MINUTE = 500.00

def run_factory_shift():
    total_cycles = 3
    successful_cycles = 0
    total_revenue_loss = 0.0

    print("=========================================")
    print(" LAUNCHING LIVE INDUSTRIAL MONITORING SPRINT ")
    print("=========================================\n")

    for i in range(total_cycles):
        machine_id = "CNC_Assembly_Robot_1"
        temperature = random.randint(50, 110)
        voltage = random.uniform(220.0, 245.0)

        print(f"[{i+1}/{total_cycles}] Querying Sensor Array: {machine_id}")
        print(f" Voltage: {voltage:.2f}V | Temperature: {temperature}°C")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = ""

        if temperature > 100:
            minutes_offline = 15
            financial_loss = minutes_offline * DOWNTIME_COST_PER_MINUTE
            total_revenue_loss += financial_loss
            log_message = f"[{timestamp}] CRITICAL: {machine_id} Overheating ({temperature}°C). Loss: £{financial_loss:,.2f}\n"
            print(f" ⚠️ ALERT: Overheating! Loss: £{financial_loss:,.2f}")

        elif voltage < 225.0:
            minutes_offline = 5
            financial_loss = minutes_offline * DOWNTIME_COST_PER_MINUTE
            total_revenue_loss += financial_loss
            log_message = f"[{timestamp}] WARNING: {machine_id} Voltage Drop ({voltage:.2f}V). Loss: £{financial_loss:,.2f}\n"
            print(f" ⚠️ ALERT: Voltage Drop! Loss: £{financial_loss:,.2f}")

        else:
            successful_cycles += 1
            print(" Status: Nominal. Output optimal.")

        if log_message:
            with open("machine_errors.log", "a") as log_file:
                log_file.write(log_message)

        print("-" * 50)
        time.sleep(1)

run_factory_shift()
