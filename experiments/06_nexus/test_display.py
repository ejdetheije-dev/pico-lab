import dht
import time
from machine import Pin, ADC, I2C
from output.lcd import LCD
from sensors.hcsr04 import HCSR04

DUUR = 60

dht11 = dht.DHT11(Pin(16, Pin.IN, Pin.PULL_UP))
ldr = ADC(26)
sonar = HCSR04()
lcd = LCD()

def lees_afstand():
    afstand = sonar.meet_afstand()
    if afstand is None or afstand > 400:
        return "---"
    return str(round(afstand)) + "cm"

def lees_licht():
    pct = min(100, max(0, round((ldr.read_u16() - 5000) / 150)))
    return str(pct) + "%"

start = time.ticks_ms()
print("Test gestart, loopt 60 seconden")

while time.ticks_diff(time.ticks_ms(), start) < DUUR * 1000:
    dht11.measure()
    temp = dht11.temperature()
    vocht = dht11.humidity()
    licht = lees_licht()
    afstand = lees_afstand()

    regel1 = str(temp) + "C " + str(vocht) + "%"
    regel2 = "L:" + licht + " A:" + afstand
    lcd.toon(regel1, regel2)
    print(regel1 + " | " + regel2)
    time.sleep(1)

lcd.toon("Klaar", "")
print("Test klaar")
