# Plan — experimentenoverzicht

Vijf experimenten van makkelijk naar complex. Eerst sensor uitlezen, daarna
combineren, ten slotte sensor + actuator als regelkring.

## Status (2026-07-27) — experiment 06 Nexus actief, loop herstelt zichzelf

| Experiment             | Code | Bedraad | Getest | Jira      |
|------------------------|------|---------|--------|-----------|
| 01 weerstation         | ja   | nee     | ja     | PICO-10   |
| 02 reactiemeting       | ja   | nee     | nee    | PICO-3    |
| 03 sonar               | ja   | nee     | nee    | PICO-4    |
| 04 servo-wijzer        | ja   | nee     | nee    | PICO-5    |
| 05 solar tracker       | ja   | nee     | ja     | PICO-22   |
| 06 nexus               | ja   | ja      | ja     | PICO-25   |

Pico 2W op **COM10** (het poortnummer verschuift bij opnieuw inpluggen — detecteer
met `mpremote connect list`, zoek VID `2e8a:`). Nexus draait op Freenove breakout
board (opstelling B), 7/7 componenten werkend. Nexus-web gedeployed op Vercel:
https://nexus-ejdetheije.vercel.app. Automatisch deploy via GitHub Actions
bij push naar main. Repo is **publiek** (vereist voor OTA raw.githubusercontent.com).
PICO-48 (OTA) afgerond. Eén openstaande PICO-taak: **PICO-49** (Pushover per trigger
schakelbaar, aangemaakt 2026-07-28).

**Zelfherstel toegevoegd (2026-07-27, commits `ac40ad3`, `8a621a8`, `9117dab`):**

De loop stopte elke 9 uur tot 2,5 dag en kwam er nooit zelf uit. Bewijs: de
`geluid_kalibratie`-events (één per boot) vielen 1:1 samen met elke run-start in
`sensor_readings`, dus **geen enkele zelf-herstart in de hele historie** — elke
herstart was handmatig. De site sprong daardoor op "Offline"; die badge is puur
afgeleid van de versheid van de nieuwste rij (`Dashboard.tsx`), geen website-status.

- Nieuw `watchdog.py`: timer-gevoede WDT met expliciete deadline (`MARGE_S = 45`).
- `timeout=15` op elke urequests-call in `supabase.py` en `ota.py`.
- Top-level `try/except` om de loop-body → traceback naar `events.type='crash'`.
- `boot`-event per start met `reset_cause` en `wdt`.
- `watchdog.py` als eerste in `ota/manifest.json`; OTA-versie `20260727002`.

Onderweg ingeperkt: alle drie de sensoren zijn hard begrensd en vallen af als
oorzaak; wat overblijft is de netwerkgrens, met `get_pending_commands()` op
~28.800 calls per dag als hoofdverdachte. **De oorspronkelijke oorzaak is nog niet
bekend** — de crash-logging moet die bij de volgende keer opleveren.

Valkuilen en de bewezen getallen staan in CLAUDE.md, sectie "Betrouwbaarheid van de
Nexus-loop". Kort: `timeout=` begrenst niet de totale call-duur, WDT-max is 8388 ms,
en een soft-IRQ blijft lopen tijdens een blokkerende socket-read.

**Openstaand na deze fix:** (a) of het bord het dágen volhoudt is nog niet aangetoond —
kijk naar de `boot`-events; (b) waarom de TLS-handshake 6-13 s duurt is nooit onderzocht,
en dat maakt de effectieve logcyclus ~78 s in plaats van 60 s; (c) een dead-man's switch
die meldt als er N minuten geen rij is; (d) direct navigeren naar een subpagina van
nexus-web geeft een Vercel 404 — er mist een SPA-rewrite naar `index.html`.

**PICO-22 afgerond** (experiment 05 solar tracker, Jira-status Gereed):

- Servo SG90 op GPIO 8 (GPIO 7 had slechte breadboard-verbinding).
- LDR links op GPIO 28, LDR rechts op GPIO 26 (gedeeld met weerstation).
- 1kΩ weerstanden (10kΩ verzadigt bij fel licht).
- Opstartskalibratie meet nulpuntverschil tussen de twee LDR's.
- DREMPEL = 300 (1500 reageerde niet op lamplicht).

**Valkuilen die bewezen zijn (zie ook CLAUDE.md):**
- Breadboard middengroef: jumper en Pico-pin altijd aan dezelfde kant.
- RP2350 ADC offset: ~3000 raw bij GND is normaal.
- 10kΩ verzadigt bij fel licht; 1kΩ + remapping werkt beter.
- LDR-kalibratie verschuift bij het inkorten/verplaatsen van draden.
- GPIO-rij defect: als pin niet reageert, probeer buurpin.
- Servo dupont-connector: altijd controleren op losse pin bij geen respons.
- Twee LDR's op verschillende posities lezen ongelijk → offset-kalibratie.
- mpremote run stopt snel → gebruik `cp :main.py` + `mpremote` voor persistent script.

Weerstanden in kit: 1kΩ, 10kΩ en 220Ω bevestigd aanwezig.

**Gepland na 2026-06-25 — drukmeting toevoegen aan experiment 01:**

GY-BME280 en GY-BMP280 worden op 2026-06-25 geleverd. Na ontvangst:
- Sensor aansluiten op I2C0 (SDA=GPIO 0, SCL=GPIO 1), zelfde bus als LCD.
- BME280 → vervangt DHT11 (temp + vocht + druk). BMP280 → DHT11 blijft
  voor vochtigheid, BMP280 voegt druk toe. Keuze afhankelijk van wat werkt.
- Nieuwe module `shared/bme280.py` schrijven.
- `main.py` en CSV uitbreiden met `druk_hpa`.

Stappenplan voor de bring-up: zie [`bring_up_plan.md`](bring_up_plan.md).

Issue tracker: Jira project **`PICO`** op
[ejdetheije.atlassian.net](https://ejdetheije.atlassian.net/browse/PICO-1).
6 Epics + 18 starter-Taken. Volgend ticket: PICO-11 (experiment 02
reactiemeting).

## Volgorde-advies

1. `01_weerstation` — leer DHT11 uitlezen en LCD aansturen
2. `02_reactiemeting` — leer timing en input handling
3. `03_sonar` — leer afstand meten en visualiseren met RGB LED
4. `04_servo_wijzer` — eerste actuator-experiment (PWM, servo)
5. `05_solar_tracker` — sensor + actuator regelkring
6. `06_nexus` — WiFi, Supabase, React-dashboard; board wordt leeggemaakt

## Experiment 01 — Weerstation

- **Leerdoel:** DHT11 uitlezen, LCD 1602 via I2C aansturen, CSV loggen.
- **Hardware:** Pico 2W, DHT11, LCD 1602 (I2C), breadboard, jumpers.
- **Bouwtijd:** ~30 min.
- **Wetenschappelijke vraag:** Hoe ontwikkelt temperatuur en luchtvochtigheid
  zich in een kamer over een uur?

## Experiment 02 — Reactiemeting

- **Leerdoel:** Random timing, externe knop met debouncing, statistiek over
  meerdere metingen.
- **Hardware:** Pico 2W, LED, drukknop, weerstand 220Ω, breadboard.
- **Bouwtijd:** ~30 min.
- **Wetenschappelijke vraag:** Wat is mijn gemiddelde reactietijd, en hoe
  consistent ben ik (standaarddeviatie)?

## Experiment 03 — Sonar

- **Leerdoel:** HC-SR04 timing meten in microseconden, drempelwaarden vertalen
  naar visuele output.
- **Hardware:** Pico 2W, HC-SR04, RGB LED, 3x 220Ω weerstand, breadboard.
- **Bouwtijd:** ~40 min.
- **Wetenschappelijke vraag:** Vanaf welke afstand wordt de meting onbetrouwbaar
  en wat is de minimale en maximale meetafstand?

## Experiment 04 — Servo wijzer

- **Leerdoel:** PWM-aansturing van servo, mapping van sensorwaarde naar
  actuatorpositie.
- **Hardware:** Pico 2W, DHT11, SG90 servo, breadboard. Servo VCC op VBUS.
- **Bouwtijd:** ~40 min.
- **Wetenschappelijke vraag:** Hoe vertaal je een continue meting (temperatuur)
  vloeiend naar een mechanische uitslag zonder trillen?

## Experiment 05 — Solar tracker

- **Leerdoel:** Twee analoge sensoren vergelijken, gesloten regelkring,
  hysterese om jitter te voorkomen.
- **Hardware:** Pico 2W, 2x LDR, 2x 1kΩ weerstand, SG90 servo, breadboard.
- **Bouwtijd:** ~60 min.
- **Wetenschappelijke vraag:** Hoe snel kan de servo het lichtste punt volgen,
  en wat is de minimale lichtverschil-drempel waarop hij betrouwbaar reageert?

## Experiment 06 — Nexus

- **Concept:** Permanente hub die continu meet en op afstand bedienbaar is.
  Kernpatroon: Pico → Supabase → React-website en terug.
- **Hardware:** Pico 2W, DHT11, LDR, HC-SR04, geluidssensor, IR ontvanger,
  LCD 1602, buzzer. Board wordt leeggemaakt voor de start.
- **Stack:** MicroPython op Pico · Supabase (Postgres + REST) · Vite + React
  + TypeScript + Tailwind · Vercel/Netlify deployment.
- **Credentials:** `config.py` gitignored, `config.example.py` gecommit.

### Fase 0 — Infrastructuur (Jira PICO-26/27/28)

- [x] PICO-26: Supabase project aanmaken + tabellen aanleggen
- [x] PICO-27: Projectmapstructuur aanmaken + config.py inrichten
- [x] PICO-28: Pico WiFi + HTTP POST naar Supabase valideren

### Fase 1 — MVP Pico (Jira PICO-29/30/31/32)

- [x] PICO-29: `supabase.py` HTTP wrapper schrijven (POST en GET)
- [x] PICO-30: Hardware bouwen: board leegmaken + Nexus bedraden
- [x] PICO-31: DHT11 periodiek loggen naar `sensor_readings`
- [x] PICO-32: HC-SR04 bewegingsdetectie naar `events` + LCD toont event

### Fase 1 — MVP Website (Jira PICO-33/34)

- [x] PICO-33: `nexus-web/` opzetten: Vite + React + TypeScript + Tailwind
- [x] PICO-34: Dashboard: live sensorwaarden via Supabase

### Fase 2 (Jira PICO-35/36/37)

- [ ] PICO-35: Geluidssensor event detectie (overgeslagen — sensor niet gevonden)
- [x] PICO-36: Commands queue: `display_message` + `buzzer` vanuit website
- [x] PICO-37: Settings: poll interval instelbaar via website

### Fase 3 (Jira PICO-38/39/40/41/42/43/44/45/46/47/48)

- [ ] PICO-38: IR bediening + LCD menu
- [x] PICO-39: BMP180 drukmeting geïntegreerd in Nexus
- [x] PICO-40: Website: grafieken + event log met filtering
- [x] PICO-42: MAX4466 geluidssensor geïntegreerd (KY-038 defect)
- [x] PICO-43: 4-kanaals relaismodule + 12V ventilator via website
- [x] PICO-44: Pushover notificaties
- [x] PICO-45: Mood switch (naam + code + humeur → buzzer + LCD)
- [ ] PICO-46: Adafruit TTL Camera (arriveert 2026-06-25)
- [x] PICO-47: Data retentie via pg_cron (365 dagen)
- [x] PICO-48: OTA software update via WiFi (GitHub raw URLs, manifest.json)
- [ ] PICO-49: Pushover per trigger schakelbaar (zie "Openstaande verbeteringen")

---

## Openstaande verbeteringen (later oppakken)

- **PICO-49: Pushover per trigger schakelbaar maken (gevraagd 2026-07-28).** Nu is
  `settings["pushover_enabled"]` één globale vlag: hij schakelt de bewegingsmelding, de
  temperatuurdrempel én het `notify`-commando tegelijk. Dat botst met het gebruik vanuit
  ElectriciteitsHuishouding, waar een dagelijkse `pg_cron`-job een `notify`-rij in `commands`
  schrijft als de database richting 300/400 MB groeit. Gewenst: **database-alarmen komen altijd
  door, lokale triggers apart onderdrukbaar.**

  Aanleiding: op 2026-07-28 is het `notify`-pad voor het eerst end-to-end getest (commando 203 →
  `pushover_sent` om 14:36:51Z, werkt). Maar het aanzetten van de vlag leverde binnen een minuut
  ook een "Beweging gedetecteerd"-push op, en die zijn niet gewenst. De vlag staat daarom weer op
  `false` — waarmee het budgetalarm van dat project stil staat tot dit opgelost is.

  Schets: de `notify`-tak in `experiments/06_nexus/main.py:199-203` loskoppelen van
  `pushover_enabled` en die vlag alleen nog op de lokale triggers laten gelden; eventueel een
  tweede setting (`pushover_lokale_triggers`) zodat beide kanten los schakelbaar zijn en de
  Settings-pagina twee toggles krijgt. Let op: settings worden in RAM gecachet en alleen op een
  `set_setting`-commando herladen (`main.py:204-206`), dus een DB-patch alleen is niet genoeg.
  Vraagt `mpremote` of OTA, en elke deploy onderbreekt de loop.

- **Automatische CSV-sync:** `mpremote mount` koppelt een lokale map als
  filesystem aan de Pico zodat data direct op de laptop schrijft. Vereist
  analyse van padconflict: `data/weerstation.csv` (Pico-upload) vs.
  `experiments/01_weerstation/data/weerstation.csv` (mount vanuit projectroot).
  Mogelijk oplossing: `tools/run_live.ps1` + pad als constante in `main.py`.

## Toekomstige experimenten

Ideeën die voortbouwen op de aanwezige hardware:

1. **RFID toegangscontrole** — RC522 leest kaarten, servo opent een
   "deur" (klepje), buzzer geeft feedback, LCD toont status.
2. **Kantelalarm** — Kantelschakelaar triggert buzzer en RGB LED, met
   instelbare gevoeligheid via joystick.
3. **IR-bestuurde RGB lamp** — IR ontvanger leest afstandsbedieningscodes,
   RGB LED past kleur en helderheid aan.
4. **Geluidsreactieve LED-meter** — Geluidsensor (analoog) stuurt de
   intensiteit van RGB LED en cijfer op 7-segment display.
5. **Stappenmotor klok** — Stappenmotor draait één omwenteling per uur,
   LCD toont tijd via WiFi-NTP-sync.
