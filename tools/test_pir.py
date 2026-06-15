"""Diagnose HC-SR501 PIR op GPIO 17 — print elke seconde de raw waarde."""
from machine import Pin
import time

pir = Pin(22, Pin.IN, Pin.PULL_DOWN)

print("Raw waarde elke seconde (0=laag, 1=hoog):")
while True:
    print(pir.value())
    time.sleep(1)
