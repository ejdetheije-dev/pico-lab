"""Test GPIO 9 output — 3s HIGH, 3s LOW, herhaal 3x."""

import time
from machine import Pin

pin = Pin(9, Pin.OUT)

for i in range(3):
    pin.high()
    print(f"HIGH — meet nu spanning op L9 vs GND")
    time.sleep(3)
    pin.low()
    print("LOW")
    time.sleep(1)

print("klaar")
