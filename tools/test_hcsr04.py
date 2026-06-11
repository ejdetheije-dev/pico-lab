"""Test HC-SR04 ultrasone sensor op GPIO 17 (trigger) en GPIO 18 (echo)."""

import time
from machine import Pin

trig = Pin(17, Pin.OUT)
echo = Pin(18, Pin.IN)

def meet():
    trig.low()
    time.sleep_us(2)
    trig.high()
    time.sleep_us(10)
    trig.low()

    timeout = time.ticks_add(time.ticks_us(), 30000)
    while echo.value() == 0:
        if time.ticks_diff(timeout, time.ticks_us()) <= 0:
            return None
        start = time.ticks_us()

    timeout = time.ticks_add(time.ticks_us(), 30000)
    while echo.value() == 1:
        if time.ticks_diff(timeout, time.ticks_us()) <= 0:
            return None
        end = time.ticks_us()

    return (time.ticks_diff(end, start) * 0.0343) / 2

print("Afstand (cm):")
while True:
    afstand = meet()
    print(afstand)
    time.sleep_ms(500)
