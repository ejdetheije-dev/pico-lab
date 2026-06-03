"""Smoketest — bewijst dat upload + soft reset werken.

Knippert de onboard LED 5x en print twee bevestigingen. Geen externe
hardware nodig. Bedoeld om de upload-workflow te valideren.
"""

import time
from machine import Pin


def main():
    led = Pin("LED", Pin.OUT)
    print("smoketest gestart")
    for _ in range(5):
        led.toggle()
        time.sleep(0.3)
        led.toggle()
        time.sleep(0.3)
    print("smoketest klaar")


main()
