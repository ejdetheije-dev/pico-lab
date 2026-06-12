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
from output.relay import Relay
from output.pushover import stuur as pushover

BEWEGING_DREMPEL = 50
AFWEZIG_NA = 30


def laad_settings():
    """Laad settings uit Supabase. Geeft defaults bij fout."""
    s = supabase.get_settings()
    return {
        "poll_interval_s": int(s.get("poll_interval_s", 60)),
        "temp_alert_threshold": int(s.get("temp_alert_threshold", 30)),
        "pushover_enabled": s.get("pushover_enabled", "false") == "true",
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
ventilator = Relay(21)

laatste_temp, laatste_vocht = 0, 0
for _ in range(5):
    try:
        laatste_temp, laatste_vocht = dht11.lees()
        break
    except Exception:
        time.sleep(2)
laatste_licht = ldr.lees()
laatste_druk = round(bmp180.lees_druk(), 1)
lcd.toon(str(laatste_temp) + "C " + str(laatste_vocht) + "%", "Nexus gestart")
print("Nexus gestart")

laatste_sensor_log = time.ticks_ms()
laatste_command_poll = time.ticks_ms()
laatste_lcd_update = time.ticks_ms()
beweging_actief = False
laatste_beweging = time.ticks_ms()
laatste_event = "-"
temp_alert_actief = False
lcd_scherm = 0

def verwerk_commands():
    global laatste_command_poll, poll_interval, settings
    if time.ticks_diff(time.ticks_ms(), laatste_command_poll) < 3000:
        return
    for cmd in supabase.get_pending_commands():
        type_ = cmd.get("command")
        payload = cmd.get("payload") or {}
        if type_ == "display_message":
            lcd.toon(payload.get("regel1", ""), payload.get("regel2", ""))
            time.sleep(3)
        elif type_ == "buzzer":
            buzzer.piep(payload.get("freq", 880), payload.get("duur_ms", 200))
        elif type_ == "fan_on":
            ventilator.aan()
            lcd.toon("Ventilator", "AAN")
            time.sleep(2)
        elif type_ == "fan_off":
            ventilator.uit()
            lcd.toon("Ventilator", "UIT")
            time.sleep(2)
        elif type_ == "notify":
            if settings["pushover_enabled"]:
                bericht = payload.get("bericht", "")
                if pushover(bericht, payload.get("titel", "Nexus")):
                    supabase.insert("events", {"type": "pushover_sent", "payload": {"bericht": bericht}})
        elif type_ == "set_setting":
            settings = laad_settings()
            poll_interval = settings["poll_interval_s"]
            print("Settings herladen: poll_interval_s =", poll_interval)
        supabase.mark_executed(cmd["id"])
    laatste_command_poll = time.ticks_ms()


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
            if settings["pushover_enabled"]:
                if pushover("Beweging gedetecteerd (" + str(round(afstand, 1)) + " cm)"):
                    supabase.insert("events", {"type": "pushover_sent", "payload": {"bericht": "Beweging gedetecteerd"}})
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
        except Exception:
            time.sleep(2)
            try:
                laatste_temp, laatste_vocht = dht11.lees()
            except Exception:
                print("DHT11 fout, gebruik laatste waarde")
        laatste_licht = ldr.lees()
        laatste_druk = round(bmp180.lees_druk(), 1)
        print("Temp:", laatste_temp, "Vocht:", laatste_vocht, "Licht:", laatste_licht, "Druk:", laatste_druk)
        supabase.insert("sensor_readings", {"sensor": "dht11_temp", "value": laatste_temp})
        verwerk_commands()
        supabase.insert("sensor_readings", {"sensor": "dht11_humidity", "value": laatste_vocht})
        verwerk_commands()
        supabase.insert("sensor_readings", {"sensor": "ldr_light", "value": laatste_licht})
        verwerk_commands()
        supabase.insert("sensor_readings", {"sensor": "bmp180_pressure", "value": laatste_druk})
        laatste_sensor_log = time.ticks_ms()
        laatste_lcd_update = 0  # forceer direct LCD refresh

        # Temperatuuralert: stuur eenmalig bij overschrijding, reset bij herstel
        drempel = settings["temp_alert_threshold"]
        if laatste_temp > drempel and not temp_alert_actief:
            temp_alert_actief = True
            if settings["pushover_enabled"]:
                bericht = "Temperatuur " + str(laatste_temp) + "C (drempel " + str(drempel) + "C)"
                if pushover(bericht, "Nexus alert"):
                    supabase.insert("events", {"type": "pushover_sent", "payload": {"bericht": bericht}})
        elif laatste_temp <= drempel and temp_alert_actief:
            temp_alert_actief = False

    verwerk_commands()

    # LCD roteren: scherm 0 = sensoren, scherm 1 = beweging — elke 4s wisselen
    if time.ticks_diff(time.ticks_ms(), laatste_lcd_update) >= 4000:
        if lcd_scherm == 0:
            r1 = str(laatste_temp) + "C " + str(laatste_vocht) + "% " + str(int(laatste_druk)) + "h"
            r2 = "Licht:" + str(laatste_licht) + "%"
        else:
            r1 = "Beweging: " + ("JA!" if beweging_actief else "nee")
            r2 = laatste_event
        lcd.toon(r1, r2)
        lcd_scherm = 1 - lcd_scherm
        laatste_lcd_update = time.ticks_ms()

    time.sleep(1)
