"""WiFi-verbinding voor de Pico 2W.

Leest SSID en wachtwoord uit `config.py` (niet in git). Biedt een eenvoudige
`connect()` met timeout en een `ensure_connected()` voor herverbinding.
"""

import network
import time

try:
    import config
except ImportError:
    config = None


def _status_text(status):
    """Vertaal de netif-status naar leesbare tekst."""
    return {
        network.STAT_IDLE: "idle",
        network.STAT_CONNECTING: "bezig met verbinden",
        network.STAT_WRONG_PASSWORD: "verkeerd wachtwoord",
        network.STAT_NO_AP_FOUND: "AP niet gevonden",
        network.STAT_CONNECT_FAIL: "verbinding mislukt",
        network.STAT_GOT_IP: "verbonden",
    }.get(status, "onbekend")


def connect(timeout_s=15):
    """Maak verbinding met WiFi. Geeft het IP terug bij succes."""
    if config is None:
        raise RuntimeError("config.py ontbreekt (zie config.py.example)")

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("WiFi: verbinden met", config.WIFI_SSID)
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        deadline = time.ticks_add(time.ticks_ms(), timeout_s * 1000)
        while not wlan.isconnected():
            if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
                raise OSError("WiFi timeout: " + _status_text(wlan.status()))
            time.sleep_ms(200)

    ip = wlan.ifconfig()[0]
    print("WiFi: verbonden, IP", ip)
    return ip


def ensure_connected(timeout_s=15):
    """Herverbind als de verbinding verbroken is."""
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        return wlan.ifconfig()[0]
    return connect(timeout_s=timeout_s)
