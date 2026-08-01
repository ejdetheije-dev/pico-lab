"""Test DHT11 op GPIO 16 — meet 5x temperatuur en luchtvochtigheid."""

import time
import dht
from machine import Pin

sensor = dht.DHT11(Pin(16, Pin.IN, Pin.PULL_UP))

for i in range(20):
    time.sleep(2)
    try:
        sensor.measure()
        print(f"{i+1}: {sensor.temperature()}C  {sensor.humidity()}%")
    except Exception:
        print(f"{i+1}: overgeslagen")

print("klaar")
