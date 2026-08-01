import io
import machine
import network
import sys
import time
import watchdog
from config import WIFI_SSID, WIFI_PASSWORD
import supabase
from sensors.dht11 import DHT11
from sensors.hcsr04 import HCSR04
from sensors.ldr import LDR
from sensors.p1 import lees as lees_p1, P1_HOST
from sensors.sound import Sound, DREMPEL as GELUID_DREMPEL
from output.lcd import LCD
from output.buzzer import Buzzer
from output.relay import Relay
from output.pushover import stuur as pushover

BEWEGING_DELTA = 15  # cm dichter dan rustafstand = beweging
AFWEZIG_NA = 30
GELUID_AFWEZIG_NA = 5

# De P1 lezen is goedkoop (LAN, geen TLS), wegschrijven naar Supabase is duur. Dus vaak
# sampelen in RAM en een keer per logcyclus in bulk flushen.
P1_SAMPLE_MS = 15_000
# Ruim een uur buffer. Loopt hij vol doordat Supabase langer weg is, dan vallen de oudste
# samples af: de meterstanden zijn cumulatief, dus de recentste zijn het meest waard.
P1_BUFFER_MAX = 240
# Rem op de foutlogging: een onbereikbare meter mag de events-tabel niet volschrijven.
P1_FOUT_STIL_MS = 300_000


def laad_settings():
    """Laad settings uit Supabase. Geeft defaults bij fout."""
    s = supabase.get_settings()
    return {
        "poll_interval_s": int(s.get("poll_interval_s", 60)),
        "temp_alert_threshold": int(s.get("temp_alert_threshold", 30)),
        "pushover_enabled": s.get("pushover_enabled", "false") == "true",
        "lcd_backlight": s.get("lcd_backlight", "true") == "true",
    }


wlan = network.WLAN(network.STA_IF)


def verbind_wifi():
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    print("Verbinden met", WIFI_SSID)
    for _ in range(20):
        if wlan.isconnected():
            print("Verbonden:", wlan.ifconfig()[0])
            return
        watchdog.sleep(1)
    raise RuntimeError("WiFi verbinding mislukt")


def herverbind_indien_nodig():
    if not wlan.isconnected():
        print("WiFi weg — herverbinden...")
        wlan.disconnect()
        watchdog.sleep(1)
        try:
            verbind_wifi()
        except RuntimeError:
            print("Herverbinding mislukt, volgende cyclus opnieuw proberen")


verbind_wifi()

settings = laad_settings()
poll_interval = settings["poll_interval_s"]
print("Settings geladen: poll_interval_s =", poll_interval)

dht11 = DHT11()
sonar = HCSR04()
ldr = LDR()
geluid = Sound()
lcd = LCD()
lcd.set_backlight(settings["lcd_backlight"])
buzzer = Buzzer()
ventilator = Relay(21)

metingen = [m for _ in range(5) if (m := sonar.meet_afstand()) is not None]
baseline_afstand = sum(metingen) / len(metingen) if metingen else 200
print("Baseline HC-SR04:", round(baseline_afstand, 1), "cm")

laatste_temp, laatste_vocht = 0, 0
for _ in range(5):
    try:
        laatste_temp, laatste_vocht = dht11.lees()
        break
    except Exception:
        time.sleep(2)
laatste_licht = ldr.lees()

# Kalibreer geluidssensor: meet ruisvloer en stel drempel dynamisch in
ruis_samples = [geluid.meet_amplitude() for _ in range(10)]
geluid_ruis = max(ruis_samples)
geluid_drempel = max(GELUID_DREMPEL, geluid_ruis + 1000)
print("Geluid ruisvloer:", geluid_ruis, "Drempel:", geluid_drempel)
supabase.insert("events", {"type": "geluid_kalibratie", "payload": {"ruisvloer": geluid_ruis, "drempel": geluid_drempel}})

lcd.toon(str(laatste_temp) + "C " + str(laatste_vocht) + "%", "OTA v2 gestart")
print("Nexus gestart")

laatste_sensor_log = time.ticks_ms()
laatste_command_poll = time.ticks_ms()
laatste_lcd_update = time.ticks_ms()
beweging_actief = False
laatste_beweging = time.ticks_ms()
laatste_event = "-"
temp_alert_actief = False
geluid_actief = False
laatste_geluid = time.ticks_ms()
lcd_scherm = 0
laatste_p1 = time.ticks_ms()
laatste_p1_fout = time.ticks_ms() - P1_FOUT_STIL_MS  # eerste fout mag meteen gelogd worden
p1_buffer = []

# Reset website-toestand bij herstart
supabase.insert("events", {"type": "motion_absent"})
supabase.insert("events", {"type": "sound_absent"})

def verwerk_beweging():
    global beweging_actief, laatste_beweging, laatste_event
    nu = time.ticks_ms()
    afstand = sonar.meet_afstand()
    if afstand is not None:
        beweging = (baseline_afstand - afstand) > BEWEGING_DELTA
        if beweging:
            laatste_beweging = nu
            if not beweging_actief:
                beweging_actief = True
                laatste_event = "Beweging!"
                print("Event: motion_detected, afstand:", round(afstand, 1))
                supabase.insert("events", {"type": "motion_detected", "payload": {"afstand_cm": round(afstand, 1)}})
                if settings["pushover_enabled"]:
                    if pushover("Beweging gedetecteerd (" + str(round(afstand, 1)) + " cm)"):
                        supabase.insert("events", {"type": "pushover_sent", "payload": {"bericht": "Beweging gedetecteerd"}})
    if beweging_actief and time.ticks_diff(nu, laatste_beweging) > AFWEZIG_NA * 1000:
        beweging_actief = False
        laatste_event = "Geen beweging"
        print("Event: motion_absent")
        supabase.insert("events", {"type": "motion_absent"})


def verwerk_geluid():
    global geluid_actief, laatste_event, laatste_geluid, geluid_drempel
    nu = time.ticks_ms()
    amplitude = geluid.meet_amplitude()
    if amplitude > geluid_drempel:
        if not geluid_actief:
            geluid_actief = True
            laatste_event = "Geluid!"
            print("Event: sound_detected, amplitude:", amplitude)
            supabase.insert("events", {"type": "sound_detected", "payload": {"amplitude": amplitude}})
        laatste_geluid = time.ticks_ms()  # reset na insert zodat debounce daarna begint
    elif geluid_actief and time.ticks_diff(nu, laatste_geluid) > GELUID_AFWEZIG_NA * 1000:
        geluid_actief = False
        laatste_event = "Geen geluid"
        print("Event: sound_absent")
        supabase.insert("events", {"type": "sound_absent"})


def verwerk_p1():
    """Sampelt de slimme meter en bewaart hem in RAM. Schrijft geen meting weg.

    Een mislukte lezing wordt wel gelogd, maar hooguit eens per P1_FOUT_STIL_MS: zonder die
    rem zou een onbereikbare meter de events-tabel volschrijven met dezelfde regel.
    """
    global laatste_p1, laatste_p1_fout
    if time.ticks_diff(time.ticks_ms(), laatste_p1) < P1_SAMPLE_MS:
        return
    laatste_p1 = time.ticks_ms()
    meting, fout = lees_p1()
    if fout is not None:
        if time.ticks_diff(time.ticks_ms(), laatste_p1_fout) > P1_FOUT_STIL_MS:
            laatste_p1_fout = time.ticks_ms()
            supabase.insert("events", {"type": "p1_fout", "payload": {"host": P1_HOST, "fout": fout[:200]}})
        return
    if len(p1_buffer) >= P1_BUFFER_MAX:
        p1_buffer.pop(0)
    p1_buffer.append((time.ticks_ms(), meting))


def flush_p1():
    """Schrijft de gebufferde samples in een call weg via energy_ingest.

    De Pico heeft geen kloksynchronisatie, dus elk sample draagt zijn ouderdom in ms en
    de database rekent dat om naar een tijdstempel. Bij een mislukte call blijft de buffer
    staan - anders was de meting weg terwijl de volgende cyclus hem alsnog had kunnen
    plaatsen.
    """
    if not p1_buffer:
        return
    nu = time.ticks_ms()
    samples = []
    for gemeten_op, meting in p1_buffer:
        sample = {"age_ms": time.ticks_diff(nu, gemeten_op)}
        sample.update(meting)
        samples.append(sample)

    # return=minimal geeft een lege body bij succes, dus toetsen op None en niet op waarheid.
    if supabase.rpc("energy_ingest", {"samples": samples}) is not None:
        print("P1:", len(samples), "samples weggeschreven")
        del p1_buffer[:]  # niet .clear(): del werkt op elke MicroPython-build
    else:
        print("P1: flush mislukt,", len(samples), "samples blijven in de buffer")


def verwerk_commands():
    global laatste_command_poll, poll_interval, settings, laatste_lcd_update
    if time.ticks_diff(time.ticks_ms(), laatste_command_poll) < 3000:
        return
    for cmd in supabase.get_pending_commands():
        type_ = cmd.get("command")
        payload = cmd.get("payload") or {}
        if type_ == "display_message":
            lcd.toon(payload.get("regel1", ""), payload.get("regel2", ""))
            watchdog.sleep(3)
        elif type_ == "buzzer":
            buzzer.piep(payload.get("freq", 880), payload.get("duur_ms", 200))
        elif type_ == "fan_on":
            ventilator.aan()
            lcd.toon("Ventilator", "AAN")
            watchdog.sleep(2)
        elif type_ == "fan_off":
            ventilator.uit()
            lcd.toon("Ventilator", "UIT")
            watchdog.sleep(2)
        elif type_ == "mood_alert":
            naam = payload.get("naam", "")
            tekst = payload.get("tekst", "")
            mood = payload.get("mood", "")
            if mood == "fijn":
                buzzer.piep(523, 200)
                time.sleep_ms(80)
                buzzer.piep(659, 200)
                time.sleep_ms(80)
                buzzer.piep(784, 400)
            else:
                buzzer.piep(784, 200)
                time.sleep_ms(80)
                buzzer.piep(523, 200)
                time.sleep_ms(80)
                buzzer.piep(392, 500)
            lcd.toon((naam + ": " + mood)[:16], tekst[:16])
            watchdog.sleep(10)
            laatste_lcd_update = time.ticks_ms()
        elif type_ == "ota_update":
            lcd.toon("Software update", "bezig...")
            import ota
            ota.check_en_update(supabase)
            lcd.toon("OTA: actueel", "geen update")
            time.sleep(2)
        elif type_ == "notify":
            if settings["pushover_enabled"]:
                bericht = payload.get("bericht", "")
                if pushover(bericht, payload.get("titel", "Nexus")):
                    supabase.insert("events", {"type": "pushover_sent", "payload": {"bericht": bericht}})
        elif type_ == "set_setting":
            settings = laad_settings()
            poll_interval = settings["poll_interval_s"]
            lcd.set_backlight(settings["lcd_backlight"])
            print("Settings herladen: poll_interval_s =", poll_interval)
        supabase.mark_executed(cmd["id"])
    laatste_command_poll = time.ticks_ms()


def log_crash(e):
    """Schrijf de traceback naar Supabase. Zonder dit sterft een exception onzichtbaar."""
    buf = io.StringIO()
    sys.print_exception(e, buf)
    tb = buf.getvalue()
    print("CRASH:", tb)
    supabase.insert("events", {"type": "crash", "payload": {"traceback": tb[:1500]}})


# Pas hier wapenen, niet vóór de bootsequentie: die duurt langer dan de watchdog-marge.
# Boot kan niet meer eeuwig hangen omdat elke netwerkcall een timeout heeft.
wdt_actief = watchdog.wapen()

# Boot-event met reset-oorzaak: 3 = WDT_RESET betekent dat de watchdog een hang heeft
# opgeruimd, 1 = PWRON_RESET is een stroomonderbreking. Zonder dit is na een incident
# niet vast te stellen waarom het bord opnieuw is gestart.
supabase.insert("events", {"type": "boot", "payload": {
    "reset_cause": machine.reset_cause(),
    "wdt": wdt_actief,
    "ip": wlan.ifconfig()[0],
    "p1_host": P1_HOST,
}})

while True:
    watchdog.leef()
    try:
        nu = time.ticks_ms()

        verwerk_beweging()
        verwerk_geluid()
        verwerk_p1()

        # Sensor logging elke POLL_INTERVAL seconden
        if time.ticks_diff(nu, laatste_sensor_log) >= poll_interval * 1000:
            herverbind_indien_nodig()
            try:
                laatste_temp, laatste_vocht = dht11.lees()
            except Exception:
                watchdog.sleep(2)
                try:
                    laatste_temp, laatste_vocht = dht11.lees()
                except Exception:
                    print("DHT11 fout, gebruik laatste waarde")
            laatste_licht = ldr.lees()
            print("Temp:", laatste_temp, "Vocht:", laatste_vocht, "Licht:", laatste_licht)
            # Eén call voor drie rijen: PostgREST accepteert een array als body. Elke call
            # is een eigen TLS-handshake (0,6-13 s), dus dit scheelt twee handshakes per
            # cyclus. Het interleaven van commands tussen de inserts is daarmee overbodig:
            # dat bestond alleen omdat drie losse inserts de loop ~30 s blokkeerden.
            supabase.insert("sensor_readings", [
                {"sensor": "dht11_temp", "value": laatste_temp},
                {"sensor": "dht11_humidity", "value": laatste_vocht},
                {"sensor": "ldr_light", "value": laatste_licht},
            ])
            verwerk_commands()
            verwerk_beweging()
            verwerk_geluid()
            verwerk_p1()  # nog even sampelen: de calls hierboven blokkeerden seconden
            flush_p1()
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
                r1 = str(laatste_temp) + "C " + str(laatste_vocht) + "% L:" + str(laatste_licht)
                r2 = "Geluid: " + ("JA!" if geluid_actief else "nee")
            else:
                r1 = "Beweging: " + ("JA!" if beweging_actief else "nee")
                r2 = laatste_event
            lcd.toon(r1, r2)
            lcd_scherm = 1 - lcd_scherm
            laatste_lcd_update = time.ticks_ms()

        time.sleep_ms(100)
    except Exception as e:
        log_crash(e)
        watchdog.sleep(5)
