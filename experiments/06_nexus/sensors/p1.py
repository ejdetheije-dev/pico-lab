"""HomeWizard P1: leest de slimme meter via de lokale v1-API.

Plain HTTP op het LAN, geen auth en geen TLS - daarmee is dit de goedkoopste call in de
hele loop, en kan er dus veel vaker gesampeld worden dan er geschreven wordt.

De meter geeft CUMULATIEVE standen. Dat is het hele punt: na een gat zijn de totalen over
dat gat nog exact bekend en is alleen de resolutie erbinnen weg.

Waarom een ruwe socket en niet urequests: op /api/v1/data antwoordt de meter urequests met
HTTP 408 (gemeten 2026-08-01), terwijl /api en de gateway wel 200 geven en een laptop het
endpoint honderden keren zonder klacht bevraagt. Een request dat in EEN write de deur uit
gaat werkt wel. Verder is urequests hier overkill: geen TLS, geen redirects, geen chunked
encoding - de meter stuurt een nette Content-Length.
"""

import config
import ujson
import usocket
import watchdog

# Geen `from config import P1_HOST`: OTA werkt config.py bewust nooit bij, dus een nieuwe
# sleutel bestaat niet op een bord dat via OTA is bijgewerkt. Dat zou de import laten falen,
# main.py niet laten starten en de watchdog nooit laten wapenen - een dood bord tot je er met
# USB bij kunt. Met een default hier landt de update gewoon en kan config.py later bij.
P1_HOST = getattr(config, "P1_HOST", "192.168.178.190")

# Gemeten vanaf een laptop: 100-460 ms per call. Vijf seconden is ruim, en langer wachten
# heeft geen zin - dan is de meter weg.
TIMEOUT = 5


def _haal(pad):
    """Doet een HTTP/1.0 GET met het hele request in een write. Geeft de body als bytes."""
    adres = usocket.getaddrinfo(P1_HOST, 80)[0][-1]
    s = usocket.socket()
    s.settimeout(TIMEOUT)
    try:
        s.connect(adres)
        s.write(b"GET " + pad + b" HTTP/1.0\r\nHost: " + P1_HOST.encode() + b"\r\n\r\n")
        antwoord = b""
        while True:
            brok = s.read(512)
            if not brok:
                break
            antwoord += brok
    finally:
        s.close()

    scheiding = antwoord.find(b"\r\n\r\n")
    if scheiding < 0:
        raise ValueError("geen headereinde in antwoord")
    kop = antwoord[:scheiding]
    if b" 200 " not in kop.split(b"\r\n")[0]:
        raise ValueError(kop.split(b"\r\n")[0].decode())
    return antwoord[scheiding + 4:]


def lees():
    """Geeft (meting, fout). Bij succes is fout None, bij mislukking is meting None.

    De foutmelding komt terug in plaats van alleen een print, omdat de Pico normaal niet aan
    USB hangt: zonder dit is een onbereikbare meter volledig onzichtbaar vanaf de buitenkant.

    De sleutels zijn die van het energy_ingest-contract, niet die van de P1: de omzetting
    hoort hier, zodat main.py niets van het JSON-formaat van HomeWizard hoeft te weten.
    """
    watchdog.feed()
    try:
        d = ujson.loads(_haal(b"/api/v1/data"))
    except Exception as e:
        print("p1 fout:", e)
        return None, str(e) or repr(e)

    return {
        "active_tariff": d["active_tariff"],
        "import_t1": d["total_power_import_t1_kwh"],
        "import_t2": d["total_power_import_t2_kwh"],
        "export_t1": d["total_power_export_t1_kwh"],
        "export_t2": d["total_power_export_t2_kwh"],
        "gas": d["total_gas_m3"],
        "power_w": d["active_power_w"],
        "l1_w": d["active_power_l1_w"],
        "l2_w": d["active_power_l2_w"],
        "l3_w": d["active_power_l3_w"],
    }, None
