from machine import Pin
import time

p = Pin(20, Pin.OUT)

p.high()
print("Set HIGH, reads:", p.value())
time.sleep(1)

p.low()
print("Set LOW, reads:", p.value())
time.sleep(1)
