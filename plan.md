# Plan — experimentenoverzicht

Vijf experimenten van makkelijk naar complex. Eerst sensor uitlezen, daarna
combineren, ten slotte sensor + actuator als regelkring.

## Status (2026-08-06) — experiment 06 Nexus actief, bord tot ~2026-09-01 onbereikbaar

> **Het bord zit sinds 2026-08-04 in een metalen doos onder een bed en hangt NIET aan USB.**
> Geen `mpremote`, geen seriële console, geen COM-poort, tot het er rond 2026-09-01 weer uit
> komt. Code wijzigen kan alleen via OTA (een `ota_update`-rij in `commands`), en een stukke
> update is dan pas over weken te herstellen — weeg dat mee vóór je iets uitrolt.
>
> Bewegings- en geluidsdetectie zijn daar zinloos en dat is geaccepteerd; wat moet doorlopen
> is de P1-keten voor het ElectriciteitsHuishouding-dashboard. Gemeten in de doos: 97,5%
> doorvoer (was 86% op het bureau) en 25 °C, dus de behuizing kost niets. Uitval wordt sinds
> 2026-08-04 dagelijks vanuit de cloud bewaakt (`/api/bewaking` in het andere project), buiten
> dit bord om — want een bord dat stilstaat meldt zijn eigen uitval niet.
>
> Vlak vóór het wegzetten uitgerold: `verbind_wifi_bij_boot()` (`f742016`, OTA-versie
> `20260804001`), zodat een mislukte wifi bij het opstarten het bord niet meer dood achterlaat.
> Zie "Betrouwbaarheid van de Nexus-loop" in `CLAUDE.md`.
>
> **Twee afstandsbedieningen (`56a8d68`, OTA-versie `20260804002`), allebei een rij in
> `commands`:** `{"command":"reset"}` herstart het bord, en een `settings`-rij `p1_host` plus
> `{"command":"set_setting"}` verplaatst het meteradres zonder `config.py` aan te raken. Beide
> zijn op 2026-08-04 echt gebruikt, niet alleen geschreven. **Valt de P1 stil, stuur dan eerst
> een `reset`** - een herstart kan het bord de meter laten kwijtraken terwijl internet gewoon
> werkt, en nog een herstart lost dat op. Staat uitgewerkt in `CLAUDE.md`.
>
> **Zelfherstel bij een onbereikbare P1 (OTA-versie `20260804003`, uitgerold 14:33 en dezelfde
> dag nog bewezen).** Het bord doet die `reset` nu zelf: is de meter 15 minuten weg terwijl
> Supabase wél bereikbaar is, dan herstart het. Dat onderscheid is het hele ontwerp - ligt het
> netwerk eruit, dan verandert een herstart niets en gooit hij wel de gebufferde samples weg.
> Hielp het niet, dan hoogstens nog eens per uur; die rem overleeft de herstart via een
> vlagbestand op de flash, want `time.ticks_ms()` begint na een reset weer bij nul.
>
> **Het ging binnen een kwartier na installatie af, op zijn eigen aanleiding.** De OTA eindigt in
> een herstart, en juist die herstart liet de P1 wegvallen: `p1_proef` om 14:33:50 dood op beide
> endpoints. Toen `p1_zelfherstel` om 14:48:52 (`weg_s` 913), boot 14:49:16, `p1_proef`
> `ok 1115 bytes` om 14:49:27, `p1_zelfherstel_gelukt` om 14:49:28. Gat: 17,1 minuten in plaats
> van de vijftien uur die het tot de dagelijkse bewaking geduurd zou hebben.
>
> **De gebruiker wil hier na 2026-09-01 opnieuw naar gevraagd worden** - zodra het bord weer
> bereikbaar is, vervalt de aanleiding. Tel dan hoe vaak `p1_zelfherstel` is afgegaan.
>
> **RLS op de laatste vier tabellen (2026-08-06, `tools/rls.sql` deel 2).** Supabase meldde
> `commands`, `settings`, `moods` en `mood_users` als CRITICAL `rls_disabled_in_public`: iedereen
> met de publishable key uit de browserbundle kon ze wissen. RLS staat nu aan met tien policies
> die exact de verbs toestaan die de code gebruikt. Lezen bleef ongewijzigd (222 / 5 / 11 / 3
> rijen vóór en ná) en de schrijfkant is end-to-end bewezen met commando 223 (`rls_proef`, een
> onbekende naam die bij het bord door alle branches heen naar `mark_executed` valt):
> ingeschreven met de publishable key om 15:28:38Z, door het bord afgevinkt om 15:28:39Z.
> **Dat 1,04 seconde is meteen het bewijs dat het bord in de doos leeft en reageert.** De
> UPDATE-policy op `commands` is hier de kritieke: zonder die kan het bord `executed_at` niet
> zetten, blijft elk commando openstaan en zou de eerste `reset` een herstartlus geven - precies
> wat je niet wilt met een bord dat je niet kunt aanraken. Wat NIET dicht is: zie
> "Openstaande verbeteringen".

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

- **Wie een rij in `commands` mag zetten (open sinds 2026-08-06).** RLS staat nu op alle tabellen,
  maar de INSERT-policy op `commands` moet `true` blijven omdat nexus-web hem vanuit de browser
  gebruikt. Gevolg: wie de publishable key uit de browserbundle haalt, kan het bord laten
  herstarten (`reset`) of het meteradres verzetten (`set_setting`). Wissen en wijzigen is dicht,
  dit niet - en met een policy is het ook niet dicht te krijgen, want de rol die mag schrijven is
  dezelfde rol als de bezoeker.

  Twee routes, geen van beide klein: (a) inloggen in nexus-web (Supabase Auth) en de policies op
  `auth.uid() is not null` zetten - dan valt de Pico's eigen SELECT/UPDATE erbuiten en heeft die
  een eigen rol nodig; (b) een serverroute ertussen (Vercel-functie met de service-role key, zoals
  ElectriciteitsHuishouding het doet met `CRON_SECRET`) en de anon INSERT dichtzetten - dan hoeft
  de Pico niet te veranderen, en dat is met een onbereikbaar bord het zwaarste argument.

  Weeg mee hoe erg dit is: de repo is publiek (vereist voor OTA), dus de key is niet geheim te
  houden. De schade blijft beperkt tot een herstart of een verkeerd meteradres, en beide zijn
  vanaf hetzelfde kanaal weer recht te zetten.

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
