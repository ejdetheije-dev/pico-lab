from machine import ADC
import time

ldr = ADC(26)

while True:
    raw = ldr.read_u16()
    print("Raw:", raw)
    time.sleep(1)
