"""
Nexus keten tests — laag 3.

Test de volledige keten: Pico → WiFi → Supabase (lees + schrijf).
Vereist: config.py op de Pico (WiFi-credentials + Supabase-key).
Uitvoeren: mpremote run tools/test_nexus_keten.py
"""

import network
import time

results = []


def ok(naam, detail=""):
    msg = f"OK   {naam}" + (f"  ({detail})" if detail else "")
    print(msg)
    results.append((naam, True))


def fail(naam, reden):
    print(f"FAIL {naam}: {reden}")
    results.append((naam, False))


# ---------------------------------------------------------------------------
# WiFi verbinding
# ---------------------------------------------------------------------------
wlan = None
try:
    from config import WIFI_SSID, WIFI_PASSWORD
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    for _ in range(20):
        if wlan.isconnected():
            break
        time.sleep(1)
    assert wlan.isconnected(), "geen verbinding na 20s"
    ip = wlan.ifconfig()[0]
    ok("WiFi verbinding", ip)
except Exception as e:
    fail("WiFi verbinding", str(e))
    print("Keten tests gestopt — geen WiFi.")
    raise SystemExit

# ---------------------------------------------------------------------------
# Supabase: sensor_readings insert
# ---------------------------------------------------------------------------
try:
    import supabase
    supabase.insert("sensor_readings", {"sensor": "keten_test", "value": 1.0})
    ok("supabase.insert(sensor_readings)", "geen exception")
except Exception as e:
    fail("supabase.insert(sensor_readings)", str(e))

# ---------------------------------------------------------------------------
# Supabase: alle vier sensortypen in volgorde (zoals main.py dat doet)
# ---------------------------------------------------------------------------
try:
    from sensors.dht11 import DHT11
    from sensors.ldr import LDR
    from sensors.bmp180 import BMP180
    from machine import I2C, Pin

    i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)
    dht = DHT11()
    ldr = LDR()
    bmp = BMP180(i2c)

    time.sleep(1)
    t, h = dht.lees()
    licht = ldr.lees()
    druk = round(bmp.lees_druk(), 1)

    supabase.insert("sensor_readings", {"sensor": "dht11_temp",      "value": t})
    supabase.insert("sensor_readings", {"sensor": "dht11_humidity",  "value": h})
    supabase.insert("sensor_readings", {"sensor": "ldr_light",       "value": licht})
    supabase.insert("sensor_readings", {"sensor": "bmp180_pressure", "value": druk})

    ok("Vier sensor inserts", f"temp={t}C vocht={h}% licht={licht}% druk={druk}hPa")
except Exception as e:
    fail("Vier sensor inserts", str(e))

# ---------------------------------------------------------------------------
# Supabase: settings ophalen
# ---------------------------------------------------------------------------
try:
    settings = supabase.get_settings()
    assert isinstance(settings, dict), f"geen dict: {type(settings)}"
    assert "poll_interval_s" in settings, f"poll_interval_s ontbreekt: {settings}"
    assert "temp_alert_threshold" in settings, f"temp_alert_threshold ontbreekt: {settings}"
    ok("supabase.get_settings()", f"poll={settings['poll_interval_s']}s  temp_drempel={settings['temp_alert_threshold']}")
except Exception as e:
    fail("supabase.get_settings()", str(e))

# ---------------------------------------------------------------------------
# Supabase: command lifecycle (insert → ophalen → markeren)
# ---------------------------------------------------------------------------
try:
    import ujson

    # Schrijf een testcommand
    supabase.insert("commands", {"command": "keten_test", "payload": {"run": True}})

    # Haal openstaande commands op — testcommand moet erin zitten
    cmds = supabase.get_pending_commands()
    assert isinstance(cmds, list), f"geen list: {type(cmds)}"

    test_cmds = [c for c in cmds if c.get("command") == "keten_test"]
    assert len(test_cmds) > 0, "testcommand niet teruggevonden in pending commands"

    # Markeer het eerste testcommand als uitgevoerd
    cmd_id = test_cmds[0]["id"]
    supabase.mark_executed(cmd_id)

    # Verifieer: command mag niet meer in pending staan
    time.sleep_ms(500)
    cmds_na = supabase.get_pending_commands()
    nog_open = [c for c in cmds_na if c.get("id") == cmd_id]
    assert len(nog_open) == 0, f"command {cmd_id} nog steeds pending na mark_executed"

    ok("Command lifecycle", f"id={cmd_id} insert->ophalen->mark_executed")
except Exception as e:
    fail("Command lifecycle", str(e))

# ---------------------------------------------------------------------------
# Supabase: motion event insert
# ---------------------------------------------------------------------------
try:
    supabase.insert("events", {"type": "keten_test", "payload": {"bron": "test_nexus_keten"}})
    ok("supabase.insert(events)", "geen exception")
except Exception as e:
    fail("supabase.insert(events)", str(e))

# ---------------------------------------------------------------------------
# Samenvatting
# ---------------------------------------------------------------------------
print()
print("=" * 40)
geslaagd = sum(1 for _, v in results if v)
print(f"Keten tests: {geslaagd}/{len(results)} OK")
for naam, v in results:
    if not v:
        print(f"  FAIL: {naam}")
