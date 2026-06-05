"""Solar tracker — twee LDR's, servo draait naar de lichtste kant.

Beide LDR's worden via ADC uitgelezen. Bij een groter verschil dan de
drempel beweegt de servo één stap naar de lichtste kant. Onder de drempel
blijft hij staan (hysterese voorkomt jitter).
"""

import time
from machine import Pin, PWM, ADC


LDR_LINKS_PIN = 28
LDR_RECHTS_PIN = 26  # gedeeld met weerstation (experiment 01)
SERVO_PIN = 8
DREMPEL = 300
STAP_GRADEN = 2
INTERVAL_MS = 80
HOEK_MIN = 10
HOEK_MAX = 170
START_HOEK = 90


class Servo:
    """Eenvoudige SG90-servo via PWM."""

    def __init__(self, pin, freq=50):
        self.pwm = PWM(Pin(pin), freq=freq)
        self.hoek = None

    def _duty(self, hoek):
        us = 500 + (hoek / 180) * 2000
        return int(us * 65535 / 20000)

    def zet(self, hoek):
        hoek = max(0, min(180, hoek))
        self.pwm.duty_u16(self._duty(hoek))
        self.hoek = hoek


def lees_gemiddeld(adc, aantal=8):
    """Gemiddelde over N samples om ruis te dempen."""
    return sum(adc.read_u16() for _ in range(aantal)) // aantal


def kalibreer(ldr_l, ldr_r, n=20):
    """Meet het nulpuntverschil tussen beide LDR's bij gelijke belichting."""
    offset = sum(lees_gemiddeld(ldr_l) - lees_gemiddeld(ldr_r) for _ in range(n)) // n
    print("Kalibratie klaar. Offset:", offset)
    return offset


def main():
    ldr_l = ADC(Pin(LDR_LINKS_PIN))
    ldr_r = ADC(Pin(LDR_RECHTS_PIN))
    servo = Servo(SERVO_PIN)
    servo.zet(START_HOEK)
    time.sleep_ms(400)

    print("Kalibreren... zorg voor gelijke belichting op beide LDR's")
    offset = kalibreer(ldr_l, ldr_r)

    print("Solar tracker gestart. Drempel:", DREMPEL)
    while True:
        links = lees_gemiddeld(ldr_l)
        rechts = lees_gemiddeld(ldr_r)
        verschil = (links - rechts) - offset

        if abs(verschil) > DREMPEL:
            doel = servo.hoek + (STAP_GRADEN if verschil > 0 else -STAP_GRADEN)
            doel = max(HOEK_MIN, min(HOEK_MAX, doel))
            servo.zet(doel)
            actie = "links" if verschil > 0 else "rechts"
        else:
            actie = "stil"

        print(
            "L={} R={} delta={} hoek={} -> {}".format(
                links, rechts, verschil, servo.hoek, actie
            )
        )
        time.sleep_ms(INTERVAL_MS)


main()
