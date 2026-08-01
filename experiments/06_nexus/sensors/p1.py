"""HomeWizard P1: leest de slimme meter via de lokale v1-API.

Plain HTTP op het LAN, geen auth en geen TLS - daarmee is dit de goedkoopste call in de
hele loop, en kan er dus veel vaker gesampeld worden dan er geschreven wordt.

De meter geeft CUMULATIEVE standen. Dat is het hele punt: na een gat zijn de totalen over
dat gat nog exact bekend en is alleen de resolutie erbinnen weg.
"""

import ujson
import urequests
import watchdog
from config import P1_HOST

# Een LAN-call zonder TLS hoort in tientallen milliseconden klaar te zijn. Duurt het
# seconden, dan is de meter weg of het wifi slecht; dan is opgeven beter dan wachten.
TIMEOUT = 5


def lees():
    """Momentopname van de meter als dict, of None als de P1 niet antwoordt.

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
        return None

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
    }
