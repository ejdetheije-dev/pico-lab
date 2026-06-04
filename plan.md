# Plan — experimentenoverzicht

Vijf experimenten van makkelijk naar complex. Eerst sensor uitlezen, daarna
combineren, ten slotte sensor + actuator als regelkring.

## Status (2026-06-04)

| Experiment             | Code | Bedraad | Getest | Jira Epic |
|------------------------|------|---------|--------|-----------|
| 01 weerstation         | ja   | ja      | ja     | PICO-2    |
| 02 reactiemeting       | ja   | nee     | nee    | PICO-3    |
| 03 sonar               | ja   | nee     | nee    | PICO-4    |
| 04 servo-wijzer        | ja   | nee     | nee    | PICO-5    |
| 05 solar tracker       | ja   | nee     | nee    | PICO-6    |

Pico 2W is live op **COM8** met MicroPython v1.28.0. Fase 0 van de bring-up
(PICO-7, PICO-8, PICO-9) is afgerond — upload-workflow gemigreerd naar
PowerShell (`tools/upload.ps1`) en gevalideerd met dummy
`experiments/00_smoketest/`.

**PICO-10 afgerond** (Fase 1 van `bring_up_plan.md`, Jira-status Gereed):

- §1.1 voeding bewezen via LED + 1kΩ (geen multimeter beschikbaar).
- §1.2 DHT11 standalone op GPIO 16, kale sensor met `Pin.IN, Pin.PULL_UP`.
- §1.3 LCD 1602 op I2C0 (adres `0x27`); pinout-labels op de voorkant van
  de backpack-PCB.
- §1.4 combinatie + CSV-log werkt: `main.py` draait, LCD toont temp+vocht,
  CSV op de flash, op te halen met `mpremote cp :data/weerstation.csv .`.
- §1.5 LDR op GPIO 26 (ADC0), bedrading `3V3 → LDR → GPIO 26 → 1kΩ → GND`,
  software remapping (`min_raw=5600`, `max_raw=25000`), bereik 19–75%.

**Valkuilen die bewezen zijn (zie ook CLAUDE.md):**
- Breadboard middengroef: jumper en Pico-pin altijd aan dezelfde kant.
- RP2350 ADC offset: ~3000 raw bij GND is normaal.
- 10kΩ verzadigt bij fel licht; 1kΩ + remapping werkt beter.

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
- **Hardware:** Pico 2W, 2x LDR, 2x 10kΩ weerstand, SG90 servo, breadboard.
- **Bouwtijd:** ~60 min.
- **Wetenschappelijke vraag:** Hoe snel kan de servo het lichtste punt volgen,
  en wat is de minimale lichtverschil-drempel waarop hij betrouwbaar reageert?

## Openstaande verbeteringen (later oppakken)

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
