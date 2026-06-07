from machine import Pin, PWM
import time


class Buzzer:
    """Passieve buzzer op GPIO 9, aangestuurd via PWM."""

    def __init__(self, pin=9):
        self._pwm = PWM(Pin(pin))

    def piep(self, freq=880, duur_ms=200):
        """Speel een toon op de opgegeven frequentie en duur."""
        self._pwm.freq(freq)
        self._pwm.duty_u16(32768)
        time.sleep_ms(duur_ms)
        self._pwm.duty_u16(0)
