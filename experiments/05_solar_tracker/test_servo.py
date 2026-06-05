from machine import Pin, PWM
import time

pwm = PWM(Pin(8), freq=50)

def zet(hoek):
    pwm.duty_u16(int((500 + hoek / 180 * 2000) * 65535 / 20000))

while True:
    for h in range(0, 181, 5):
        zet(h)
        time.sleep_ms(50)
    for h in range(180, -1, -5):
        zet(h)
        time.sleep_ms(50)
