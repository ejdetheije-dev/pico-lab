# Plan — experimentenoverzicht

Vijf experimenten van makkelijk naar complex. Eerst sensor uitlezen, daarna
combineren, ten slotte sensor + actuator als regelkring.

## Status (2026-05-28)

| Experiment             | Code | Bedraad | Getest |
|------------------------|------|---------|--------|
| 01 weerstation         | ja   | nee     | nee    |
| 02 reactiemeting       | ja   | nee     | nee    |
| 03 sonar               | ja   | nee     | nee    |
| 04 servo-wijzer        | ja   | nee     | nee    |
| 05 solar tracker       | ja   | nee     | nee    |

Hardware (Pico 2W + Freenove kit) is nog niet in huis. Zodra het pakket
binnen is gaan we 01 bouwen, opstarten en valideren — dan pas door naar 02.
Stappenplan voor die bring-up: zie [`bring_up_plan.md`](bring_up_plan.md).

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
