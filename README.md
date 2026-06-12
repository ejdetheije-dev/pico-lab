# Pico Lab

Experimenteer-lab rond de Raspberry Pi Pico 2W. Korte, op zichzelf staande
MicroPython-experimenten met sensoren en actuatoren uit het Freenove Ultimate
Starter Kit. Experiment 06 (Nexus) is een permanente hub die continu meet en
op afstand bedienbaar is via een React-website.

## Vereisten

- Raspberry Pi Pico 2W met MicroPython firmware (COM9)
- Freenove Ultimate Starter Kit (sensoren, breadboard, jumper wires)
- Windows-laptop met `uv` en `mpremote`

## Snelstart

1. Installeer `mpremote`:

   ```powershell
   uv tool install mpremote
   ```

2. Sluit de Pico 2W aan via USB. Controleer de COM-poort:

   ```powershell
   mpremote connect list
   ```

3. Upload een experiment:

   ```powershell
   .\tools\upload.ps1 experiments\06_nexus
   ```

4. Open de REPL om output te zien:

   ```powershell
   mpremote
   ```

## Mappen

```
experiments/
  01_weerstation/     DHT11 + LCD, CSV-log op flash
  05_solar_tracker/   Twee LDR's + servo, regelkring
  06_nexus/           Permanente hub (zie hieronder)
shared/               Herbruikbare modules
tools/                Upload- en testscripts
nexus-web/            React-dashboard voor Nexus
bring_up_plan.md      Hardware bring-up stappenplan en valkuilen
```

## Nexus (experiment 06)

Nexus is de actieve hub. Architectuur:

```
Pico 2W meet/detecteert --> Supabase --> nexus-web dashboard
Website stuurt command   --> Supabase --> Pico voert uit
```

### Sensoren op het breadboard

| GPIO | Component    | Logt als             |
|------|--------------|----------------------|
| 0/1  | LCD 1602     | I2C0 (SDA/SCL)       |
| 9    | Buzzer       | PWM                  |
| 16   | DHT11        | dht11_temp / dht11_humidity |
| 17/18| HC-SR04      | events: motion_detected / motion_absent |
| 21   | Relais k2    | fan_on / fan_off     |
| 26   | LDR          | ldr_light (%)        |
| 0/1  | BMP180       | bmp180_pressure (hPa)|

### Commands die de website kan sturen

| Command           | Effect                        |
|-------------------|-------------------------------|
| `display_message` | Tekst op LCD (regel1/regel2)  |
| `buzzer`          | Pieptoon (freq, duur_ms)      |
| `fan_on`          | Relais aan — ventilator start |
| `fan_off`         | Relais uit — ventilator stopt |
| `set_setting`     | Herlaad settings van Supabase |

### Mapstructuur Nexus

```
experiments/06_nexus/
  main.py             Hoofdloop
  config.py           Gitignored — WiFi + Supabase credentials
  config.example.py   Placeholders voor nieuwe installatie
  supabase.py         HTTP wrapper naar Supabase REST API
  sensors/            dht11.py, ldr.py, hcsr04.py, bmp180.py
  output/             lcd.py, buzzer.py, relay.py
```

### Lokaal draaien van de website

Zie `nexus-web/README.md`.
