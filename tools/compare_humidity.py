"""Vergelijk DHT11 luchtvochtigheid (Nexus) met Open-Meteo buitenvochtigheid.

Eenmalig analysescript, geen onderdeel van de Pico-codebase.
"""

import bisect
from datetime import datetime, timezone

import requests

SUPABASE_URL = "https://xzmsrsuxnuiokonjavws.supabase.co"
SUPABASE_KEY = "sb_publishable_gwdUIpoOcge__KexKrYfbw_vpKyNZm9"
LAT, LON = 52.13, 4.45


def haal_sensor_metingen():
    metingen = []
    offset = 0
    pagina = 1000
    while True:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/sensor_readings",
            params={
                "select": "value,created_at",
                "sensor": "eq.dht11_humidity",
                "order": "created_at.asc",
                "limit": pagina,
                "offset": offset,
            },
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
            },
            timeout=30,
        )
        r.raise_for_status()
        rows = r.json()
        if not rows:
            break
        metingen.extend(rows)
        offset += pagina
        if len(rows) < pagina:
            break
    return metingen


def haal_open_meteo():
    r = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": LAT,
            "longitude": LON,
            "hourly": "relative_humidity_2m",
            "past_days": 16,
            "forecast_days": 1,
            "timezone": "UTC",
        },
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()["hourly"]
    tijden = [datetime.fromisoformat(t).replace(tzinfo=timezone.utc) for t in data["time"]]
    vocht = data["relative_humidity_2m"]
    return tijden, vocht


def dichtsbijzijnde_uur(tijden, doel):
    idx = bisect.bisect_left(tijden, doel)
    kandidaten = []
    if idx < len(tijden):
        kandidaten.append(idx)
    if idx > 0:
        kandidaten.append(idx - 1)
    return min(kandidaten, key=lambda i: abs((tijden[i] - doel).total_seconds()))


def main():
    metingen = haal_sensor_metingen()
    tijden, vocht = haal_open_meteo()

    verschillen = []
    for m in metingen:
        ts = datetime.fromisoformat(m["created_at"]).astimezone(timezone.utc)
        i = dichtsbijzijnde_uur(tijden, ts)
        if abs((tijden[i] - ts).total_seconds()) > 3600:
            continue
        verschillen.append(float(m["value"]) - vocht[i])

    n = len(verschillen)
    gem = sum(verschillen) / n
    gem_abs = sum(abs(v) for v in verschillen) / n
    mn, mx = min(verschillen), max(verschillen)

    print(f"Aantal Nexus-metingen (totaal):     {len(metingen)}")
    print(f"Aantal gematcht met Open-Meteo uur:  {n}")
    print(f"Gemiddeld verschil (Nexus - buiten): {gem:+.1f} procentpunt")
    print(f"Gemiddelde absolute afwijking:       {gem_abs:.1f} procentpunt")
    print(f"Min / max verschil:                  {mn:+.1f} / {mx:+.1f}")


if __name__ == "__main__":
    main()
