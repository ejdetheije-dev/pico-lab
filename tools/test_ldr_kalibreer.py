"""LDR kalibratie op GPIO 26 — meet continu, noteer waarden bij vinger/schaduw/lamp."""

import time
from machine import ADC, Pin

ldr = ADC(Pin(26))

print("LDR kalibratie - GPIO 26")
print("Dek af met vinger voor min, lamp erbij voor max")
print("Ctrl-C om te stoppen")
print()

while True:
    raw = ldr.read_u16()
    print(f"raw={raw:5d}")
    time.sleep_ms(500)
