# Pico Lab — Claude instructies

## Projectoverzicht

Experimenteer-lab rond de Raspberry Pi Pico 2W. Doel: korte, afgebakende
experimenten waarin sensoren en actuatoren uit het Freenove Ultimate Starter
Kit op een breadboard worden gecombineerd. Code is MicroPython, draait direct
op de Pico, en wordt vanaf een Windows-laptop geupload via `mpremote`.

Iedere `experiments/NN_naam/` map staat op zichzelf: één duidelijk leerdoel,
één wetenschappelijke vraag, één `main.py` die werkt zodra je hem upload.

## Hardware inventaris

### Board

- Raspberry Pi Pico 2W (chip RP2350, WiFi 802.11n, BLE 5.2, 26 GPIO)
- Verbinding met laptop: USB, verschijnt als COM-poort op Windows
- Upload: `mpremote`

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
| Servo 1..6           | GPIO 7..12         | PWM                                |
| RGB LED R/G/B        | GPIO 13 / 14 / 15  | PWM                                |
| DHT11                | GPIO 16            | 1-wire                             |
| HC-SR04 trigger      | GPIO 17            |                                    |
| HC-SR04 echo         | GPIO 18            |                                    |
| Geluidssensor (D)    | GPIO 19            |                                    |
| IR ontvanger         | GPIO 20            |                                    |
| Kantelschakelaar     | GPIO 21            |                                    |
| Joystick knop        | GPIO 22            |                                    |
| LDR / joystick X     | GPIO 26 (ADC0)     | Analoog                            |
| LDR2 / joystick Y    | GPIO 27 (ADC1)     | Analoog                            |
| Geluidssensor (A)    | GPIO 28 (ADC2)     | Analoog                            |

Stappenmotor en knop voor experiment 02 krijgen pins toegewezen die in dat
experiment vrij zijn — vermeld dit altijd in het bedradingsschema.

## mpremote workflow (Windows)

Installatie:

```powershell
pip install mpremote
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
bash tools/upload.sh experiments/01_weerstation
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
