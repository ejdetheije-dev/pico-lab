import network
import time
from config import WIFI_SSID, WIFI_PASSWORD
import supabase
from sensors.dht11 import DHT11
from sensors.hcsr04 import HCSR04
from sensors.ldr import LDR
from sensors.bmp180 import BMP180
from output.lcd import LCD
from output.buzzer import Buzzer

BEWEGING_DREMPEL = 50
AFWEZIG_NA = 30


def laad_settings():
    """Laad poll_interval_s en temp_alert_threshold uit Supabase. Geeft defaults bij fout."""
    s = supabase.get_settings()
    return {
        "poll_interval_s": int(s.get("poll_interval_s", 60)),
        "temp_alert_threshold": int(s.get("temp_alert_threshold", 30)),
    }


def verbind_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    print("Verbinden met", WIFI_SSID)
    for _ in range(20):
        if wlan.isconnected():
            print("Verbonden:", wlan.ifconfig()[0])
            return
        time.sleep(1)
    raise RuntimeError("WiFi verbinding mislukt")


verbind_wifi()

settings = laad_settings()
poll_interval = settings["poll_interval_s"]
print("Settings geladen: poll_interval_s =", poll_interval)

dht11 = DHT11()
sonar = HCSR04()
ldr = LDR()
lcd = LCD()
bmp180 = BMP180(lcd.i2c)
buzzer = Buzzer()

laatste_temp, laatste_vocht = 0, 0
for _ in range(5):
    try:
        laatste_temp, laatste_vocht = dht11.lees()
        break
    except OSError:
        time.sleep(2)
lcd.toon(str(laatste_temp) + "C " + str(laatste_vocht) + "%", "Nexus gestart")
print("Nexus gestart")

laatste_sensor_log = time.ticks_ms()
laatste_command_poll = time.ticks_ms()
beweging_actief = False
laatste_beweging = time.ticks_ms()
laatste_event = "-"

while True:
    nu = time.ticks_ms()

    # Bewegingsdetectie
    afstand = sonar.meet_afstand()
    if afstand is not None:
        if afstand < BEWEGING_DREMPEL and not beweging_actief:
            beweging_actief = True
            laatste_beweging = nu
            laatste_event = "Beweging!"
            print("Event: motion_detected, afstand:", round(afstand, 1))
            supabase.insert("events", {"type": "motion_detected", "payload": {"afstand_cm": round(afstand, 1)}})
        elif afstand >= BEWEGING_DREMPEL and beweging_actief:
            if time.ticks_diff(nu, laatste_beweging) > AFWEZIG_NA * 1000:
                beweging_actief = False
                laatste_event = "Geen beweging"
                print("Event: motion_absent")
                supabase.insert("events", {"type": "motion_absent"})

    # Sensor logging elke POLL_INTERVAL seconden
    if time.ticks_diff(nu, laatste_sensor_log) >= poll_interval * 1000:
        try:
            laatste_temp, laatste_vocht = dht11.lees()
        except OSError:
            time.sleep(2)
            try:
                laatste_temp, laatste_vocht = dht11.lees()
            except OSError:
                print("DHT11 fout, gebruik laatste waarde")
        licht = ldr.lees()
        druk = round(bmp180.lees_druk(), 1)
        print("Temp:", laatste_temp, "Vocht:", laatste_vocht, "Licht:", licht, "Druk:", druk)
        supabase.insert("sensor_readings", {"sensor": "dht11_temp", "value": laatste_temp})
        supabase.insert("sensor_readings", {"sensor": "dht11_humidity", "value": laatste_vocht})
        supabase.insert("sensor_readings", {"sensor": "ldr_light", "value": licht})
        supabase.insert("sensor_readings", {"sensor": "bmp180_pressure", "value": druk})
        laatste_sensor_log = time.ticks_ms()

    # Commands verwerken elke 10 seconden
    if time.ticks_diff(nu, laatste_command_poll) >= 10000:
        for cmd in supabase.get_pending_commands():
            type_ = cmd.get("command")
            payload = cmd.get("payload") or {}
            if type_ == "display_message":
                lcd.toon(payload.get("regel1", ""), payload.get("regel2", ""))
                time.sleep(3)
            elif type_ == "buzzer":
                buzzer.piep(payload.get("freq", 880), payload.get("duur_ms", 200))
            elif type_ == "set_setting":
                settings = laad_settings()
                poll_interval = settings["poll_interval_s"]
                print("Settings herladen: poll_interval_s =", poll_interval)
            supabase.mark_executed(cmd["id"])
        laatste_command_poll = time.ticks_ms()

    # LCD bijwerken
    lcd.toon(str(laatste_temp) + "C " + str(laatste_vocht) + "%", laatste_event)

    time.sleep(1)
