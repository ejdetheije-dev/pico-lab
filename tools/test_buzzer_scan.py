"""GPIO scan — speelt toon op elk GPIO om de buzzer te vinden."""

import time
from machine import Pin, PWM

PINS = list(range(0, 23)) + [26, 27, 28]

for gpio in PINS:
    print(f"GPIO {gpio}")
    try:
        p = PWM(Pin(gpio))
        p.freq(880)
        p.duty_u16(32768)
        time.sleep_ms(500)
        p.duty_u16(0)
        p.deinit()
    except Exception as e:
        print(f"  fout: {e}")
    time.sleep_ms(150)

print("klaar")
