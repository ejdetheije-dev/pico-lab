import urequests
import ujson
import time
import watchdog
from config import SUPABASE_URL, SUPABASE_KEY

# Ruim boven de gemeten latency (0,6-13 s) en ruim onder watchdog.MARGE_S, zodat
# een hangende socket via een exception herstelt in plaats van via een board-reset.
TIMEOUT = 15

_auth = {
    "apikey": SUPABASE_KEY,
    "Authorization": "Bearer " + SUPABASE_KEY,
    "Connection": "close",
}

_write_headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": "Bearer " + SUPABASE_KEY,
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
    "Connection": "close",
}


def _vraag(methode, url, data=None):
    """HTTP-call met timeout en één retry. Geeft de body terug, raist bij twee mislukkingen.

    Vangt Exception, niet alleen OSError: zonder timeout hing een socket-read eeuwig
    en een niet-JSON body gaf een fatale ValueError. Meldt voortgang aan de watchdog
    per poging, zodat een reeks trage calls geen reset uitlokt.
    """
    for poging in range(2):
        watchdog.feed()
        try:
            if methode == "GET":
                r = urequests.get(url, headers=_auth, timeout=TIMEOUT)
            elif methode == "POST":
                r = urequests.post(url, headers=_write_headers, data=data, timeout=TIMEOUT)
            else:
                r = urequests.patch(url, headers=_write_headers, data=data, timeout=TIMEOUT)
            inhoud = r.content
            r.close()
            watchdog.feed()
            return inhoud
        except Exception:
            watchdog.feed()
            if poging == 0:
                time.sleep_ms(500)
            else:
                raise


def insert(table, data):
    """Voeg een rij in aan de opgegeven tabel."""
    try:
        _vraag("POST", SUPABASE_URL + "/rest/v1/" + table, ujson.dumps(data))
    except Exception as e:
        print("insert fout:", table, e)


def get_pending_commands():
    """Haal niet-uitgevoerde commands op (executed_at is null). Lege lijst bij fout."""
    try:
        body = _vraag("GET", SUPABASE_URL + "/rest/v1/commands?executed_at=is.null&order=id.asc")
        return ujson.loads(body)
    except Exception as e:
        print("get_pending_commands fout:", e)
        return []


def get_settings():
    """Haal settings op als dict {key: value}. Geeft lege dict bij fout."""
    try:
        body = _vraag("GET", SUPABASE_URL + "/rest/v1/settings?select=key,value")
        return {row["key"]: row["value"] for row in ujson.loads(body)}
    except Exception as e:
        print("get_settings fout:", e)
        return {}


def mark_executed(command_id):
    """Zet executed_at op het huidige tijdstip voor een command."""
    try:
        _vraag(
            "PATCH",
            SUPABASE_URL + "/rest/v1/commands?id=eq." + str(command_id),
            ujson.dumps({"executed_at": "now"}),
        )
    except Exception as e:
        print("mark_executed fout:", e)
