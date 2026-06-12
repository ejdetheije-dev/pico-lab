"""
Nexus module tests — laag 1.

Test elke klasse in isolatie: correcte init, sane return-waarden.
Uitvoeren: mpremote run tools/test_nexus_module.py
"""

import time
from machine import Pin, ADC, I2C, PWM

results = []


def ok(naam, detail=""):
    msg = f"OK   {naam}" + (f"  ({detail})" if detail else "")
    print(msg)
    results.append((naam, True))


def fail(naam, reden):
    print(f"FAIL {naam}: {reden}")
    results.append((naam, False))


# ---------------------------------------------------------------------------
# DHT11
# ---------------------------------------------------------------------------
try:
    from sensors.dht11 import DHT11
    s = DHT11()
    time.sleep(1)
    t, h = s.lees()
    assert isinstance(t, int), "temp geen int"
    assert isinstance(h, int), "vocht geen int"
    assert 0 < t < 60,  f"temp buiten bereik: {t}"
    assert 0 < h <= 100, f"vocht buiten bereik: {h}"
    ok("DHT11.lees()", f"{t}C {h}%")
except Exception as e:
    fail("DHT11.lees()", str(e))

# ---------------------------------------------------------------------------
# HCSR04
# ---------------------------------------------------------------------------
try:
    from sensors.hcsr04 import HCSR04
    sonar = HCSR04()
    afstand = sonar.meet_afstand()
    assert afstand is None or isinstance(afstand, float), "verwacht float of None"
    if afstand is not None:
        assert 2 <= afstand <= 400, f"afstand buiten bereik: {afstand}"
    ok("HCSR04.meet_afstand()", f"{round(afstand,1) if afstand else 'timeout'} cm")
except Exception as e:
    fail("HCSR04.meet_afstand()", str(e))

# ---------------------------------------------------------------------------
# LDR
# ---------------------------------------------------------------------------
try:
    from sensors.ldr import LDR
    ldr = LDR()
    pct = ldr.lees()
    raw = ldr.adc.read_u16()
    assert isinstance(pct, int), "verwacht int"
    assert 0 <= pct <= 100, f"percentage buiten bereik: {pct}"
    assert raw > 0, f"raw ADC nul — pin los?"
    ok("LDR.lees()", f"{pct}%  raw={raw}")
except Exception as e:
    fail("LDR.lees()", str(e))

# ---------------------------------------------------------------------------
# BMP180
# ---------------------------------------------------------------------------
try:
    from sensors.bmp180 import BMP180
    i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)
    bmp = BMP180(i2c)
    # kalibratieparameters geladen
    for k in ("AC1", "AC2", "AC3", "AC4", "AC5", "AC6", "B1", "B2", "MC", "MD"):
        assert k in bmp._k, f"kalibratieparameter {k} ontbreekt"
    t_bmp = bmp.lees_temperatuur()
    p = bmp.lees_druk()
    assert 0 < t_bmp < 60,   f"temp buiten bereik: {t_bmp}"
    assert 800 < p < 1100,   f"druk buiten bereik: {p}"
    ok("BMP180.lees_druk()", f"{p:.1f} hPa  {t_bmp:.1f}C")
except Exception as e:
    fail("BMP180.lees_druk()", str(e))

# ---------------------------------------------------------------------------
# LCD
# ---------------------------------------------------------------------------
try:
    from output.lcd import LCD
    lcd = LCD()
    # I2C-adres bereikbaar (init zou al gefaald hebben, maar verifieer scan)
    adressen = lcd.i2c.scan()
    assert 0x27 in adressen, f"0x27 niet gevonden, scan: {adressen}"
    lcd.toon("ModuleTest", "LCD OK")
    time.sleep(1)
    lcd.toon("", "")
    ok("LCD.toon()", "0x27 gevonden, tekst geschreven")
except Exception as e:
    fail("LCD.toon()", str(e))

# ---------------------------------------------------------------------------
# Buzzer
# ---------------------------------------------------------------------------
try:
    from output.buzzer import Buzzer
    buz = Buzzer()
    assert hasattr(buz, "_pwm"), "PWM-object ontbreekt"
    buz.piep(freq=660, duur_ms=100)
    ok("Buzzer.piep()", "660 Hz 100 ms (hoorbaar)")
except Exception as e:
    fail("Buzzer.piep()", str(e))

# ---------------------------------------------------------------------------
# Relay
# ---------------------------------------------------------------------------
try:
    from output.relay import Relay
    rel = Relay(21)
    assert rel.waarde() == 0, "relay niet laag na init"
    rel.aan()
    assert rel.waarde() == 1, "relay niet hoog na aan()"
    time.sleep_ms(300)
    rel.uit()
    assert rel.waarde() == 0, "relay niet laag na uit()"
    ok("Relay.aan()/uit()", "GPIO 21, klik gehoord")
except Exception as e:
    fail("Relay.aan()/uit()", str(e))

# ---------------------------------------------------------------------------
# Samenvatting
# ---------------------------------------------------------------------------
print()
print("=" * 40)
geslaagd = sum(1 for _, v in results if v)
print(f"Module tests: {geslaagd}/{len(results)} OK")
for naam, v in results:
    if not v:
        print(f"  FAIL: {naam}")
