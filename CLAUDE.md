# Pico Lab — Claude instructies

## Projectoverzicht

Experimenteer-lab rond de Raspberry Pi Pico 2W. Doel: korte, afgebakende
experimenten waarin sensoren en actuatoren uit het Freenove Ultimate Starter
Kit op een breadboard worden gecombineerd. Code is MicroPython, draait direct
op de Pico, en wordt vanaf een Windows-laptop geupload via `mpremote`.

Iedere `experiments/NN_naam/` map staat op zichzelf: één duidelijk leerdoel,
één wetenschappelijke vraag, één `main.py` die werkt zodra je hem upload.

## Huidige status

Stand per 2026-06-13:

- **Nieuwe Pico 2W op COM9** met MicroPython (voorgeïnstalleerd uit de doos).
  Oude Pico (COM8) niet meer in gebruik voor Nexus.
- **Fase 0 afgerond:** PICO-7, PICO-8, PICO-9 (Gereed in Jira).
- **PICO-10 afgerond** (experiment 01 weerstation volledig werkend):
  - DHT11 op GPIO 16, kaal — `Pin.IN, Pin.PULL_UP` expliciet meegeven.
  - LCD 1602 op I2C0 (SDA=0, SCL=1, VCC=Vbus), adres `0x27`.
- **PICO-22 afgerond** (experiment 05 solar tracker werkend, 2026-06-05):
  - Servo SG90 op GPIO 8, LDR's op GPIO 26 en 28, DREMPEL = 300.
- **PICO-26 t/m PICO-32 afgerond** (experiment 06 Nexus MVP, 2026-06-06):
  - Supabase project `nexus` op `https://xzmsrsuxnuiokonjavws.supabase.co`.
  - Vier tabellen: `sensor_readings`, `events`, `commands`, `settings`.
  - Nexus breadboard: LCD (GPIO 0/1/Vbus), DHT11 (GPIO 16),
    HC-SR04 (GPIO 17/18), LDR (GPIO 26 + 1kΩ).
  - `experiments/06_nexus/main.py` draait: DHT11 logt elke 60s,
    HC-SR04 detecteert beweging, LCD toont status.
  - Supabase publishable key in `config.py` (gitignored).
- **PICO-33 t/m PICO-36 afgerond** (nexus-web + commands, 2026-06-07):
  - `nexus-web/` opgezet: Vite + React + TypeScript + Tailwind CSS + Supabase JS.
  - Dashboard toont live temperatuur en luchtvochtigheid (polling 5s).
  - Commands-pagina: `display_message` toont tekst op LCD, `buzzer` speelt toon.
  - Passieve buzzer aangesloten op GPIO 9 (PWM, 200–2000Hz werkt).
  - `tools/upload.ps1` verbeterd: uploadt nu ook submappen en losse `.py`
    bestanden uit de experimentmap (excl. `config.py` en `test_*.py`).
- **PICO-35 overgeslagen** (geluidssensor niet gevonden — vervangen door PICO-42 KY-038).
- **Nexus netwerkstabiliteit verbeterd (2026-06-09):**
  - `supabase.py` gesplitst in `_auth` (GET) en `_write_headers` (POST/PATCH).
    `Prefer: return=minimal` en `Connection: close` correct per requesttype.
  - Retry-logica: één herpoging na 500ms bij `OSError` (ECONNRESET) in alle
    netwerkfuncties — loop crasht nooit meer bij netwerkstoringen.
  - Commands worden elke 10s gepollt i.p.v. elke seconde (was 60 HTTPS/min).
  - `laatste_sensor_log` update na inserts i.p.v. vóór — voorkomt rapid-fire logging.
- **LDR lichtmeting toegevoegd aan Nexus:**
  - `sensors/ldr.py` aangemaakt, logt `ldr_light` (%) elke `poll_interval_s` seconden.
  - Kalibratie op huidige opstelling: `min_raw=6000` (vinger), `max_raw=36000` (lamp).
  - Dashboard toont lichtwaarde als derde sensorkaart.
- **PICO-37 afgerond** (settings instelbaar via website):
  - `Settings.tsx` toegevoegd: `poll_interval_s` en `temp_alert_threshold` instelbaar.
  - Pico laadt settings bij opstart via `supabase.get_settings()`.
  - Pico herlaadt settings bij ontvangst van `set_setting` command.
  - `settings` tabel: kolommen `key`, `value`.
- **BMP180 geïntegreerd in Nexus (2026-06-09):**
  - GY-68 module (VIN/GND/SCL/SDA) werkt op I2C-adres 0x77.
  - Deelt I2C-bus met LCD (0x27) op GPIO 0/1 — geen conflict.
  - `sensors/bmp180.py` aangemaakt, logt `bmp180_pressure` (hPa) elke poll.
  - Dashboard toont luchtdruk als vierde sensorkaart.
  - DHT11 retry-logica toegevoegd in main.py (OSError ETIMEDOUT bij opstart).
  - PICO-41 was geannuleerd wegens onduidelijke pinout — pinout nu bewezen: VIN/GND/SCL/SDA.
- **Testscripts beschikbaar in `tools/`:**
  - `test_gpio_loopback.py` — GPIO-loopback test voor nieuwe Pico (13 paren)
  - `test_i2c_scan.py` — I2C-bus scan
  - `test_bmp180.py` — BMP180 standalone test
- **PICO-39 afgerond** (2026-06-12): BMP180 drukmeting bewezen en geïntegreerd in Nexus.
- **PICO-42 geblokkeerd** (2026-06-11): twee KY-038 modules getest — beide
  defect/te laag vermogen. AO-uitgang blijft op ~0.1V, DO triggert nooit.
  **GPIO 28 (ADC2) is defect op deze Pico** — leest ~8400 bij directe 3V3
  (correct: 65535). GPIO 27 (ADC1) werkt wel. KY-038 AO op GPIO 27.
  2x MAX4466 besteld, arriveert 2026-06-12. PICO-42 hervat na ontvangst.
- **PICO-43 afgerond** (2026-06-12):
  - 4-kanaals relaismodule (SONGLE SRD-05VDC), DC+ → 3V3 (niet VBUS).
  - Jumpers S1–S4 op **H** (HIGH trigger) — 3V3 logica werkt dan correct.
  - **Kanaal 1 beschadigd**: 12V raakte IN1 tijdens bedrading. Gebruik **kanaal 2**.
  - IN2 → GPIO 21, relay HIGH = aan, LOW = uit.
  - 12V adaptor: COM → 12V+, NO → ventilator+, 12V− → ventilator−.
  - `output/relay.py` aangemaakt.
  - GPIO 20 heeft slechte breadboard-contact — gebruik GPIO 21.
  - `fan_on` / `fan_off` commands in `main.py` en Commands-pagina.
  - `tools/test_nexus_all.py` test alle 6 componenten inclusief gemeten waarden.
- **Command-responsiviteit verbeterd (2026-06-12):**
  - Vier sensor-inserts blokkeerden de loop elk ~10s → commands kwamen 40s te laat.
  - Oplossing: `verwerk_commands()` helper aangeroepen *tussen* elke sensor-insert
    met verse `time.ticks_ms()` — commands reageren nu binnen ~3s.
- **Commands UI verbeterd (2026-06-12):**
  - Per-knop `useCommand()` hook — knoppen bevriezen niet meer samen.
  - `ActionButton` component: `scale-95` + kleurflits + "Verstuurd" label bij succes.
- **PICO-44 afgerond** (2026-06-12): Pushover notificaties als output kanaal.
  - `output/pushover.py` aangemaakt: HTTP POST naar `api.pushover.net/1/messages.json`.
  - Triggers: `motion_detected` event en temperatuurdrempel overschrijding (eenmalig).
  - `notify` command: website kan vrij bericht sturen via Supabase.
  - Elke verzonden notificatie wordt gelogd als `pushover_sent` event in Supabase.
  - `pushover_enabled` setting: toggle op Settings-pagina, standaard **uit**.
  - Credentials in `config.py`: `PUSHOVER_TOKEN`, `PUSHOVER_USER`.
- **Code review uitgevoerd (2026-06-12):** vier bugs gefixed:
  - `hcsr04.py`: `start`/`end` buiten while-lussen (waren mogelijk undefined).
  - `supabase.py`: socket-lek bij JSON-fout — `r.content` voor `r.close()`.
  - `supabase.py`: `"now()"` → `"now"` als geldige PostgreSQL timestamp keyword.
  - `main.py`: DHT11 retry vangt nu ook checksum errors (`Exception` i.p.v. `OSError`).
- **Testpiramide toegevoegd (2026-06-12):**
  - `tools/test_nexus_module.py` — module tests (laag 1, geen WiFi)
  - `tools/test_nexus_integratie.py` — integratie tests (laag 2, geen WiFi)
  - `tools/test_nexus_keten.py` — keten tests (laag 3, WiFi + Supabase)
  - `tools/test_nexus_master.py` — master runner, alle lagen achter elkaar
- **PICO-40 afgerond** (2026-06-12): Grafieken + event log op website.
  - `nexus-web/src/pages/Grafieken.tsx`: vier lijngrafieken (temp, vocht, licht, druk).
  - Supabase real-time subscriptions via `postgres_changes` — updates direct bij insert.
  - Vereist in Supabase SQL: `ALTER TABLE sensor_readings REPLICA IDENTITY FULL`,
    idem voor `events`, plus `ALTER PUBLICATION supabase_realtime ADD TABLE ...`.
  - Y-as per sensor instelbaar: temperatuur `[min(0, data), auto]`, overige `auto/auto`.
  - Limietknoppen: 50 / 100 / 1000 / 50000 meetpunten.
  - Event log met filterknopen: Alles / Beweging / Geen beweging / Pushover.
  - `sensor_readings` tabel uitgebreid met `created_at timestamptz DEFAULT now()`.
- **LCD roterende weergave (2026-06-12):**
  - Scherm 0 (4s): `23C 65% 1013h` / `Licht:72%`
  - Scherm 1 (4s): `Beweging: JA!/nee` / laatste event
  - LCD update alleen bij schermwissel of na nieuwe meting — geen onnodige I2C writes.
- **PICO-42 afgerond** (2026-06-12): MAX4466 geluidssensor geïntegreerd.
  - `sensors/sound.py`: piek-tot-piek amplitude over 50 samples (50ms), DREMPEL=7000.
  - `verwerk_geluid()` helper aangeroepen in hoofdlus én tussen sensor-inserts.
  - `time.sleep(1)` → `time.sleep_ms(100)` — geluidsdetectie runt 10x per seconde.
  - `sound_detected` / `sound_absent` events gelogd met amplitude in payload.
  - **Let op:** MAX4466 OUT moet op **GPIO 27** (niet GPIO 26 — dat is de LDR).
    GPIO 26 en 27 op hetzelfde signaal = MAX4466 onderdrukt LDR-meting volledig.
  - LDR kalibratie bijgewerkt: `min_raw=4000`, `max_raw=34088`.
  - `tools/test_max4466.py`: kalibratiescript met amplitude live in terminal.
- **Bewegingsdetectie betrouwbaarheid verbeterd (2026-06-12):**
  - HC-SR04 miste events tijdens sensor-inserts (40s blindspot per poll-cyclus).
  - Oplossing: `verwerk_beweging()` helper, zelfde patroon als `verwerk_geluid()`.
  - Aangeroepen in hoofdlus én tussen elke sensor-insert.
- **MAX4466 kalibratie bevestigd (2026-06-13):**
  - Potmeter linksom gedraaid (meer gain). Ruisvloer: ~993–2641. DREMPEL=7000 blijft correct.
  - Ruisvloer 2.6× marge onder drempel; praten begint bij ~8050.
- **Dashboard beweging/geluid toegevoegd (2026-06-13):**
  - `StatusCard` component: toont "JA" (oranje) / "nee" (grijs) op basis van laatste event.
  - `fetchStatus()`: haalt laatste `motion_*` en `sound_*` event op uit Supabase, refresht elke 5s.
- **Geluid debounce toegevoegd (2026-06-13):**
  - `GELUID_AFWEZIG_NA = 5` seconden — `sound_absent` wordt pas gelogd na 5s stilte.
  - Zelfde patroon als `AFWEZIG_NA = 30` voor beweging.
  - Vóór fix: elke adempauze triggerde `sound_absent`, website zag altijd "nee".
- **Event log verbeterd (2026-06-13):**
  - Geluid-filter knop toegevoegd in Grafieken (`sound_detected`).
  - `sound_detected` krijgt groen label, `sound_absent` grijs.
- **Bewegingsdetectie verbeterd via baseline-aanpak (2026-06-13):**
  - Vaste drempel `BEWEGING_DREMPEL = 50` vervangen door dynamische baseline.
  - Bij opstart meet Pico de rustafstand (5 pings, gemiddelde). Beweging =
    (baseline - meting) > `BEWEGING_DELTA` (15 cm).
  - Werkt ongeacht opstelling — sensor past zich aan bij herstart.
  - `laatste_beweging` bijgewerkt bij elke meting met beweging (debounce vanaf laatste detectie).
- **Open-Meteo buiten-data toegevoegd aan dashboard (2026-06-13):**
  - Sectie "Buiten — Voorschoten (Open-Meteo)" onder de sensor-kaarten.
  - Toont temperatuur, vochtigheid en luchtdruk van buitenlocatie.
  - Per kaart: buitenwaarde + delta tov Nexus (oranje = Nexus hoger, blauw = lager).
  - Locatie: lat 52.13, lon 4.45 (Voorschoten). Ververst elke 60 seconden. Geen API-key.
- **PICO-45 afgerond (2026-06-13): Mood switch**
  - Nieuwe pagina "Mood" op de website: naam + 3-cijferige code + fijn/matig/slecht.
  - Twee Supabase-tabellen: `mood_users` (name, code) en `moods` (user_name, mood, tekst).
  - Eerste gebruik: gebruiker aangemaakt met naam + code. Code vergeten → rij verwijderen in Supabase.
  - Bij `fijn` en `slecht`: buzzer + tekst 10s op LCD.
    Fijn: C5→E5→G5 (oplopend majeur). Slecht: G5→C5→G4 (dalend, zwaar).
  - Command `mood_alert` in `verwerk_commands()`. `laatste_lcd_update` gereset na display.
- **Volgende stappen:** PICO-38 (IR bediening).

### Nieuwe hardware — beschikbaar en onderweg

- **BMP180** (in huis, werkend): I2C-adres 0x77, deelt bus met LCD op GPIO 0/1.
- **KY-038 geluidssensor** (2x, beide defect): AO blijft op ~0.1V, DO triggert nooit.
  Vervangen door MAX4466 (arriveert 2026-06-12). AO → GPIO 27, DO → GPIO 19.
- **4-kanaals relaismodule** (in huis, werkend): kanaal 1 beschadigd, kanaal 2 in gebruik.
  IN2 → GPIO 21, DC+ → 3V3, jumpers op H. PICO-43 afgerond.
- **12V adaptor + ventilator** (in huis): aangesloten op relaiskanaal 2, werkt.
- **MAX4466 geluidssensor** (2x, in huis, werkend): GPIO 27 (ADC1). PICO-42 afgerond.

### Supabase kolomnamen (bewezen uit debug-sessie)

| Tabel | Kolommen |
|-------|----------|
| `commands` | `id`, `command` (niet `type`!), `payload`, `created_at`, `executed_at` |
| `sensor_readings` | `id`, `sensor`, `value`, `created_at` (timestamptz, DEFAULT now()) |
| `events` | `id`, `type`, `payload` |
| `settings` | `id`, `key`, `value` (`key` is uniek, UPSERT op conflict) |
| `mood_users` | `id`, `name` (uniek), `code`, `created_at` |
| `moods` | `id`, `user_name`, `mood`, `tekst`, `created_at` |

RLS is uitgeschakeld op alle tabellen — anon key heeft volledige toegang.
- GY-BME280 en GY-BMP280 worden geleverd op **2026-06-25**. Na ontvangst
  wordt experiment 01 uitgebreid met drukmeting. Plan:
  - Sensor op dezelfde I2C-bus als LCD (SDA=GPIO 0, SCL=GPIO 1, VCC=3V3).
  - I2C-adres: `0x76` (SDO→GND) of `0x77` (SDO→3V3) — geen conflict met LCD.
  - BME280 meet temp + vocht + druk → vervangt DHT11. BMP280 meet alleen
    temp + druk → DHT11 blijft voor vochtigheid. Keuze na ontvangst.
  - Nieuwe module `shared/bme280.py`, CSV-header krijgt kolom `druk_hpa`.
- Het bash `tools/upload.sh` is vervangen door **`tools/upload.ps1`**: de
  Windows-bash hier is WSL en heeft geen `mpremote` of directe COM-toegang.
  PowerShell is de natuurlijke shell op Windows. Docs zijn bijgewerkt.
- Issue tracker: Jira project **`PICO`** op
  `https://ejdetheije.atlassian.net`. 6 Epics (PICO-1 t/m PICO-6) en 18
  starter-Taken (PICO-7 t/m PICO-24).

### Schakelen tussen experimenten

Beide experimenten staan tegelijk op het breadboard. Schakelen = ander
experiment uploaden, Pico herstart automatisch:

```powershell
# Weerstation
.\tools\upload.ps1 experiments\01_weerstation
mpremote

# Solar tracker
.\tools\upload.ps1 experiments\05_solar_tracker
mpremote
```

### Actuele pin-bezetting op het breadboard

Beide experimenten staan tegelijk op het bord. Overzicht:

| GPIO | Experiment 01 (weerstation) | Experiment 05 (solar tracker) |
|------|-----------------------------|-------------------------------|
| 0    | LCD SDA (I2C0)              | —                             |
| 1    | LCD SCL (I2C0)              | —                             |
| 8    | —                           | Servo signaal                 |
| 16   | DHT11                       | —                             |
| 26   | LDR                         | LDR rechts (gedeeld)          |
| 28   | —                           | LDR links                     |
| Vbus | LCD VCC                     | Servo VCC                     |

### LDR — afgerond (2026-06-04)

- Bedrading: `3V3 → LDR → GPIO 26 → 1kΩ → GND`.
- GPIO 26 is gedeeld: experiment 01 (weerstation) en experiment 05 (solar tracker LDR rechts) gebruiken dezelfde fysieke LDR. Beide experimenten draaien nooit tegelijk.
- `shared/ldr.py` gebruikt software remapping: `min_raw=2500`, `max_raw=21000`.
- Gemeten bereik na kalibratie: vinger≈5%, schaduw≈43%, lamp≈74%.
- **Let op:** kalibratie verschuift als draden worden ingekort of verplaatst.
  Bij afwijkend bereik: `test_adc.py` uitvoeren, raw waarden noteren bij
  vinger/schaduw/lamp, dan `min_raw` en `max_raw` herberekenen in `ldr.py`.

**Valkuilen LDR (bewezen uit debug-sessie):**
- **Breadboard middengroef:** jumper draad en Pico-pin ALTIJD aan dezelfde
  kant van de middengroef. Links en rechts zijn elektrisch gescheiden — ook
  al staan ze in dezelfde genummerde rij. Dit was de hoofdoorzaak van de
  vaste 17%-waarde.
- **Weerstandkeuze:** 10kΩ verzadigt bij fel licht (92–96%, onbruikbaar).
  1kΩ geeft een bruikbare spreiding in combinatie met software remapping.
- **RP2350 ADC offset:** GPIO 26 leest ~3000 raw (~5%) bij directe GND-
  verbinding. Dit is normaal gedrag van de RP2350 — geen fout.

**Kit-inventaris bijgewerkt:** 10kΩ weerstanden zitten ook in de Freenove kit
(naast de eerder gevonden 1kΩ en 220Ω).

### Solar tracker — afgerond (2026-06-05)

- Servo op GPIO 8 (GPIO 7 had slechte verbinding in die breadboard-rij).
- Freenove SG90 draadkleuren: **bruin = GND, rood = VCC (Vbus), oranje = signaal**.
- Twee LDR's lezen ongelijk in ambient licht → opstartskalibratie meet het
  nulpuntverschil en trekt dat af van de delta. Zie `kalibreer()` in `main.py`.
- DREMPEL = 300. Bij 1500 reageerde de servo niet op lamplicht.
- `test_servo.py` beschikbaar als diagnostisch script voor servo-isolatietest.

**Valkuilen servo (bewezen uit debug-sessie):**
- **Losse pin in connector:** female dupont-connector kan halfingeplukt zijn.
  Altijd controleren bij geen respons — ook al lijkt alles aangesloten.
- **GPIO-rij defect:** als een pin niet reageert, probeer de buurpin.
  GPIO 7 werkte niet, GPIO 8 wel.
- **mpremote run stopt snel:** gebruik `cp :main.py` + `mpremote` voor
  een persistent draaiend script. `mpremote run` keert terug zodra het klaar is.
- **REPL multiline:** code kopiëren vanuit markdown geeft `IndentationError`.
  Sla code op in een bestand en upload met `mpremote cp` of `upload.ps1`.

## Experiment 06 — Nexus

Nexus is een permanente hub die continu meet, events logt en op afstand
bedienbaar is via een React-website. Kernpatroon:

**Pico meet/detecteert → Supabase → website**
**Website stuurt commando → Supabase → Pico voert uit**

Het breadboard wordt **leeggemaakt** voordat dit experiment wordt opgebouwd.
Experimenten 01 en 05 blijven in de repo maar zijn niet meer bedraad.

### Mapstructuur

```
experiments/06_nexus/
├── main.py               # Hoofdloop
├── config.py             # Gitignored — echte WiFi + Supabase credentials
├── config.example.py     # Gecommit — placeholders voor nieuwe installatie
├── supabase.py           # HTTP wrapper (GET/POST naar Supabase REST)
├── sensors/
│   ├── dht11.py
│   ├── ldr.py
│   ├── hcsr04.py
│   ├── sound.py
│   ├── ir.py
│   └── bme280.py         # Toevoegen na ontvangst op 2026-06-25
├── output/
│   ├── lcd.py
│   └── buzzer.py
└── handlers/
    ├── event_handler.py
    └── command_handler.py

nexus-web/                # Root van pico-lab repo — aparte tech-stack
├── src/
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Events.tsx
│   │   ├── Commands.tsx
│   │   └── Settings.tsx
│   ├── lib/
│   │   └── supabase.ts
│   └── components/
│       ├── SensorCard.tsx
│       ├── EventLog.tsx
│       └── CommandForm.tsx
├── package.json
└── vite.config.ts
```

Website-stack: **Vite + React + TypeScript + Tailwind CSS** met Supabase JS
client. Deployment via Vercel of Netlify (gratis tier).

### Pin-tabel Nexus

Leeg bord, alle pins beschikbaar. Toewijzing op basis van standaard pinout.

| GPIO | Component | Functie |
|------|-----------|---------|
| 0 | LCD 1602 SDA | I2C0 data |
| 1 | LCD 1602 SCL | I2C0 klok |
| 9 | Buzzer passief | PWM toon |
| 13 | RGB LED R | PWM (toekomstig) |
| 14 | RGB LED G | PWM (toekomstig) |
| 15 | RGB LED B | PWM (toekomstig) |
| 16 | DHT11 | 1-wire |
| 17 | HC-SR04 trigger | Digitaal uit |
| 18 | HC-SR04 echo | Digitaal in |
| 19 | Geluidssensor (D) | Digitaal interrupt |
| 20 | IR ontvanger | Digitaal interrupt |
| 26 | LDR | ADC0 |
| Vbus | LCD VCC, Servo VCC | 5V via USB |

### Credentials

`config.py` is gitignored. `config.example.py` wordt gecommit met placeholders:

```python
# config.example.py — kopieer naar config.py en vul in
WIFI_SSID = "jouw-netwerk"
WIFI_PASSWORD = "jouw-wachtwoord"
SUPABASE_URL = "https://xxxx.supabase.co"
SUPABASE_KEY = "eyJ..."
```

Voeg `experiments/06_nexus/config.py` toe aan `.gitignore` voor de eerste commit.

---

## Hardware inventaris

### Board

- Raspberry Pi Pico 2W (chip RP2350, WiFi 802.11n, BLE 5.2, 26 GPIO)
- Verbinding met laptop: USB, verschijnt als COM-poort op Windows
- Upload: `mpremote`

### Sticker op het breadboard (ALTIJD gebruiken bij bedrading)

Op het breadboard zit een sticker met de pinlabels van de Pico. Gebruik
**altijd deze labels** — nooit fysieke pinnummers (1–40).

Rechterkant (van USB-connector naar beneden):
`Vbus`, `3V3`, `GND`, `EN`, `Vref`, `26`, `RUN`, `22`, `21`, `20`, `19`, `18`, `17`, `16`

Linkerkant (van USB-connector naar beneden):
`0`, `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `10`, `11`, `12`, `13`, `14`, `15`

GND-pinnen zitten op beide kanten verspreid — de blauwe rail op het breadboard
is de GND-rail.

### Sensoren (Freenove kit)

| Sensor               | Interface          | Opmerking                          |
|----------------------|--------------------|------------------------------------|
| DHT11                | 1-wire digitaal    | Temperatuur + luchtvochtigheid     |
| HC-SR04              | 2x digitaal        | Trigger + echo, ultrasoon          |
| LDR (fotoresistor)   | Analoog (ADC)      | Lichtintensiteit                   |
| Geluidssensor module | Digitaal of ADC    | Drempel of analoog niveau          |
| IR ontvanger         | Digitaal           | Afstandsbedieningssignalen         |
| Kantelschakelaar     | Digitaal           | Oriëntatie (open/dicht)            |
| RFID RC522           | SPI                | Kaartlezing                        |
| Joystick module      | 2x ADC + digitaal  | X, Y, knop                         |

### Actuatoren

| Component            | Interface          | Opmerking                          |
|----------------------|--------------------|------------------------------------|
| SG90 micro servo (6x)| PWM                | 0–180°, signaal 3.3V               |
| Stappenmotor + ULN2003| 4x digitaal       | Nauwkeurige rotatie                |
| RGB LED              | 3x PWM             | Kleurmenging                       |
| Buzzer (actief + passief) | Digitaal of PWM | Toon                              |
| 7-segment display    | 7-8x digitaal      | Cijferweergave                     |
| LCD 1602 (I2C)       | I2C                | 16x2 tekst                         |

## Pinout-conventies

Per component een vaste "default" GPIO. Experimenten met conflicten mogen
afwijken — documenteer dat dan in de `README.md` van het experiment.

| Component            | Default GPIO       | Functie                            |
|----------------------|--------------------|------------------------------------|
| LCD 1602 SDA         | GPIO 0             | I2C0 data                          |
| LCD 1602 SCL         | GPIO 1             | I2C0 clock                         |
| RFID SCK             | GPIO 2             | SPI0                               |
| RFID MOSI            | GPIO 3             | SPI0                               |
| RFID MISO            | GPIO 4             | SPI0                               |
| RFID CS              | GPIO 5             | SPI0                               |
| RFID RST             | GPIO 6             |                                    |
| Servo 1..6           | GPIO 7..12         | PWM; exp 05 gebruikt GPIO 8        |
| RGB LED R/G/B        | GPIO 13 / 14 / 15  | PWM                                |
| DHT11                | GPIO 16            | 1-wire                             |
| HC-SR04 trigger      | GPIO 17            |                                    |
| HC-SR04 echo         | GPIO 18            |                                    |
| Geluidssensor (D)    | GPIO 19            |                                    |
| IR ontvanger         | GPIO 20            |                                    |
| Kantelschakelaar     | GPIO 21            |                                    |
| Joystick knop        | GPIO 22            |                                    |
| LDR / joystick X     | GPIO 26 (ADC0)     | Analoog; gedeeld: weerstation + solar tracker LDR rechts |
| LDR2 / joystick Y    | GPIO 27 (ADC1)     | Analoog                            |
| Solar tracker LDR links | GPIO 28 (ADC2)  | Analoog; alleen experiment 05      |
| Geluidssensor (A)    | GPIO 28 (ADC2)     | Analoog; niet tegelijk met exp 05  |

Stappenmotor en knop voor experiment 02 krijgen pins toegewezen die in dat
experiment vrij zijn — vermeld dit altijd in het bedradingsschema.

## mpremote workflow (Windows)

Installatie:

```powershell
uv tool install mpremote
```

COM-poort detecteren:

```powershell
mpremote connect list
```

Eén bestand uploaden:

```powershell
mpremote cp experiments/01_weerstation/main.py :main.py
```

Compleet experiment uploaden (via helperscript):

```powershell
.\tools\upload.ps1 experiments\01_weerstation
```

Live REPL en output bekijken:

```powershell
mpremote
```

Reset na upload: `Ctrl-D` in de REPL (soft reset).

Testscript uitvoeren (lokaal bestand direct op Pico runnen — GEEN cp nodig):

```powershell
mpremote run tools/test_mijn_script.py
```

**Let op:** `mpremote run` verwacht een **lokaal pad**. Nooit eerst `cp` doen
en daarna `run` zonder pad — dat geeft "could not read file".

## Codeerstijl

- MicroPython, geen zware externe libraries. Alleen wat op de Pico past.
- Iedere sensor of actuator krijgt zijn eigen klasse in een eigen module.
- Korte modules, korte functies, duidelijke namen.
- Commentaar en docstrings in het Nederlands.
- Geen emoji's in code, prints, of logs.
- Geen defensieve programmering. Geef root cause, geen workarounds.
- Geen try/except tenzij er een concrete fout is om af te vangen.

## Experimentstructuur

```
experiments/NN_naam/
    main.py        # entry point, draait op de Pico
    README.md      # hypothese, schema, waarnemingen
    data/          # CSV's van metingen (niet in git)
```

`main.py` mag importeren uit `shared/`. Het uploadscript kopieert
`shared/` automatisch mee.

## Nexus printplaat — solderschema (PY-5CM×7CM perfboard)

Pico en LCD zijn **niet** op de plaat — die hangen apart. De plaat bevat
sensoren/actuatoren en twee module-headers. Pico sluit aan via pinheaders
op rij A.

### Componentenlijst op de plaat

| Component | Type | Aansluiting |
|-----------|------|-------------|
| DHT11 | Direct gesoldeerd | 3 pins |
| Passieve buzzer | Direct gesoldeerd | 2 pins |
| LDR | Direct gesoldeerd | 2 benen |
| 1kΩ weerstand | Direct gesoldeerd | 2 benen |
| KY-038 header | 4-pins header | module hangt eraan |
| HC-SR04 header | 4-pins header | module hangt eraan |
| BMP180 header | 4-pins header | module hangt eraan |

### Lay-out (rijen A–R, kolommen 1–17)

```
     1    2    3    4    5    6    7    8    9   10   11
A  [GND][3V3][VBU][G9 ][G16][G17][G18][G19][G26][G0 ][G1 ]  <- Pico headers
B    .    .    .    .    .    .    .    .    .    .    .
C    .    .    .    .    .    .    .    .    .    .    .
D    .  [VCC][DAT][GND]  .    .  [ + ][ - ]  .    .    .    <- DHT11 + Buzzer
E    .    .    .    .    .    .    .    .    .    .    .
F    .    .    .    .    .    .    .    .    .    .    .
G    .    .    .    .  [LDR]  .    .    .    .    .    .    <- LDR been 1 (3V3)
H    .    .    .    .  [LDR]  .    .    .    .    .    .    <- LDR been 2
I    .    .    .    .  [1kO]  .    .    .    .    .    .    <- 1kΩ been 1
J    .    .    .    .  [1kO]  .    .    .    .    .    .    <- 1kΩ been 2 (GND)
K    .    .    .    .    .    .    .    .    .    .    .
L    .  [VCC][GND][D0 ][A0 ]  .    .    .    .    .    .    <- KY-038 header
M    .    .    .    .    .    .    .    .    .    .    .
N    .  [VCC][GND][TRG][ECH]  .    .    .    .    .    .    <- HC-SR04 header
O    .    .    .    .    .    .    .    .    .    .    .
P    .  [VIN][GND][SCL][SDA]  .    .    .    .    .    .    <- BMP180 header
Q  [===][===][===][===][===][===][===][===][===]  .    .    <- GND-rail
R  [===][===][===][===][===][===][===][===][===]  .    .    <- 3V3-rail
```

### Verbindingen achterkant (draadjes + soldeerbruggen)

| # | Van | Naar | Opmerking |
|---|-----|------|-----------|
| 1 | A1 (GND) | Q1 | |
| 2 | A2 (3V3) | R1 | kolom 2 verbindt ook D2, L2, N2, P2 onderweg |
| 3 | A4 (G9) | D7 | Buzzer signaal |
| 4 | A5 (G16) | D3 | DHT11 data |
| 5 | A6 (G17) | N4 | HC-SR04 trigger |
| 6 | A7 (G18) | N5 | HC-SR04 echo |
| 7 | A8 (G19) | L4 | KY-038 D0 |
| 8 | A9 (G26) | H5 | LDR midden-knoop |
| 9 | A10 (G0/SDA) | P5 | BMP180 SDA — via col 10 omlaag, dan links in rij P |
| 10 | A11 (G1/SCL) | P4 | BMP180 SCL — via col 11 naar O11, dan links naar O4, dan omlaag |
| 11 | D2 (DHT11 VCC) | R2 | onderdeel van kolom-2 draad |
| 12 | D4 (DHT11 GND) | Q4 | |
| 13 | D8 (Buzzer −) | Q7 | |
| 14 | G5 (LDR been 1) | R5 | 3V3 zijde |
| 15 | H5–I5 | soldeer­brug | LDR been 2 + 1kΩ been 1 |
| 16 | J5 (1kΩ been 2) | Q5 | GND zijde |
| 17 | L2 (KY-038 VCC) | R2 | onderdeel van kolom-2 draad |
| 18 | L3 (KY-038 GND) | Q3 | kolom-3 draad verbindt ook N3 en P3 |
| 19 | N2 (HC-SR04 VCC) | R2 | onderdeel van kolom-2 draad |
| 20 | N3 (HC-SR04 GND) | Q3 | onderdeel van kolom-3 draad |
| 21 | P2 (BMP180 VIN) | R2 | onderdeel van kolom-2 draad |
| 22 | P3 (BMP180 GND) | Q3 | onderdeel van kolom-3 draad |

**Let op:** buzzer-pinafstand verschilt per model — controleer of D7/D8
past of dat je de benen ombuigt.

### Achterkant — soldeerpatroon

```
ACHTERKANT (zelfde richting als voorkant)

      1    2    3    4    5    6    7    8    9   10   11
 A    o----o----·----o----o----o----o----o----o----o----o
      |    |         |    |    |    |         |    |    |
      |    |    +----+    |    |    |    +----+    |    |
      |    |    |    +----+----+----+    |         |    |
 B    |    |    |    |    x    x         |         |    |
      |    |    |    |    |    |         |         |    |
 C    |    |    |    |    |    +---------+         |    |
      |    |    |    |    |                        |    |
 D    ·    o----o----o    ·    ·    o----o    ·    |    |
      |    |         |              |              |    |
      |    |         |              |              |    |
 E    |    |         |    ·    ·    |              |    |
      |    |         |              |              |    |
 F    |    |         |    ·    ·    |              |    |
      |    |         |                             |    |
 G    |    |         |    o    ·    |              |    |
      |    |         |    |         |              |    |
 H    |    |         |    o==(brug) |              |    |
      |    |         |       |      |              |    |
 I    |    |         |    o==(brug) |              |    |
      |    |         |    |                        |    |
 J    |    |         |    o    ·    ·              |    |
      |    |         |    |                        |    |
 K    |    |         |    |    ·    ·              |    |
      |    |    +----+    |                        |    |
 L    |    o----o    o----o    ·    ·              |    |
      |    |         |    |                        |    |
 M    |    |    +----+    |                        |    |
      |    |    |         |                        |    |
 N    |    o----o    o----o    ·    ·              |    |
      |    |         |    |                        |    |
 O    |    |         |    |         +--------------x----+
      |    |         |    |         |              |
 P    |    o----o    o----o         |              |
      |    |         |    |         |
 Q    o====o====o====o====o====·====o====o====·   GND-rail
 R    o====o====·====·====o====·====·====·====·   3V3-rail
```

Legenda:
- `o` = gesoldeerd pad
- `|` `-` = draad (geïsoleerd)
- `x` = kruising (draden raken elkaar NIET, beide geïsoleerd)
- `==(brug)` = soldeer­brug H5-I5
- `====` = doorlopende rail

Twee nieuwe draden voor BMP180 I2C:
- **G0/SDA (A10 → P5):** col 10 omlaag van A10 naar P10, dan links P10─P5
- **G1/SCL (A11 → P4):** col 11 omlaag naar O11, dan links O11─O4, dan omlaag O4─P4. Kruist col 10 bij O10 (×).

Kolom 2 loopt van A2 helemaal door naar R2 — verbindt in één draad:
Pico 3V3 → DHT11 VCC → KY-038 VCC → HC-SR04 VCC → BMP180 VIN → 3V3-rail.

Kolom 3 loopt van L3/N3/P3 naar Q3 — verbindt KY-038 GND, HC-SR04 GND en BMP180 GND.

## Veiligheidsregels

- Servo-signaal komt van een Pico GPIO (3.3V PWM).
- Servo-VCC gaat naar VBUS (pin 40, 5V via USB) — NOOIT naar de 3.3V pin.
- Maximaal 3 servo's tegelijk op USB-voeding. Meer servo's: externe 5V voeding
  met gemeenschappelijke GND.
- Servo draadkleuren: bruin = GND, rood = VCC (5V), oranje = signaal.
- Stappenmotor altijd via ULN2003 driver — nooit direct op GPIO.
- Bij twijfel: meet eerst, dan aansluiten.
