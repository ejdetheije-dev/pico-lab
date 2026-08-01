"""ADC scan — lees GPIO 26/27/28 om de LDR-pin te vinden. Dek LDR af met vinger."""

import time
from machine import ADC, Pin

pins = {26: ADC(Pin(26)), 27: ADC(Pin(27)), 28: ADC(Pin(28))}

for _ in range(10):
    vals = {gpio: adc.read_u16() for gpio, adc in pins.items()}
    print(f"26={vals[26]:5d}  27={vals[27]:5d}  28={vals[28]:5d}")
    time.sleep(1)
