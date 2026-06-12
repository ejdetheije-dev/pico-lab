from machine import ADC, Pin
import time, sys

adc = ADC(Pin(27))
DREMPEL = 8000

sys.stdout.write("MAX4466 test\n")

while True:
    laag = 65535
    hoog = 0
    for _ in range(50):
        v = adc.read_u16()
        if v < laag:
            laag = v
        if v > hoog:
            hoog = v
        time.sleep_us(1000)
    amplitude = hoog - laag
    status = "GELUID" if amplitude > DREMPEL else "stil"
    sys.stdout.write(status + " " + str(amplitude) + "\n")
