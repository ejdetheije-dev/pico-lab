"""Test LDR (GPIO 26) en KY-038 geluidssensor (AO=GPIO 28, DO=GPIO 19).

Upload en run:
    mpremote cp tools/test_sensors_ldr_sound.py :test_sensors_ldr_sound.py
    mpremote run test_sensors_ldr_sound.py
"""

import time
from machine import ADC, Pin

ldr = ADC(Pin(26))
sound_ao = ADC(Pin(27))
sound_do = Pin(19, Pin.IN)

print("LDR raw | Geluid raw | Geluid DO")
print("-" * 36)

while True:
    ldr_raw = ldr.read_u16()
    sound_raw = sound_ao.read_u16()
    sound_digital = sound_do.value()
    print(f"{ldr_raw:6d}  | {sound_raw:10d} | {sound_digital}")
    time.sleep_ms(20)
