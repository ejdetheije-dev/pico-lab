"""Pushover push-notificaties via HTTPS API. Best-effort, geen retry."""

import urequests
import ujson
from config import PUSHOVER_TOKEN, PUSHOVER_USER

_URL = "https://api.pushover.net/1/messages.json"
_HEADERS = {"Content-Type": "application/json"}


def stuur(bericht, titel="Nexus"):
    """Stuur een push-notificatie. Fouten worden gelogd maar niet doorgegeven."""
    try:
        r = urequests.post(
            _URL,
            headers=_HEADERS,
            data=ujson.dumps({
                "token": PUSHOVER_TOKEN,
                "user": PUSHOVER_USER,
                "title": titel,
                "message": bericht,
            }),
        )
        r.close()
        print("Pushover verstuurd:", bericht)
    except Exception as e:
        print("Pushover fout:", e)
