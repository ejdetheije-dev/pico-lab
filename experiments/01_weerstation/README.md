# Experiment 01 — Weerstation

## Hypothese

Tijdens een uur in een gesloten kamer met één persoon stijgt de temperatuur
licht (0.5–1 °C) en stijgt de luchtvochtigheid duidelijker door uitademing.
Lichtintensiteit daalt meetbaar wanneer de verlichting wordt gedimd of buiten
bewolking toeneemt.

## Benodigde componenten

- Raspberry Pi Pico 2W
- DHT11
- LCD 1602 met PCF8574 I2C-backpack (adres 0x27)
- LDR (fotoresistor)
- 1kΩ weerstand (pull-down voor LDR)
- Breadboard, jumper wires

## Bedradingsschema

```
   Pico 2W                  DHT11               LCD 1602 (I2C)
   --------                 -----               --------------
   3.3V (pin 36) ---------- VCC ---- (+) ------ VCC
   GND  (pin 38) ---------- GND ---- (-) ------ GND
   GPIO 16 (pin 21) ------- DATA
   GPIO 0  (pin 1)  ---------------------------- SDA
   GPIO 1  (pin 2)  ---------------------------- SCL

   LDR spanningsdeler (GPIO 26 / ADC0):
   3.3V (pin 36) --- LDR --- GPIO 26 (pin 31) --- 1kΩ --- GND (pin 38)
```

Hoe de LDR werkt: bij meer licht daalt de weerstand van de LDR, stijgt de
spanning op GPIO 26, en geeft `ldr.lees()` een hogere waarde (0-100).

## Verwachte resultaten

- Temperatuur: 18–24 °C, stabiel met variatie < 1 °C per minuut.
- Luchtvochtigheid: 30–60 %, met langzame stijging als ramen dicht zijn.
- DHT11 resolutie: 1 °C en 1 %, dus geen sub-graad signaal zichtbaar.
- Lichtintensiteit: 0-100 % (relatief). Reageert direct op aan/uitschakelen
  van verlichting of doorgaan van de hand over de sensor.

## Meetmethode

1. Plaats sensor op vaste positie, niet in direct zonlicht of luchtstroom.
2. Sluit ramen, log 60 minuten (720 metingen bij 5 s interval).
3. Haal `data/weerstation.csv` op via `mpremote cp :data/weerstation.csv .`.
4. Plot in een spreadsheet of Python.

## Waarnemingen

_(vul aan tijdens uitvoering)_
