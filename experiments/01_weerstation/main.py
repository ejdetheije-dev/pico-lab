"""Weerstation — DHT11 + LDR uitlezen, weergeven op LCD, loggen naar CSV.

Meet elke 5 seconden temperatuur, luchtvochtigheid en lichtintensiteit.
Toont de waarden op het LCD 1602 en schrijft een rij naar
`data/weerstation.csv` op de flash.
"""

import time
import dht
from machine import Pin

from shared.display_helper import Lcd1602
from shared.logger import CsvLogger
from shared.ldr import Ldr


DHT_PIN = 16
LDR_PIN = 26
INTERVAL_S = 5


def main():
    sensor = dht.DHT11(Pin(DHT_PIN, Pin.IN, Pin.PULL_UP))
    ldr = Ldr(LDR_PIN)
    lcd = Lcd1602(sda=0, scl=1)
    logger = CsvLogger(
        "data/weerstation.csv",
        header=["tijd", "temp_c", "vocht_pct", "licht_pct"],
    )

    print("Weerstation gestart. Interval:", INTERVAL_S, "s")
    while True:
        sensor.measure()
        t = sensor.temperature()
        h = sensor.humidity()
        l = ldr.lees()

        lcd.show(
            "T:{}C  V:{}%".format(t, h),
            "Licht: {}%".format(l),
        )
        ok = logger.log(t, h, l)
        print("temp={}C vocht={}% licht={}% gelogd={}".format(t, h, l, ok))

        time.sleep(INTERVAL_S)


main()
