"""Test passieve buzzer op GPIO 9 (PWM)."""

import time
from machine import Pin, PWM

buzzer = PWM(Pin(9))

for freq in [440, 880, 1320, 880, 440]:
    buzzer.freq(freq)
    buzzer.duty_u16(32768)
    time.sleep_ms(300)

buzzer.duty_u16(0)
buzzer.deinit()
print("klaar")
