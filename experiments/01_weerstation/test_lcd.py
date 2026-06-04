"""Minimale LCD-test — toont twee regels tekst."""

from shared.display_helper import Lcd1602

lcd = Lcd1602(sda=0, scl=1)
lcd.show("LCD test OK", "regel 2")
print("Klaar")
