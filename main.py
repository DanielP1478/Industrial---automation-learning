import machine
import time
import dht

# Pin 15 is our sensor data channel
sensor_pin = machine.Pin(15)
sensor = dht.DHT22(sensor_pin)

while True:
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()

        # This exact format allows factory_monitor.py to parse the text data
        print(f"DATA:{temp},{hum}")

    except OSError:
        print("DATA:ERROR,ERROR")

    # Read data every 3 seconds
    time.sleep(3)
