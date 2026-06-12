# Bring-up plan

Stappenplan voor wanneer de hardware in huis is. Doel: depth-first werken —
experiment 01 één keer volledig werkend krijgen vóór we aan 02 beginnen.
Dat valideert de hele keten (USB → mpremote → breadboard → sensor → log)
in plaats van vijf half-werkende opstellingen.

## Werkwijze per stap

Voor elk component, in deze volgorde:

1. **Voeding aansluiten** — multimeter op de rails, 3.3V en 5V verifiëren
2. **Signaallijnen** — pas aansluiten als voeding klopt; controleer met
   pinout in `CLAUDE.md`
3. **Sensor uitlezen in de REPL** — één regel Python, geen `main.py` nog
4. **Pas dan `main.py` uploaden** — integratie als laatste stap

Bij problemen: één variabele tegelijk wijzigen, niet meerdere dingen tegelijk
"proberen". Bewijs eerst waar de fout zit met meting, niet met gokken.

## Fase 0 — Pico zelf live krijgen

Geschatte tijd: 15 min. Geen breadboard nodig.

1. Pico 2W via USB op laptop aansluiten
2. COM-poort detecteren:

   ```powershell
   mpremote connect list
   ```

3. Geen MicroPython erop? Houd BOOTSEL ingedrukt tijdens aansluiten,
   sleep `.uf2`-firmware naar de USB-massastorage die verschijnt.
   Recentste firmware: https://micropython.org/download/RPI_PICO2_W/
4. REPL openen en onboard-LED laten knipperen:

   ```powershell
   mpremote
   ```

   ```python
   from machine import Pin
   import time
   led = Pin("LED", Pin.OUT)
   for _ in range(5):
       led.toggle()
       time.sleep(0.5)
   ```

**Klaar als:** LED knippert. USB + firmware + mpremote zijn bewezen.

## Fase 1 — Experiment 01 weerstation in losse stappen

Geschatte tijd: 60–90 min.

### 1.1 Voeding op breadboard

- 3.3V (pin 36) → rode rail
- GND (pin 38) → blauwe rail
- Multimeter: 3.3V ± 0.1V tussen de rails

### 1.2 DHT11 standalone

- VCC → 3.3V rail, GND → GND rail, DATA → GPIO 16 (pin 21)
- Multimeter op DATA: ~3.3V (idle, met pull-up)
- REPL test:

  ```python
  import dht
  from machine import Pin
  s = dht.DHT11(Pin(16))
  s.measure()
  print(s.temperature(), s.humidity())
  ```

- **Klaar als:** redelijke getallen verschijnen (15–30 °C, 20–80 %).
  Krijg je `OSError: Failed to read sensor`? Wacht 2 s en probeer opnieuw —
  DHT11 heeft tijd nodig na power-on.

### 1.3 LCD 1602 standalone

- VCC → 5V (VBUS pin 40), GND → GND, SDA → GPIO 0, SCL → GPIO 1
- Achterkant heeft een potmeter voor contrast — draaien als scherm leeg lijkt
- I2C-adres scannen in REPL:

  ```python
  from machine import I2C, Pin
  i2c = I2C(0, sda=Pin(0), scl=Pin(1))
  print(i2c.scan())
  ```

- **Klaar als:** `[39]` (0x27) of `[63]` (0x3F) verschijnt. Wijk je af van
  0x27? Pas `Lcd1602(addr=...)` aan in `main.py`.
- Hello-world test met `shared/display_helper.py` via REPL.

### 1.4 Combinatie en logging

- Beide componenten samen op breadboard, gemeenschappelijke GND
- Upload en draai:

  ```powershell
  .\tools\upload.ps1 experiments\01_weerstation
  mpremote
  ```

- **Klaar als:** LCD toont temp + vocht, console print elke 5 s een rij,
  na ~1 min staat er een CSV op de flash:

  ```powershell
  mpremote cp :data/weerstation.csv .
  ```

- Vink experiment 01 af in `plan.md` (kolom "Getest").

## Fase 2 — De andere vier experimenten

Eén experiment per sessie, in deze volgorde:

1. `02_reactiemeting` — LED + knop (eenvoudig, geen sensor-quirks)
2. `03_sonar` — HC-SR04 (let op 5V echo-lijn, eventueel spanningsdeler)
3. `04_servo_wijzer` — eerste actuator (servo op VBUS, niet 3.3V!)
4. `05_solar_tracker` — sensor + actuator regelkring

Per experiment dezelfde fase-1 aanpak: voeding → signaal → REPL → main.py.
Vink af in `plan.md` na elke afronding.

## Fase 3 — Eerste eigen variatie

Pak één idee uit "Toekomstige experimenten" in `plan.md` en bouw het zelf.
Daarmee bewijs je dat je de patronen door hebt:

- Sensor in eigen klasse
- `main.py` per experiment, geen globale state
- `shared/` voor herbruikbare stukken
- README met hypothese + schema + waarnemingen

## Relaismodule valkuilen (bewezen 2026-06-11)

- **3V3 vs 5V logica:** SONGLE SRD-05VDC op 5V (VBUS) — 3V3 GPIO kan optocoupler
  niet volledig afsnijden in LOW-trigger modus. Oplossing: DC+ op **3V3**, jumpers
  op **H** (HIGH trigger). GPIO HIGH = relais aan, GPIO LOW = relais uit.
- **12V op IN-pin:** dikke adaptordraad voorzichtig aansluiten. Als 12V per ongeluk
  op een IN-klem komt, is die channel permanent beschadigd. Altijd 12V **losgekoppeld**
  houden tijdens bedrading van de IN-pinnen.
- **Zwevende IN-pinnen:** in LOW-trigger modus activeren zwevende IN-pinnen het relais
  (trekt te veel stroom). Altijd alle ongebruikte IN-pinnen op VCC zetten of direct
  aansturen.
- **GPIO 20 slechte contact:** GPIO 20 op dit bord heeft slechte breadboard-contact.
  Gebruik GPIO 21 als alternatief.
- **GPIO 28 defect:** ADC2 (GPIO 28) leest ~8400 bij directe 3V3 — pin is beschadigd.
  Gebruik GPIO 27 (ADC1) voor analoge sensoren.

## Command-responsiviteit in de hoofdloop (bewezen 2026-06-12)

Wanneer de loop meerdere blokkerende HTTPS-calls achter elkaar doet (bijv. vier
sensor-inserts van elk ~10s), komen commands tot 40s te laat aan.

**Oplossing:** extraheer command-polling in een aparte functie en roep die aan
*tussen* elke blokkerende operatie, met verse `time.ticks_ms()`:

```python
def verwerk_commands():
    global laatste_command_poll
    if time.ticks_diff(time.ticks_ms(), laatste_command_poll) < 3000:
        return
    for cmd in supabase.get_pending_commands():
        # ...verwerk...
        supabase.mark_executed(cmd["id"])
    laatste_command_poll = time.ticks_ms()

# In sensor-logging blok:
supabase.insert("sensor_readings", {"sensor": "dht11_temp", "value": temp})
verwerk_commands()
supabase.insert("sensor_readings", {"sensor": "ldr_light", "value": licht})
verwerk_commands()
# ... etc.
```

De `3000ms` guard voorkomt dat `verwerk_commands()` bij elke insert een echte
poll doet — alleen als er 3s verstreken zijn.

## Grafieken real-time setup (bewezen 2026-06-12)

Supabase real-time werkt niet zonder deze twee SQL-statements in de SQL Editor:

```sql
ALTER TABLE sensor_readings REPLICA IDENTITY FULL;
ALTER TABLE events REPLICA IDENTITY FULL;
ALTER PUBLICATION supabase_realtime ADD TABLE sensor_readings;
ALTER PUBLICATION supabase_realtime ADD TABLE events;
```

Zonder `REPLICA IDENTITY FULL` ontvangen kolom-gefilterde subscriptions
(`filter: 'sensor=eq.dht11_temp'`) geen events. Zonder `ADD TABLE` werkt
real-time helemaal niet voor die tabel.

## Pushover integratie valkuilen (bewezen 2026-06-12)

- **`config.py` wordt niet geüpload door `upload.ps1`** — altijd apart uploaden:
  ```powershell
  mpremote cp experiments\06_nexus\config.py :config.py
  ```
- **Toggle-knob buiten de balk:** gebruik `inline-flex items-center` op de track
  en `inline-block` op de knop — geen `absolute` positionering of `overflow-hidden`.
- **Standaard uitgeschakeld:** `pushover_enabled` default is `"false"`. Gebruiker
  moet expliciet aanzetten via Settings → Opslaan. Pico herlaadt na `set_setting` command.
- **Notificatie logging:** elke verstuurde notificatie staat als `pushover_sent` event
  in de `events` tabel — zichtbaar in Supabase dashboard.

## MAX4466 valkuilen (bewezen 2026-06-12)

- **GPIO-conflict LDR/geluid:** MAX4466 OUT op GPIO 26 onderdrukt de LDR volledig
  (MAX4466 trekt pin naar VCC/2 ≈ 32800 raw = constant ~50%). Altijd GPIO 27 gebruiken.
- **Drempel kalibreren:** ruisvloer ~5600–6400, zachte klap ~7000–8000, harde klap ~9000–10000.
  Start met DREMPEL=7000. Verlaag naar 6800 bij te weinig gevoeligheid.
- **Loop-snelheid:** `time.sleep(1)` geeft maar 4.5% kans een klap te vangen. Gebruik
  `time.sleep_ms(100)` in de hoofdlus voor 10x hogere meetfrequentie.

## Veelvoorkomende valkuilen

- **COM-poort wisselt** na herstart van de Pico op Windows. `mpremote connect list`
  opnieuw draaien.
- **LCD blijft leeg, maar I2C-scan vindt adres:** contrast-potmeter op de
  backpack draaien.
- **DHT11 geeft soms een uitleesfout:** geen workaround inbouwen — wacht 2 s
  tussen metingen, controleer pull-up.
- **Servo trilt of doet niets:** je hebt 'm op 3.3V hangen. Moet VBUS (5V).
- **Meerdere servo's tegelijk:** USB-voeding zakt in. Externe 5V adapter met
  gemeenschappelijke GND.
- **HC-SR04 echo op GPIO geeft rare metingen na uren:** 5V op GPIO is buiten
  spec. Spanningsdeler 1kΩ + 2kΩ op de echo-lijn.
