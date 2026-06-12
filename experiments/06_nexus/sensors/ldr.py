"""LDR (fotoresistor) op GPIO 26 via ADC.

Bedrading: 3.3V -> LDR -> GPIO 26 -> 1kOhm -> GND.
Hogere waarde = meer licht.
"""

from machine import ADC, Pin


class LDR:
    """Fotoresistor. Geeft lichtintensiteit 0-100 terug."""

    def __init__(self, pin=26, min_raw=4000, max_raw=34088):
        self.adc = ADC(Pin(pin))
        self.min_raw = min_raw
        self.max_raw = max_raw

    def lees(self):
        """Lichtintensiteit als percentage (0 = donker, 100 = fel)."""
        raw = self.adc.read_u16()
        pct = (raw - self.min_raw) / (self.max_raw - self.min_raw) * 100
        return max(0, min(100, round(pct)))
