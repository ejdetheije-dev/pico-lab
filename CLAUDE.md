# Pico Lab — Claude instructies

## Projectoverzicht

Experimenteer-lab rond de Raspberry Pi Pico 2W. Doel: korte, afgebakende
experimenten waarin sensoren en actuatoren uit het Freenove Ultimate Starter
Kit op een breadboard worden gecombineerd. Code is MicroPython, draait direct
op de Pico, en wordt vanaf een Windows-laptop geupload via `mpremote`.

Iedere `experiments/NN_naam/` map staat op zichzelf: één duidelijk leerdoel,
één wetenschappelijke vraag, één `main.py` die werkt zodra je hem upload.

## Huidige status

Stand per 2026-06-05:

- Pico 2W is live op **COM8** met MicroPython v1.28.0 (RPI_PICO2_W),
  gemonteerd op breadboard, USB-C aangesloten op de Windows-laptop.
- **Fase 0 afgerond:** PICO-7, PICO-8, PICO-9 (Gereed in Jira).
- **PICO-10 afgerond** (experiment 01 weerstation volledig werkend):
  - §1.1 voeding bewezen met LED + 1kΩ (geen multimeter beschikbaar).
  - §1.2 DHT11 op GPIO 16 leest in REPL `23 52` (°C / % rv). Sensor is
    **kaal** (geen PCB-module) — `Pin.IN, Pin.PULL_UP` expliciet meegeven.
  - §1.3 LCD 1602 op I2C0 (SDA=0, SCL=1, VCC=Vbus), adres `0x27`. Pinout
    valkuil: de `GND/VCC/SDA/SCL`-silkscreen labels staan op de **voorkant**
    van het PCB-tje, niet op de achterkant.
  - §1.4 combinatie + CSV-log: `experiments/01_weerstation/main.py` draait
    end-to-end. LCD toont temp+vocht, console logt per 5 s, CSV op
    `:data/weerstation.csv` (Pico-flash).
- **PICO-22 afgerond** (experiment 05 solar tracker werkend, 2026-06-05):
  - Twee LDR's: GPIO 26 (gedeeld met weerstation) en GPIO 28 (nieuw).
  - Servo SG90 op GPIO 8 (GPIO 7 had slechte breadboard-verbinding).
  - Opstartskalibratie compenseert nulpuntverschil tussen de twee LDR's.
  - DREMPEL = 300 (1500 reageerde niet op lamplicht).
  - Beide experimenten op het bord; draaien nooit tegelijk.
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
