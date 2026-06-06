import dht
from machine import Pin


class DHT11:
    """Temperatuur- en vochtigheidssensor op de opgegeven GPIO-pin."""

    def __init__(self, pin=16):
        self._sensor = dht.DHT11(Pin(pin, Pin.IN, Pin.PULL_UP))

    def lees(self):
        """Geeft (temperatuur_c, vochtigheid_pct) terug."""
        self._sensor.measure()
        return self._sensor.temperature(), self._sensor.humidity()
