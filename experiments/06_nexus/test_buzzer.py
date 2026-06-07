from machine import Pin, PWM
import time

# Test 1: actieve buzzer (gewoon HIGH)
pin = Pin(9, Pin.OUT)
print("Test 1: actief (HIGH)")
pin.value(1)
time.sleep(1)
pin.value(0)
time.sleep(0.5)

# Test 2: passieve buzzer laag (200Hz)
print("Test 2: PWM 200Hz")
buzzer = PWM(Pin(9))
buzzer.freq(200)
buzzer.duty_u16(32768)
time.sleep(1)
buzzer.duty_u16(0)
time.sleep(0.5)

# Test 3: passieve buzzer hoog (2000Hz)
print("Test 3: PWM 2000Hz")
buzzer.freq(2000)
buzzer.duty_u16(32768)
time.sleep(1)
buzzer.duty_u16(0)

print("Klaar - welke test hoorde je?")
