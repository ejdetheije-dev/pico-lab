import urequests
import ujson
from config import SUPABASE_URL, SUPABASE_KEY

_headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": "Bearer " + SUPABASE_KEY,
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}


def insert(table, data):
    """Voeg een rij in aan de opgegeven tabel."""
    r = urequests.post(
        SUPABASE_URL + "/rest/v1/" + table,
        headers=_headers,
        data=ujson.dumps(data),
    )
    r.close()


def get_pending_commands():
    """Haal niet-uitgevoerde commands op (executed_at is null)."""
    r = urequests.get(
        SUPABASE_URL + "/rest/v1/commands?executed_at=is.null&order=id.asc",
        headers=_headers,
    )
    result = r.json()
    r.close()
    return result


def mark_executed(command_id):
    """Zet executed_at op het huidige tijdstip voor een command."""
    headers = dict(_headers)
    headers["Prefer"] = "return=minimal"
    r = urequests.patch(
        SUPABASE_URL + "/rest/v1/commands?id=eq." + str(command_id),
        headers=headers,
        data=ujson.dumps({"executed_at": "now()"}),
    )
    r.close()
