"""
Nexus master test — voert alle drie testlagen achter elkaar uit.

  Laag 1: module tests      (geen hardware nodig buiten sensoren/actuatoren)
  Laag 2: integratie tests  (geen WiFi nodig)
  Laag 3: keten tests       (WiFi + Supabase vereist)

Uitvoeren: mpremote run tools/test_nexus_master.py
"""

import time
from machine import I2C, Pin

totaal_ok = 0
totaal_fail = 0
laag_resultaten = []


def sectie(titel):
    print()
    print("=" * 50)
    print(titel)
    print("=" * 50)


def check(naam, conditie, detail=""):
    global totaal_ok, totaal_fail
    if conditie:
        msg = f"OK   {naam}" + (f"  ({detail})" if detail else "")
        print(msg)
        totaal_ok += 1
        return True
    else:
        print(f"FAIL {naam}")
        totaal_fail += 1
        return False


# ============================================================
# LAAG 1: MODULE TESTS
# ============================================================
sectie("LAAG 1: MODULE TESTS")
laag1_ok = 0
laag1_fail = 0

# DHT11
try:
    from sensors.dht11 import DHT11
    time.sleep(1)
    t, h = DHT11().lees()
    ok = 0 < t < 60 and 0 < h <= 100
    check("DHT11.lees()", ok, f"{t}C {h}%")
    if ok: laag1_ok += 1
    else:  laag1_fail += 1
except Exception as e:
    print(f"FAIL DHT11.lees(): {e}"); laag1_fail += 1

# HCSR04
try:
    from sensors.hcsr04 import HCSR04
    af = HCSR04().meet_afstand()
    ok = af is None or (isinstance(af, float) and 2 <= af <= 400)
    check("HCSR04.meet_afstand()", ok, f"{round(af,1) if af else 'timeout'}cm")
    if ok: laag1_ok += 1
    else:  laag1_fail += 1
except Exception as e:
    print(f"FAIL HCSR04.meet_afstand(): {e}"); laag1_fail += 1

# LDR
try:
    from sensors.ldr import LDR
    ldr = LDR()
    pct = ldr.lees()
    raw = ldr.adc.read_u16()
    ok = 0 <= pct <= 100 and raw > 0
    check("LDR.lees()", ok, f"{pct}%  raw={raw}")
    if ok: laag1_ok += 1
    else:  laag1_fail += 1
except Exception as e:
    print(f"FAIL LDR.lees(): {e}"); laag1_fail += 1

# BMP180
try:
    from sensors.bmp180 import BMP180
    _i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)
    bmp = BMP180(_i2c)
    kalibs_ok = all(k in bmp._k for k in ("AC1","AC2","AC3","AC4","AC5","AC6","B1","B2","MC","MD"))
    t_bmp = bmp.lees_temperatuur()
    p = bmp.lees_druk()
    ok = kalibs_ok and 0 < t_bmp < 60 and 800 < p < 1100
    check("BMP180.lees_druk()", ok, f"{p:.1f}hPa {t_bmp:.1f}C kalibratie={'ok' if kalibs_ok else 'FAIL'}")
    if ok: laag1_ok += 1
    else:  laag1_fail += 1
except Exception as e:
    print(f"FAIL BMP180.lees_druk(): {e}"); laag1_fail += 1

# LCD
try:
    from output.lcd import LCD
    lcd = LCD()
    adressen = lcd.i2c.scan()
    ok = 0x27 in adressen
    lcd.toon("Master test", "LCD OK")
    time.sleep(1)
    check("LCD.toon()", ok, f"I2C scan: {[hex(a) for a in adressen]}")
    if ok: laag1_ok += 1
    else:  laag1_fail += 1
except Exception as e:
    print(f"FAIL LCD.toon(): {e}"); laag1_fail += 1

# Buzzer
try:
    from output.buzzer import Buzzer
    buz = Buzzer()
    buz.piep(660, 80)
    ok = True
    check("Buzzer.piep()", ok, "660Hz 80ms")
    if ok: laag1_ok += 1
    else:  laag1_fail += 1
except Exception as e:
    print(f"FAIL Buzzer.piep(): {e}"); laag1_fail += 1

# Relay
try:
    from output.relay import Relay
    rel = Relay(21)
    start_laag = rel.waarde() == 0
    rel.aan(); hoog = rel.waarde() == 1
    time.sleep_ms(200)
    rel.uit(); laag = rel.waarde() == 0
    ok = start_laag and hoog and laag
    check("Relay.aan()/uit()", ok, "GPIO 21 init->hoog->laag")
    if ok: laag1_ok += 1
    else:  laag1_fail += 1
except Exception as e:
    print(f"FAIL Relay.aan()/uit(): {e}"); laag1_fail += 1

totaal_ok += laag1_ok
totaal_fail += laag1_fail
laag_resultaten.append(("Laag 1 module", laag1_ok, laag1_ok + laag1_fail))

# ============================================================
# LAAG 2: INTEGRATIE TESTS
# ============================================================
sectie("LAAG 2: INTEGRATIE TESTS")
laag2_ok = 0
laag2_fail = 0

# I2C bus: beide adressen
try:
    adr = _i2c.scan()
    ok = 0x27 in adr and 0x77 in adr
    check("I2C bus: LCD(0x27) + BMP180(0x77)", ok, str([hex(a) for a in adr]))
    if ok: laag2_ok += 1
    else:  laag2_fail += 1
except Exception as e:
    print(f"FAIL I2C bus scan: {e}"); laag2_fail += 1

# BMP180 leesbaar na LCD init (gedeelde bus)
try:
    bmp2 = BMP180(lcd.i2c)
    p2 = bmp2.lees_druk()
    ok = 800 < p2 < 1100
    check("BMP180 na LCD init (gedeelde I2C)", ok, f"{p2:.1f}hPa")
    if ok: laag2_ok += 1
    else:  laag2_fail += 1
except Exception as e:
    print(f"FAIL BMP180 na LCD init: {e}"); laag2_fail += 1

# Alle sensoren tegelijk leesbaar
try:
    time.sleep(1)
    t2, h2 = DHT11().lees()
    af2 = HCSR04().meet_afstand()
    licht2 = LDR().lees()
    druk2 = round(BMP180(lcd.i2c).lees_druk(), 1)
    ok = 0 < t2 < 60 and 0 < h2 <= 100 and 0 <= licht2 <= 100 and 800 < druk2 < 1100
    check("Alle sensoren tegelijk", ok,
          f"temp={t2}C vocht={h2}% licht={licht2}% druk={druk2}hPa sonar={round(af2,1) if af2 else 'geen'}cm")
    if ok: laag2_ok += 1
    else:  laag2_fail += 1
except Exception as e:
    print(f"FAIL Alle sensoren tegelijk: {e}"); laag2_fail += 1

# Relay + Buzzer + LCD zonder conflict
try:
    rel2 = Relay(21)
    rel2.aan()
    lcd.toon("Relay AAN", "Buzzer...")
    buz.piep(440, 80)
    ok1 = rel2.waarde() == 1
    time.sleep_ms(300)
    rel2.uit()
    lcd.toon("Relay UIT", "")
    ok2 = rel2.waarde() == 0
    ok = ok1 and ok2
    check("Relay + Buzzer + LCD", ok, "geen conflict")
    if ok: laag2_ok += 1
    else:  laag2_fail += 1
except Exception as e:
    print(f"FAIL Relay + Buzzer + LCD: {e}"); laag2_fail += 1

# LCD afkapping >16 tekens
try:
    lcd.toon("1234567890123456789", "abcdefghijklmnopqrs")
    time.sleep_ms(500)
    lcd.toon("", "")
    check("LCD afkappen >16 tekens", True)
    laag2_ok += 1
except Exception as e:
    print(f"FAIL LCD afkappen: {e}"); laag2_fail += 1

totaal_ok += laag2_ok
totaal_fail += laag2_fail
laag_resultaten.append(("Laag 2 integratie", laag2_ok, laag2_ok + laag2_fail))

# ============================================================
# LAAG 3: KETEN TESTS (WiFi + Supabase)
# ============================================================
sectie("LAAG 3: KETEN TESTS")
laag3_ok = 0
laag3_fail = 0
wifi_ok = False

# WiFi
try:
    import network
    from config import WIFI_SSID, WIFI_PASSWORD
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        for _ in range(20):
            if wlan.isconnected(): break
            time.sleep(1)
    wifi_ok = wlan.isconnected()
    check("WiFi verbinding", wifi_ok, wlan.ifconfig()[0] if wifi_ok else "timeout")
    if wifi_ok: laag3_ok += 1
    else:       laag3_fail += 1
except Exception as e:
    print(f"FAIL WiFi: {e}"); laag3_fail += 1

if wifi_ok:
    import supabase

    # Sensor insert
    try:
        supabase.insert("sensor_readings", {"sensor": "keten_test", "value": 1.0})
        check("supabase.insert(sensor_readings)", True)
        laag3_ok += 1
    except Exception as e:
        print(f"FAIL supabase.insert: {e}"); laag3_fail += 1

    # Vier sensor inserts (zoals main.py)
    try:
        time.sleep(1)
        t3, h3 = DHT11().lees()
        l3 = LDR().lees()
        p3 = round(BMP180(lcd.i2c).lees_druk(), 1)
        supabase.insert("sensor_readings", {"sensor": "dht11_temp",      "value": t3})
        supabase.insert("sensor_readings", {"sensor": "dht11_humidity",  "value": h3})
        supabase.insert("sensor_readings", {"sensor": "ldr_light",       "value": l3})
        supabase.insert("sensor_readings", {"sensor": "bmp180_pressure", "value": p3})
        check("Vier sensor inserts", True, f"temp={t3} vocht={h3} licht={l3} druk={p3}")
        laag3_ok += 1
    except Exception as e:
        print(f"FAIL vier sensor inserts: {e}"); laag3_fail += 1

    # Settings ophalen
    try:
        s = supabase.get_settings()
        ok = isinstance(s, dict) and "poll_interval_s" in s and "temp_alert_threshold" in s
        check("supabase.get_settings()", ok, str(s))
        if ok: laag3_ok += 1
        else:  laag3_fail += 1
    except Exception as e:
        print(f"FAIL get_settings: {e}"); laag3_fail += 1

    # Command lifecycle
    try:
        supabase.insert("commands", {"command": "keten_test", "payload": {"run": True}})
        cmds = supabase.get_pending_commands()
        test_cmds = [c for c in cmds if c.get("command") == "keten_test"]
        assert len(test_cmds) > 0, "testcommand niet teruggevonden"
        cmd_id = test_cmds[0]["id"]
        supabase.mark_executed(cmd_id)
        time.sleep_ms(500)
        cmds_na = supabase.get_pending_commands()
        nog_open = [c for c in cmds_na if c.get("id") == cmd_id]
        ok = len(nog_open) == 0
        check("Command lifecycle", ok, f"id={cmd_id} insert->pending->mark_executed")
        if ok: laag3_ok += 1
        else:  laag3_fail += 1
    except Exception as e:
        print(f"FAIL command lifecycle: {e}"); laag3_fail += 1

    # Event insert
    try:
        supabase.insert("events", {"type": "keten_test", "payload": {"bron": "test_nexus_master"}})
        check("supabase.insert(events)", True)
        laag3_ok += 1
    except Exception as e:
        print(f"FAIL event insert: {e}"); laag3_fail += 1

else:
    print("SKIP keten tests — geen WiFi")

totaal_ok += laag3_ok
totaal_fail += laag3_fail
laag_resultaten.append(("Laag 3 keten", laag3_ok, laag3_ok + laag3_fail))

# ============================================================
# EINDRAPPORT
# ============================================================
print()
print("=" * 50)
print("EINDRAPPORT")
print("=" * 50)
for naam, ok_n, totaal_n in laag_resultaten:
    status = "OK" if ok_n == totaal_n else "FAIL"
    print(f"  {naam}: {ok_n}/{totaal_n}  [{status}]")
print(f"\nTotaal: {totaal_ok}/{totaal_ok + totaal_fail} OK")
if totaal_fail == 0:
    print("Alles geslaagd.")
else:
    print(f"{totaal_fail} test(s) gefaald — zie boven voor details.")
