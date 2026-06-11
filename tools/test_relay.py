"""Test relaismodule kanaal 1 op GPIO 21 (active LOW). Schakelt 5x aan/uit."""

import time
from machine import Pin

relay = Pin(21, Pin.OUT)  # IN2 = kanaal 2
relay.high()
time.sleep(1)

for i in range(5):
    print(f"Aan ({i+1})")
    relay.low()
    time.sleep(1)
    print(f"Uit ({i+1})")
    relay.high()
    time.sleep(1)

print("klaar")
