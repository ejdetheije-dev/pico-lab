from machine import Pin
import time

trig = Pin(17, Pin.OUT)
echo = Pin(18, Pin.IN)

while True:
    trig.low()
    time.sleep_us(2)
    trig.high()
    time.sleep_us(10)
    trig.low()

    while echo.value() == 0:
        start = time.ticks_us()
    while echo.value() == 1:
        end = time.ticks_us()

    afstand = (time.ticks_diff(end, start) * 0.0343) / 2
    print("Afstand:", round(afstand, 1), "cm")
    time.sleep(1)
