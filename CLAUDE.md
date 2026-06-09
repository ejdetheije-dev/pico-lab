# Pico Lab — Claude instructies

## Projectoverzicht

Experimenteer-lab rond de Raspberry Pi Pico 2W. Doel: korte, afgebakende
experimenten waarin sensoren en actuatoren uit het Freenove Ultimate Starter
Kit op een breadboard worden gecombineerd. Code is MicroPython, draait direct
op de Pico, en wordt vanaf een Windows-laptop geupload via `mpremote`.

Iedere `experiments/NN_naam/` map staat op zichzelf: één duidelijk leerdoel,
één wetenschappelijke vraag, één `main.py` die werkt zodra je hem upload.

## Huidige status

Stand per 2026-06-09:

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
- **Volgende stappen:** PICO-42 (KY-038 woensdag 2026-06-11),
  PICO-43 (relaimodule + ventilator woensdag 2026-06-11).

### Nieuwe hardware — beschikbaar en onderweg

- **BMP180** (al in huis): module reageert niet op I2C — pinout onduidelijk, overgeslagen. PICO-41 geannuleerd.
- **KY-038 geluidssensor** (arriveert 2026-06-11): D0 → GPIO 19 (al gereserveerd),
  drempel instelbaar via trimmer op module. Ticket: PICO-42.
- **4-kanaals relaimodule + 12V adaptor + 12V ventilator** (arriveert 2026-06-11):
  één relaiskanaal stuurt de ventilator, Pico GPIO stuurt relai aan. Maakt
  afstandsbediening van 12V-apparaten mogelijk vanuit de website. Ticket: PICO-43.

### Supabase kolomnamen (bewezen uit debug-sessie)

| Tabel | Kolommen |
|-------|----------|
| `commands` | `id`, `command` (niet `type`!), `payload`, `created_at`, `executed_at` |
| `sensor_readings` | `id`, `sensor`, `value` (geen `created_at`) |
| `events` | `id`, `type`, `payload` |
| `settings` | `id`, `key`, `value` (`key` is uniek, UPSERT op conflict) |

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

## Veiligheidsregels

- Servo-signaal komt van een Pico GPIO (3.3V PWM).
- Servo-VCC gaat naar VBUS (pin 40, 5V via USB) — NOOIT naar de 3.3V pin.
- Maximaal 3 servo's tegelijk op USB-voeding. Meer servo's: externe 5V voeding
  met gemeenschappelijke GND.
- Servo draadkleuren: bruin = GND, rood = VCC (5V), oranje = signaal.
- Stappenmotor altijd via ULN2003 driver — nooit direct op GPIO.
- Bij twijfel: meet eerst, dan aansluiten.
