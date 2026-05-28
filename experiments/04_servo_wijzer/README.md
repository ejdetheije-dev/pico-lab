# Experiment 04 — Servo-wijzer

## Hypothese

Een SG90 servo kan een continue sensorwaarde betrouwbaar vertalen naar een
mechanische hoek zonder zichtbaar trillen, mits we de bewegingen vertragen
en de DHT11-resolutie (1 °C) accepteren als stapgrootte.

## Benodigde componenten

- Raspberry Pi Pico 2W
- DHT11
- SG90 micro servo
- Breadboard, jumper wires (female-to-female voor de servo-stekker)
- Eventueel: papieren of kartonnen wijzer geplakt op de servo-arm

## Bedradingsschema

```
   Pico 2W                  DHT11               SG90 servo
   --------                 -----               ----------
   3.3V (pin 36) ---------- VCC
   GND  (pin 38) ---------- GND ----+------ GND (bruin)
                                    |
   VBUS (pin 40, 5V) ------------------ VCC (rood)
   GPIO 16 (pin 21) ------- DATA
   GPIO 7  (pin 10) -------------------- SIGNAAL (oranje)
```

LET OP: servo-VCC gaat naar **VBUS (5V)**, nooit naar de 3.3V pin. Eén
servo werkt prima op USB-voeding; bij meerdere servo's een externe 5V
adapter gebruiken met gemeenschappelijke GND.

## Verwachte resultaten

- Bij 20 °C wijst de servo naar het midden (~90°).
- Bij 0 °C staat hij links (0°), bij 40 °C rechts (180°).
- Verandering met 1 °C geeft een sprong van 4.5°, duidelijk zichtbaar.
- Geen trillen in rust dankzij de soepel-naar-mapping.

## Meetmethode

1. Plaats een gemarkeerde schaal achter de servowijzer (0, 10, 20, 30, 40 °C).
2. Houd je hand om de DHT11 om de temperatuur te laten stijgen.
3. Vergelijk wijzerstand met console-output.
4. Test wat er gebeurt bij koeling (raam open of koelelement).

## Waarnemingen

_(vul aan tijdens uitvoering)_
