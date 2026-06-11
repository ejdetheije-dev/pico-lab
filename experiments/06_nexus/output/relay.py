"""4-kanaals relaismodule. Kanaal 2 stuurt de ventilator (GPIO 21, HIGH trigger, 3V3)."""

from machine import Pin


class Relay:
    """Eén relaiskanaal, active HIGH."""

    def __init__(self, pin):
        self._pin = Pin(pin, Pin.OUT)
        self._pin.low()

    def aan(self):
        self._pin.high()

    def uit(self):
        self._pin.low()

    def waarde(self):
        return self._pin.value()
