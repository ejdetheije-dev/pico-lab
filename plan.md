# Plan — experimentenoverzicht

Vijf experimenten van makkelijk naar complex. Eerst sensor uitlezen, daarna
combineren, ten slotte sensor + actuator als regelkring.

## Status (2026-06-07) — experiment 06 Nexus actief

| Experiment             | Code | Bedraad | Getest | Jira      |
|------------------------|------|---------|--------|-----------|
| 01 weerstation         | ja   | nee     | ja     | PICO-10   |
| 02 reactiemeting       | ja   | nee     | nee    | PICO-3    |
| 03 sonar               | ja   | nee     | nee    | PICO-4    |
| 04 servo-wijzer        | ja   | nee     | nee    | PICO-5    |
| 05 solar tracker       | ja   | nee     | ja     | PICO-22   |
| 06 nexus               | ja   | ja      | ja     | PICO-25   |

Nieuwe Pico 2W op **COM9** met MicroPython (voorgeïnstalleerd). Board is
leeggemaakt — Nexus-hardware aangesloten: LCD, DHT11, HC-SR04, LDR, buzzer.
PICO-26 t/m PICO-34 en PICO-36 zijn Gereed. PICO-35 overgeslagen (geluidssensor
niet gevonden). Volgende stap: PICO-37 (poll interval instelbaar).

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
- [ ] PICO-37: Settings: poll interval instelbaar via website

### Fase 3 (Jira PICO-38/39/40)

- [ ] PICO-38: IR bediening + LCD menu
- [ ] PICO-39: BME280 integreren (na levering 2026-06-25)
- [ ] PICO-40: Website: grafieken + event log met filtering

---

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
