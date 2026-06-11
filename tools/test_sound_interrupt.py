"""Test KY-038 DO pin via interrupt op GPIO 19.

Klap hard en kijk of de teller oploopt.
"""

import time
from machine import Pin

triggered = bytearray(1)

def geluid(pin):
    triggered[0] = 1

do = Pin(19, Pin.IN, Pin.PULL_UP)
do.irq(trigger=Pin.IRQ_FALLING, handler=geluid)

print("Raak GPIO 21 aan GND of klap naast microfoon:")
while True:
    if triggered[0]:
        print("Getriggerd!")
        triggered[0] = 0
    time.sleep_ms(20)
