"""LDR (fotoresistor) via ADC.

Verwachte bedrading: 3.3V → LDR → GPIO-pin → 1kΩ → GND.
Hogere waarde = meer licht.
"""

from machine import ADC, Pin


class Ldr:
    """Fotoresistor op een ADC-pin. Geeft lichtintensiteit 0-100 terug."""

    def __init__(self, pin=26):
        self.adc = ADC(Pin(pin))

    def lees(self):
        """Lichtintensiteit als percentage (0 = donker, 100 = fel)."""
        return round(self.adc.read_u16() / 655)
