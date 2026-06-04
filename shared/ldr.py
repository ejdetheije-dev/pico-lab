"""LDR (fotoresistor) via ADC.

Bedrading: 3.3V → LDR → GPIO-pin → 1kΩ → GND.
Hogere waarde = meer licht.

min_raw en max_raw zijn gekalibreerd op de meetomgeving:
stel ze bij als de sensor verplaatst wordt of de omgeving sterk verandert.
"""

from machine import ADC, Pin


class Ldr:
    """Fotoresistor op een ADC-pin. Geeft lichtintensiteit 0-100 terug."""

    def __init__(self, pin=26, min_raw=5600, max_raw=25000):
        self.adc = ADC(Pin(pin))
        self.min_raw = min_raw
        self.max_raw = max_raw

    def lees(self):
        """Lichtintensiteit als percentage (0 = donker, 100 = fel)."""
        raw = self.adc.read_u16()
        pct = (raw - self.min_raw) / (self.max_raw - self.min_raw) * 100
        return max(0, min(100, round(pct)))
