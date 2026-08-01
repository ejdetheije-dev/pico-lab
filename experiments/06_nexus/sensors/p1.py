"""HomeWizard P1: leest de slimme meter via de lokale v1-API.

Plain HTTP op het LAN, geen auth en geen TLS - daarmee is dit de goedkoopste call in de
hele loop, en kan er dus veel vaker gesampeld worden dan er geschreven wordt.

De meter geeft CUMULATIEVE standen. Dat is het hele punt: na een gat zijn de totalen over
dat gat nog exact bekend en is alleen de resolutie erbinnen weg.
"""

import config
import ujson
import urequests
import watchdog

# Geen `from config import P1_HOST`: OTA werkt config.py bewust nooit bij, dus een nieuwe
# sleutel bestaat niet op een bord dat via OTA is bijgewerkt. Dat zou de import laten falen,
# main.py niet laten starten en de watchdog nooit laten wapenen - een dood bord tot je er met
# USB bij kunt. Met een default hier landt de update gewoon en kan config.py later bij.
P1_HOST = getattr(config, "P1_HOST", "192.168.178.190")

# Een LAN-call zonder TLS hoort in tientallen milliseconden klaar te zijn. Toch dezelfde
# ruime grens als supabase.py: op 5 s gaf elke lezing ETIMEDOUT (gemeten 2026-08-01), en
# een te krappe timeout is niet te onderscheiden van een onbereikbare meter. Blijkt 15 s
# ook te weinig, dan is het geen traagheid maar routering.
TIMEOUT = 15


def lees():
    """Geeft (meting, fout). Bij succes is fout None, bij mislukking is meting None.

    De foutmelding komt terug in plaats van alleen een print, omdat de Pico normaal niet aan
    USB hangt: zonder dit is een onbereikbare meter volledig onzichtbaar vanaf de buitenkant.

    De sleutels zijn die van het energy_ingest-contract, niet die van de P1: de omzetting
    hoort hier, zodat main.py niets van het JSON-formaat van HomeWizard hoeft te weten.
    """
    watchdog.feed()
    try:
        r = urequests.get("http://" + P1_HOST + "/api/v1/data", timeout=TIMEOUT)
        inhoud = r.content  # eerst lezen, dan sluiten - anders lekt de socket bij een JSON-fout
        r.close()
        d = ujson.loads(inhoud)
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
