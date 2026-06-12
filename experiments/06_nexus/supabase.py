import urequests
import ujson
import time
from config import SUPABASE_URL, SUPABASE_KEY

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
}


def _post(url, data):
    """POST met één retry na 500ms bij ECONNRESET."""
    for poging in range(2):
        try:
            r = urequests.post(url, headers=_write_headers, data=data)
            r.close()
            return
        except OSError:
            if poging == 0:
                time.sleep_ms(500)
            else:
                raise


def insert(table, data):
    """Voeg een rij in aan de opgegeven tabel."""
    try:
        _post(SUPABASE_URL + "/rest/v1/" + table, ujson.dumps(data))
    except OSError as e:
        print("insert fout:", table, e)


def get_pending_commands():
    """Haal niet-uitgevoerde commands op (executed_at is null)."""
    for poging in range(2):
        try:
            r = urequests.get(
                SUPABASE_URL + "/rest/v1/commands?executed_at=is.null&order=id.asc",
                headers=_auth,
            )
            data = r.content
            r.close()
            return ujson.loads(data)
        except OSError:
            if poging == 0:
                time.sleep_ms(500)
            else:
                print("get_pending_commands fout: twee pogingen mislukt")
                return []


def get_settings():
    """Haal settings op als dict {key: value}. Geeft lege dict bij fout."""
    for poging in range(2):
        try:
            r = urequests.get(
                SUPABASE_URL + "/rest/v1/settings?select=key,value",
                headers=_auth,
            )
            data = r.content
            r.close()
            return {row["key"]: row["value"] for row in ujson.loads(data)}
        except OSError:
            if poging == 0:
                time.sleep_ms(500)
            else:
                print("get_settings fout: twee pogingen mislukt")
                return {}


def mark_executed(command_id):
    """Zet executed_at op het huidige tijdstip voor een command."""
    try:
        r = urequests.patch(
            SUPABASE_URL + "/rest/v1/commands?id=eq." + str(command_id),
            headers=_write_headers,
            data=ujson.dumps({"executed_at": "now"}),
        )
        r.close()
    except OSError as e:
        print("mark_executed fout:", e)
