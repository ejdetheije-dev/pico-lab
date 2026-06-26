import urequests
import ujson
import os
import machine
import time

BASE_URL = "https://raw.githubusercontent.com/ejdetheije-dev/pico-lab/main/experiments/06_nexus/"
LOCAL_VERSION_PAD = "version.txt"
NIET_UPDATEN = {"config.py"}


def _lees_versie():
    try:
        with open(LOCAL_VERSION_PAD) as f:
            return f.read().strip()
    except OSError:
        return "0"


def _download(url):
    """Download URL, gooit OSError bij HTTP-fout of netwerkfout. Eén retry."""
    for poging in range(2):
        try:
            r = urequests.get(url)
            if r.status_code != 200:
                r.close()
                raise OSError("HTTP " + str(r.status_code))
            data = r.content
            r.close()
            return data
        except OSError:
            if poging == 0:
                time.sleep_ms(500)
            else:
                raise


def _maak_map(pad):
    if "/" in pad:
        map_naam = pad.rsplit("/", 1)[0]
        try:
            os.mkdir(map_naam)
        except OSError:
            pass


def check_en_update(supabase_module):
    """Vergelijk versie met GitHub. Download en installeer nieuwe bestanden indien nodig."""
    print("OTA: versie controleren...")
    try:
        remote_versie = _download(BASE_URL + "ota/version.txt").decode().strip()
    except Exception as e:
        print("OTA: versie ophalen mislukt:", e)
        supabase_module.insert("events", {"type": "ota_mislukt", "payload": {"stap": "versie", "fout": str(e)}})
        return

    lokale_versie = _lees_versie()
    print("OTA: lokaal =", lokale_versie, "/ remote =", remote_versie)

    if remote_versie <= lokale_versie:
        print("OTA: al up-to-date")
        supabase_module.insert("events", {"type": "ota_actueel", "payload": {"versie": lokale_versie}})
        return

    supabase_module.insert("events", {"type": "ota_gestart", "payload": {"van": lokale_versie, "naar": remote_versie}})

    try:
        manifest = ujson.loads(_download(BASE_URL + "ota/manifest.json"))
    except Exception as e:
        print("OTA: manifest ophalen mislukt:", e)
        supabase_module.insert("events", {"type": "ota_mislukt", "payload": {"stap": "manifest", "fout": str(e)}})
        return

    for bestand in manifest:
        if bestand in NIET_UPDATEN:
            print("OTA: sla over:", bestand)
            continue
        print("OTA: download", bestand)
        try:
            data = _download(BASE_URL + bestand)
        except Exception as e:
            print("OTA: download mislukt:", bestand, e)
            supabase_module.insert("events", {"type": "ota_mislukt", "payload": {"stap": bestand, "fout": str(e)}})
            return

        tmp = bestand + ".tmp"
        _maak_map(bestand)
        with open(tmp, "wb") as f:
            f.write(data)
        try:
            os.remove(bestand)
        except OSError:
            pass
        os.rename(tmp, bestand)

    with open(LOCAL_VERSION_PAD, "w") as f:
        f.write(remote_versie)

    print("OTA: update geslaagd naar versie", remote_versie)
    supabase_module.insert("events", {"type": "ota_geslaagd", "payload": {"versie": remote_versie}})
    time.sleep(2)
    machine.reset()
