import network
import time
from config import WIFI_SSID, WIFI_PASSWORD
import supabase
from sensors.dht11 import DHT11
from sensors.hcsr04 import HCSR04
from output.lcd import LCD

POLL_INTERVAL = 60
BEWEGING_DREMPEL = 50
AFWEZIG_NA = 30


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

dht11 = DHT11()
sonar = HCSR04()
lcd = LCD()

laatste_temp, laatste_vocht = dht11.lees()
lcd.toon(str(laatste_temp) + "C " + str(laatste_vocht) + "%", "Nexus gestart")
print("Nexus gestart")

laatste_sensor_log = time.ticks_ms()
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
    if time.ticks_diff(nu, laatste_sensor_log) >= POLL_INTERVAL * 1000:
        laatste_temp, laatste_vocht = dht11.lees()
        print("Temp:", laatste_temp, "Vocht:", laatste_vocht)
        supabase.insert("sensor_readings", {"sensor": "dht11_temp", "value": laatste_temp})
        supabase.insert("sensor_readings", {"sensor": "dht11_humidity", "value": laatste_vocht})
        laatste_sensor_log = nu

    # LCD bijwerken
    lcd.toon(str(laatste_temp) + "C " + str(laatste_vocht) + "%", laatste_event)

    time.sleep(1)
