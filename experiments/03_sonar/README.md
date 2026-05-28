# Experiment 03 — Sonar

## Hypothese

De HC-SR04 is betrouwbaar tussen ca. 3 cm en 200 cm. Onder 3 cm zal de echo
te snel terugkomen om correct te meten; boven 200 cm wordt de echo te zwak
en krijg je timeouts of grote ruis.

## Benodigde componenten

- Raspberry Pi Pico 2W
- HC-SR04 ultrasone sensor (werkt op 5V)
- RGB LED (gemeenschappelijke kathode)
- 3x 220Ω weerstand
- Breadboard, jumper wires
- Een voorwerp om te meten (kartonnen doos werkt goed)

## Bedradingsschema

```
   Pico 2W                  HC-SR04            RGB LED (CC)
   --------                 -------            ------------
   VBUS (pin 40, 5V) ------ VCC
   GND  (pin 38)    ------- GND ----+
   GPIO 17 (pin 22) ------- TRIG    |
   GPIO 18 (pin 24) ------- ECHO    |
                                    +-------- common kathode
   GPIO 13 (pin 17) --[220R]------------- R
   GPIO 14 (pin 19) --[220R]------------- G
   GPIO 15 (pin 20) --[220R]------------- B
```

Let op: HC-SR04 echo geeft een 5V puls. Op de Pico is 5V op een GPIO niet
ideaal. Voor langdurig gebruik kun je een spanningsdeler (1kΩ + 2kΩ) op de
echo-lijn plaatsen. Voor korte experimenten gaat het meestal goed.

## Verwachte resultaten

- Stabiele metingen 5–150 cm, herhaling binnen ±1 cm.
- 150–200 cm: meer ruis, soms timeouts.
- > 200 cm: vaak `geen echo`.
- Onder 3 cm: meting blijft op ~2 cm steken.

## Meetmethode

1. Zet een voorwerp loodrecht voor de sensor.
2. Schuif van 2 cm tot 250 cm in stappen van 10 cm en noteer de gemeten
   waarde uit de console.
3. Vergelijk met de werkelijke afstand (meetlint).
4. Test ook een zacht doek-oppervlak vs hard karton: zachte oppervlakken
   absorberen geluid en geven kortere bereik.

## Waarnemingen

_(vul aan tijdens uitvoering)_
