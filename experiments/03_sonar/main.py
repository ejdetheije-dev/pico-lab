"""Sonar — HC-SR04 afstand meten, visualiseren met RGB LED.

- < 10 cm  -> rood
- 10–30 cm -> oranje (rood + groen)
- > 30 cm  -> groen
- > 200 cm of timeout -> uit
"""

import time
from machine import Pin, PWM


TRIG_PIN = 17
ECHO_PIN = 18
LED_R_PIN = 13
LED_G_PIN = 14
LED_B_PIN = 15
INTERVAL_MS = 100


class HCSR04:
    """Ultrasone afstandsensor."""

    def __init__(self, trig_pin, echo_pin):
        self.trig = Pin(trig_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        self.trig.low()

    def afstand_cm(self, timeout_us=30000):
        """Meet één afstand. None bij timeout (geen echo)."""
        self.trig.low()
        time.sleep_us(2)
        self.trig.high()
        time.sleep_us(10)
        self.trig.low()

        start = time.ticks_us()
        while self.echo.value() == 0:
            if time.ticks_diff(time.ticks_us(), start) > timeout_us:
                return None
        t_rise = time.ticks_us()
        while self.echo.value() == 1:
            if time.ticks_diff(time.ticks_us(), t_rise) > timeout_us:
                return None
        duur = time.ticks_diff(time.ticks_us(), t_rise)
        return duur * 0.0343 / 2


class RgbLed:
    """RGB LED via 3x PWM. Waarden 0..255 per kanaal."""

    def __init__(self, r_pin, g_pin, b_pin, freq=1000):
        self.r = PWM(Pin(r_pin), freq=freq)
        self.g = PWM(Pin(g_pin), freq=freq)
        self.b = PWM(Pin(b_pin), freq=freq)

    def kleur(self, r, g, b):
        self.r.duty_u16(r * 257)
        self.g.duty_u16(g * 257)
        self.b.duty_u16(b * 257)

    def uit(self):
        self.kleur(0, 0, 0)


def kleur_voor_afstand(cm):
    """Map afstand naar (r, g, b)."""
    if cm is None or cm > 200:
        return 0, 0, 0
    if cm < 10:
        return 255, 0, 0
    if cm < 30:
        return 200, 80, 0
    return 0, 200, 0


def main():
    sonar = HCSR04(TRIG_PIN, ECHO_PIN)
    led = RgbLed(LED_R_PIN, LED_G_PIN, LED_B_PIN)

    print("Sonar gestart.")
    while True:
        cm = sonar.afstand_cm()
        led.kleur(*kleur_voor_afstand(cm))
        if cm is None:
            print("afstand: geen echo")
        else:
            print("afstand: {:.1f} cm".format(cm))
        time.sleep_ms(INTERVAL_MS)


main()
