"""Servo-wijzer — DHT11 temperatuur stuurt servo positie.

Mapping: 0 °C -> 0°, 40 °C -> 180°. Wordt geclipt buiten dit bereik.
Soepel verloop: stapsgewijs naar nieuwe positie om jitter te vermijden.
"""

import time
import dht
from machine import Pin, PWM


DHT_PIN = 16
SERVO_PIN = 7
TEMP_MIN_C = 0
TEMP_MAX_C = 40
INTERVAL_S = 2


class Servo:
    """SG90 micro servo via PWM (50 Hz, pulsbreedte 500–2500 us)."""

    def __init__(self, pin, freq=50):
        self.pwm = PWM(Pin(pin), freq=freq)
        self._huidige_hoek = None

    def _hoek_naar_duty(self, hoek):
        us = 500 + (hoek / 180) * 2000
        return int(us * 65535 / 20000)

    def zet_hoek(self, hoek):
        """Zet de servo direct op een hoek (0..180)."""
        hoek = max(0, min(180, hoek))
        self.pwm.duty_u16(self._hoek_naar_duty(hoek))
        self._huidige_hoek = hoek

    def soepel_naar(self, hoek, stap=2, vertraging_ms=15):
        """Beweeg stapsgewijs naar de doelhoek."""
        hoek = max(0, min(180, hoek))
        if self._huidige_hoek is None:
            self.zet_hoek(hoek)
            return
        richting = 1 if hoek > self._huidige_hoek else -1
        h = self._huidige_hoek
        while abs(h - hoek) >= stap:
            h += richting * stap
            self.zet_hoek(h)
            time.sleep_ms(vertraging_ms)
        self.zet_hoek(hoek)


def temp_naar_hoek(temp_c):
    """Lineaire mapping van temperatuur naar 0..180 graden."""
    if temp_c <= TEMP_MIN_C:
        return 0
    if temp_c >= TEMP_MAX_C:
        return 180
    return (temp_c - TEMP_MIN_C) * 180 / (TEMP_MAX_C - TEMP_MIN_C)


def main():
    sensor = dht.DHT11(Pin(DHT_PIN))
    servo = Servo(SERVO_PIN)

    print("Servo-wijzer gestart.")
    while True:
        sensor.measure()
        t = sensor.temperature()
        hoek = temp_naar_hoek(t)
        servo.soepel_naar(hoek)
        print("temp={}C -> hoek={:.0f} graden".format(t, hoek))
        time.sleep(INTERVAL_S)


main()
