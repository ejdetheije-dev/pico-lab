import network
import urequests
import ujson
import time
from config import WIFI_SSID, WIFI_PASSWORD, SUPABASE_URL, SUPABASE_KEY

def verbind_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    print("Verbinden met", WIFI_SSID)
    for _ in range(20):
        if wlan.isconnected():
            print("Verbonden:", wlan.ifconfig()[0])
            return True
        time.sleep(1)
        print(".")
    print("Verbinding mislukt")
    return False

def test_post():
    url = SUPABASE_URL + "/rest/v1/sensor_readings"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": "Bearer " + SUPABASE_KEY,
        "Content-Type": "application/json"
    }
    data = ujson.dumps({"sensor": "test", "value": 42.0})
    r = urequests.post(url, headers=headers, data=data)
    print("Status:", r.status_code)
    r.close()

if verbind_wifi():
    test_post()
