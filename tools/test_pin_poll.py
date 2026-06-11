"""Test of GPIO 21 GND detecteert via polling."""

import time
from machine import Pin

pin = Pin(21, Pin.IN, Pin.PULL_UP)
print("Raak GPIO 21 aan GND. Wacht op LOW...")

while True:
    if pin.value() == 0:
        print("LOW gedetecteerd!")
    time.sleep_ms(10)
