"""Weerstation — DHT11 uitlezen, weergeven op LCD, loggen naar CSV.

Meet elke 5 seconden temperatuur en luchtvochtigheid. Toont de waarden op
het LCD 1602 en schrijft een rij naar `data/weerstation.csv` op de flash.
"""

import time
import dht
from machine import Pin

from shared.display_helper import Lcd1602
from shared.logger import CsvLogger


DHT_PIN = 16
INTERVAL_S = 5


def main():
    sensor = dht.DHT11(Pin(DHT_PIN))
    lcd = Lcd1602(sda=0, scl=1)
    logger = CsvLogger(
        "data/weerstation.csv",
        header=["tijd", "temp_c", "vocht_pct"],
    )

    print("Weerstation gestart. Interval:", INTERVAL_S, "s")
    while True:
        sensor.measure()
        t = sensor.temperature()
        h = sensor.humidity()

        lcd.show("Temp: {} C".format(t), "Vocht: {} %".format(h))
        ok = logger.log(t, h)
        print("temp={}C vocht={}% gelogd={}".format(t, h, ok))

        time.sleep(INTERVAL_S)


main()
