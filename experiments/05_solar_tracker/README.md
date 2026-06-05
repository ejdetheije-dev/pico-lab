# Experiment 05 — Solar tracker

## Hypothese

Twee LDR's met een tussenschot kunnen het lichtste punt in hun gezichtsveld
lokaliseren door hun ADC-waarden te vergelijken. Met een gepaste drempel
(hysterese) volgt de servo een bewegende lichtbron zonder te trillen.

## Benodigde componenten

- Raspberry Pi Pico 2W
- 2x LDR (fotoresistor) — LDR rechts is gedeeld met experiment 01 (weerstation) op GPIO 26
- 2x 1kΩ weerstand (pull-down voor spanningsdeler; 10kΩ verzadigt bij fel licht)
- SG90 micro servo
- Klein kartonnen tussenschot tussen de twee LDR's (5–10 mm hoog)
- Breadboard, jumper wires
- Zaklamp of telefoonzaklamp als testlichtbron

## Bedradingsschema

```
   Pico 2W                  LDR links             LDR rechts
   --------                 ---------             ----------
   3.3V (pin 36) ----+----- LDR_L           +---- LDR_R
                     |       |              |      |
                    (gelijk) |             (gelijk)|
                             +--- ADC2     |       +--- ADC0
                             |  (GPIO 28)  |       | (GPIO 26) *gedeeld met weerstation*
                            [1kR]          |      [1kR]
                             |             |       |
                            GND           GND     GND

   Servo:
   GND  (pin 38)   ----------- GND (bruin)
   VBUS (pin 40)   ----------- VCC (rood)
   GPIO 7 (pin 10) ----------- SIGNAAL (oranje)
```

Monteer beide LDR's naast elkaar op de servo-arm met een kartonnen schotje
tussen, zodat licht van links de linker-LDR sterker raakt en omgekeerd.

## Verwachte resultaten

- Bij gelijkmatig licht: `delta` < drempel, servo blijft staan.
- Bij zaklamp links: `links > rechts`, hoek loopt op (naar links).
- Bij zaklamp recht boven: servo schommelt rond de balanspositie.
- Reactiesnelheid: ~25 graden per seconde bij stappen van 2°/80 ms.
- Zonder drempel: continu trillen door ruis van enkele honderden counts.

## Meetmethode

1. Start het experiment in halflicht; noteer de rust-ADC-waarden.
2. Beweeg de zaklamp langzaam van links naar rechts; meet hoe snel de servo
   volgt.
3. Verlaag de drempel stapsgewijs (1500 -> 1000 -> 500): vanaf welke waarde
   begint hij te trillen?
4. Test in fel zonlicht en in schemerlicht — werkt het signaal-tot-ruis
   beide kanten op?

## Waarnemingen

_(vul aan tijdens uitvoering)_
