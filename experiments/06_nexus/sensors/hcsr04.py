from machine import Pin
import time


class HCSR04:
    """Ultrasone afstandssensor op trigger- en echo-pin."""

    def __init__(self, trigger=17, echo=18):
        self._trig = Pin(trigger, Pin.OUT)
        self._echo = Pin(echo, Pin.IN)

    def meet_afstand(self):
        """Geeft afstand in cm terug, of None bij timeout."""
        self._trig.low()
        time.sleep_us(2)
        self._trig.high()
        time.sleep_us(10)
        self._trig.low()

        timeout = time.ticks_add(time.ticks_us(), 30000)
        while self._echo.value() == 0:
            if time.ticks_diff(timeout, time.ticks_us()) <= 0:
                return None
        start = time.ticks_us()

        timeout = time.ticks_add(time.ticks_us(), 30000)
        while self._echo.value() == 1:
            if time.ticks_diff(timeout, time.ticks_us()) <= 0:
                return None
        end = time.ticks_us()

        return (time.ticks_diff(end, start) * 0.0343) / 2
