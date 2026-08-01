"""Buzzer langdurig test — 5s aaneengesloten toon op GPIO 9."""

import time
from machine import Pin, PWM

buzzer = PWM(Pin(9))
buzzer.freq(440)
buzzer.duty_u16(32768)
print("toon aan — 5 seconden")
time.sleep(5)
buzzer.duty_u16(0)
buzzer.deinit()
print("klaar")
