# Plan — experimentenoverzicht

Vijf experimenten van makkelijk naar complex. Eerst sensor uitlezen, daarna
combineren, ten slotte sensor + actuator als regelkring.

## Status (2026-06-03)

| Experiment             | Code | Bedraad | Getest | Jira Epic |
|------------------------|------|---------|--------|-----------|
| 01 weerstation         | ja   | nee     | nee    | PICO-2    |
| 02 reactiemeting       | ja   | nee     | nee    | PICO-3    |
| 03 sonar               | ja   | nee     | nee    | PICO-4    |
| 04 servo-wijzer        | ja   | nee     | nee    | PICO-5    |
| 05 solar tracker       | ja   | nee     | nee    | PICO-6    |

Pico 2W is live op **COM8** met MicroPython v1.28.0. Fase 0 van de bring-up
(PICO-7, PICO-8, PICO-9) is afgerond — upload-workflow gemigreerd naar
PowerShell (`tools/upload.ps1`) en gevalideerd met dummy
`experiments/00_smoketest/`. Freenove kit is binnen, inclusief DHT11 en
LCD 1602: PICO-10 (eerste experiment-bouw) is klaar om te starten.
GY-BME280 + GY-BMP280 worden op 2026-06-25 geleverd als losse toevoegingen
voor een latere variant; geen blokker voor experiment 01. Stappenplan voor
de bring-up: zie [`bring_up_plan.md`](bring_up_plan.md).

Issue tracker: Jira project **`PICO`** op
[ejdetheije.atlassian.net](https://ejdetheije.atlassian.net/browse/PICO-1).
6 Epics + 18 starter-Taken. Volgende ticket: PICO-10.

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
