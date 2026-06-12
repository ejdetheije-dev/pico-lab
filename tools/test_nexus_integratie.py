"""
Nexus integratie tests — laag 2.

Test samenwerking tussen modules: gedeelde I2C-bus, gelijktijdige sensor-
uitlezing, gecombineerde actuatoraansturing. Geen WiFi nodig.
Uitvoeren: mpremote run tools/test_nexus_integratie.py
"""

import time
from machine import I2C, Pin

results = []


def ok(naam, detail=""):
    msg = f"OK   {naam}" + (f"  ({detail})" if detail else "")
    print(msg)
    results.append((naam, True))


def fail(naam, reden):
    print(f"FAIL {naam}: {reden}")
    results.append((naam, False))


# ---------------------------------------------------------------------------
# I2C bus: beide adressen aanwezig (LCD 0x27 + BMP180 0x77)
# ---------------------------------------------------------------------------
try:
    i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)
    adressen = i2c.scan()
    assert 0x27 in adressen, f"LCD 0x27 niet op bus: {adressen}"
    assert 0x77 in adressen, f"BMP180 0x77 niet op bus: {adressen}"
    ok("I2C bus scan", f"adressen: {[hex(a) for a in adressen]}")
except Exception as e:
    fail("I2C bus scan", str(e))

# ---------------------------------------------------------------------------
# BMP180 leesbaar nadat LCD dezelfde I2C-bus heeft geïnitialiseerd
# ---------------------------------------------------------------------------
try:
    from output.lcd import LCD
    from sensors.bmp180 import BMP180
    lcd = LCD()
    bmp = BMP180(lcd.i2c)          # deelt de i2c instantie van LCD
    druk = bmp.lees_druk()
    assert 800 < druk < 1100, f"druk buiten bereik na LCD init: {druk}"
    lcd.toon("I2C bus OK", f"{druk:.0f} hPa")
    time.sleep(1)
    ok("BMP180 na LCD init", f"{druk:.1f} hPa  (gedeelde I2C bus)")
except Exception as e:
    fail("BMP180 na LCD init", str(e))

# ---------------------------------------------------------------------------
# Alle vier sensoren tegelijk initialiseerbaar en uitleesbaar
# ---------------------------------------------------------------------------
try:
    from sensors.dht11 import DHT11
    from sensors.hcsr04 import HCSR04
    from sensors.ldr import LDR

    dht = DHT11()
    sonar = HCSR04()
    ldr = LDR()
    # bmp en lcd al aangemaakt hierboven — hergebruik

    time.sleep(1)
    t, h = dht.lees()
    afstand = sonar.meet_afstand()
    licht = ldr.lees()
    druk2 = bmp.lees_druk()

    assert 0 < t < 60,   f"DHT11 temp: {t}"
    assert 0 < h <= 100, f"DHT11 vocht: {h}"
    assert licht is not None, "LDR geeft None"
    assert 800 < druk2 < 1100, f"BMP180: {druk2}"
    # HCSR04 kan None geven als niets in bereik — dat is geldig
    detail = f"temp={t}C vocht={h}% licht={licht}% druk={druk2:.0f}hPa sonar={round(afstand,1) if afstand else 'geen'}cm"
    ok("Alle sensoren tegelijk", detail)
except Exception as e:
    fail("Alle sensoren tegelijk", str(e))

# ---------------------------------------------------------------------------
# LCD update na relay-statuswijziging (geen resource conflict)
# ---------------------------------------------------------------------------
try:
    from output.relay import Relay
    from output.buzzer import Buzzer

    rel = Relay(21)
    buz = Buzzer()

    rel.aan()
    lcd.toon("Relay AAN", "Buzzer...")
    buz.piep(440, 80)
    assert rel.waarde() == 1, "relay niet hoog"
    time.sleep_ms(300)

    rel.uit()
    lcd.toon("Relay UIT", "")
    assert rel.waarde() == 0, "relay niet laag"

    ok("Relay + Buzzer + LCD", "geen conflict, relay schakelt")
except Exception as e:
    fail("Relay + Buzzer + LCD", str(e))

# ---------------------------------------------------------------------------
# LCD afkappen op 16 tekens (randgeval)
# ---------------------------------------------------------------------------
try:
    lcd.toon("1234567890123456789", "abcdefghijklmnopqrs")
    # geen exception = geslaagd; scherm toont max 16 tekens per regel
    ok("LCD afkappen", ">16 tekens zonder fout")
    time.sleep(1)
    lcd.toon("", "")
except Exception as e:
    fail("LCD afkappen", str(e))

# ---------------------------------------------------------------------------
# Samenvatting
# ---------------------------------------------------------------------------
print()
print("=" * 40)
geslaagd = sum(1 for _, v in results if v)
print(f"Integratie tests: {geslaagd}/{len(results)} OK")
for naam, v in results:
    if not v:
        print(f"  FAIL: {naam}")
