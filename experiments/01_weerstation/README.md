# Experiment 01 — Weerstation

## Hypothese

Tijdens een uur in een gesloten kamer met één persoon stijgt de temperatuur
licht (0.5–1 °C) en stijgt de luchtvochtigheid duidelijker door uitademing.

## Benodigde componenten

- Raspberry Pi Pico 2W
- DHT11
- LCD 1602 met PCF8574 I2C-backpack (adres 0x27)
- Breadboard, jumper wires
- Eventueel: 10kΩ pull-up tussen DHT11 DATA en 3.3V

## Bedradingsschema

```
   Pico 2W                  DHT11               LCD 1602 (I2C)
   --------                 -----               --------------
   3.3V (pin 36) ---------- VCC ---- (+) ------ VCC
   GND  (pin 38) ---------- GND ---- (-) ------ GND
   GPIO 16 (pin 21) ------- DATA
   GPIO 0  (pin 1)  ---------------------------- SDA
   GPIO 1  (pin 2)  ---------------------------- SCL
```

## Verwachte resultaten

- Temperatuur: 18–24 °C, stabiel met variatie < 1 °C per minuut.
- Luchtvochtigheid: 30–60 %, met langzame stijging als ramen dicht zijn.
- DHT11 resolutie: 1 °C en 1 %, dus geen sub-graad signaal zichtbaar.

## Meetmethode

1. Plaats sensor op vaste positie, niet in direct zonlicht of luchtstroom.
2. Sluit ramen, log 60 minuten (720 metingen bij 5 s interval).
3. Haal `data/weerstation.csv` op via `mpremote cp :data/weerstation.csv .`.
4. Plot in een spreadsheet of Python.

## Waarnemingen

_(vul aan tijdens uitvoering)_
