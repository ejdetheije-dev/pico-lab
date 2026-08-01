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
import time
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
    """Doet een HTTP GET en geeft de body als bytes.

    Leest exact Content-Length bytes in plaats van tot de verbinding sluit. Dat is hier geen
    detail maar de kern: de meter antwoordt met HTTP/1.1 en houdt de verbinding open, dus
    "lezen tot EOF" blijft hangen op de laatste brok. Gemeten 2026-08-01: precies 1024 bytes
    binnen (twee reads van 512) en dan ETIMEDOUT, terwijl het antwoord ~1240 bytes is. Het
    kleine /api-endpoint viel binnen een enkele read en werkte daardoor wel - vandaar dat het
    op een netwerkprobleem leek. `Connection: close` staat erbij zodat de meter zelf afsluit.
    """
    adres = usocket.getaddrinfo(P1_HOST, 80)[0][-1]
    s = usocket.socket()
    s.settimeout(TIMEOUT)
    begin = time.ticks_ms()
    ontvangen = b""
    body = b""
    lengte = None
    try:
        s.connect(adres)
        s.write(
            b"GET " + pad + b" HTTP/1.1\r\nHost: " + P1_HOST.encode()
            + b"\r\nConnection: close\r\n\r\n"
        )
        # Eerst de headers compleet krijgen.
        while b"\r\n\r\n" not in ontvangen:
            brok = s.recv(512)
            if not brok:
                raise ValueError("verbinding dicht voor het einde van de headers")
            ontvangen += brok

        kop, _, body = ontvangen.partition(b"\r\n\r\n")
        statusregel = kop.split(b"\r\n")[0]
        if b" 200 " not in statusregel:
            raise ValueError(statusregel.decode())

        lengte = _kop_waarde(kop, b"content-length")
        if lengte is None:
            raise ValueError("geen Content-Length")
        while len(body) < lengte:
            brok = s.recv(512)
            if not brok:
                raise ValueError("body afgebroken op %d van %d bytes" % (len(body), lengte))
            body += brok
    except Exception as e:
        gelezen = len(ontvangen) if not body else len(kop) + 4 + len(body)
        raise ValueError("%s na %d bytes in %d ms" % (e, gelezen, time.ticks_diff(time.ticks_ms(), begin)))
    finally:
        s.close()

    return body[:lengte]


def _kop_waarde(kop, naam):
    """Waarde van een headerregel als int, of None. Hoofdletterongevoelig."""
    for regel in kop.split(b"\r\n")[1:]:
        veld, _, waarde = regel.partition(b":")
        if veld.strip().lower() == naam:
            return int(waarde.strip())
    return None


def proef():
    """Meet beide endpoints een keer en geeft per pad het aantal bytes of de fout.

    /api is klein (122 bytes) en werkt, /api/v1/data is groot (1120) en faalt. Ze naast
    elkaar meten laat zien of dat verschil aan de omvang ligt.
    """
    uitslag = {}
    for pad in (b"/api", b"/api/v1/data"):
        watchdog.feed()
        try:
            uitslag[pad.decode()] = "ok %d bytes" % len(_haal(pad))
        except Exception as e:
            uitslag[pad.decode()] = str(e) or repr(e)
    return uitslag


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
