"""GPIO scan — zoekt op welke pin de DHT11 reageert."""

import time
import dht
from machine import Pin

PINS = list(range(0, 23)) + [26, 27, 28]

for gpio in PINS:
    print(f"GPIO {gpio}...", end=" ")
    try:
        sensor = dht.DHT11(Pin(gpio, Pin.IN, Pin.PULL_UP))
        time.sleep_ms(1000)
        sensor.measure()
        print(f"OK: {sensor.temperature()}C  {sensor.humidity()}%")
    except OSError:
        print("geen reactie")
    except Exception as e:
        print(f"fout: {e}")

print("klaar")
