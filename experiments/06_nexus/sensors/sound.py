from machine import ADC, Pin
import time

DREMPEL = 8000


class Sound:
    """MAX4466 microfoon op ADC. Meet piek-tot-piek amplitude over 50ms."""

    def __init__(self, pin=27):
        self.adc = ADC(Pin(pin))

    def meet_amplitude(self):
        """Piek-tot-piek amplitude (ADC counts) over 50 samples."""
        laag = 65535
        hoog = 0
        for _ in range(50):
            v = self.adc.read_u16()
            if v < laag:
                laag = v
            if v > hoog:
                hoog = v
            time.sleep_us(1000)
        return hoog - laag
