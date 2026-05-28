# Experiment 02 — Reactiemeting

## Hypothese

Een uitgeruste volwassene heeft een gemiddelde visuele reactietijd van
200–280 ms, met een standaarddeviatie van 20–40 ms over 10 pogingen.
Vermoeidheid verhoogt zowel het gemiddelde als de spreiding.

## Benodigde componenten

- Raspberry Pi Pico 2W
- Standaard 5mm LED (rood)
- 220Ω weerstand
- Drukknop
- Breadboard, jumper wires

## Bedradingsschema

```
   Pico 2W                  LED                Knop
   --------                 ---                ----
   GPIO 15 (pin 20) ---[220R]--- LED+
                                 LED- ------- GND
   GPIO 14 (pin 19) ----------------+----- knop
                                    |
                                   GND
   (interne pull-up actief op GPIO 14)
```

## Verwachte resultaten

- Reactietijd: typisch 200–300 ms.
- Standaarddeviatie: 20–50 ms.
- Te vroege drukken (< 80 ms na LED-on) worden afgewezen.
- Drukken tijdens de wachttijd resulteert in herhaling van de ronde.

## Meetmethode

1. Zit ontspannen, hand op knop, blik op LED.
2. Doe 10 geldige rondes.
3. Noteer gemiddelde en standaarddeviatie uit de console-output.
4. Herhaal in een tweede sessie (bv. na sport of laat op de avond) voor
   vergelijking.

## Waarnemingen

_(vul aan tijdens uitvoering)_
