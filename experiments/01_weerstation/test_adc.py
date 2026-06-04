"""Minimale ADC-test op GPIO 26."""

import time
from machine import ADC, Pin

adc = ADC(Pin(26))

while True:
    raw = adc.read_u16()
    pct = round(raw / 655)
    print("raw={} pct={}%".format(raw, pct))
    time.sleep(1)
