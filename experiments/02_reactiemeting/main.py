"""Reactiemeting — LED flitst op random moment, knop meet reactietijd.

Voert 10 metingen uit, toont per meting de reactietijd in ms, en geeft aan
het eind het gemiddelde, minimum, maximum en de spreiding.
"""

import time
import random
from machine import Pin


LED_PIN = 15
BUTTON_PIN = 14
ROUNDS = 10
MIN_WACHT_MS = 1500
MAX_WACHT_MS = 5000
TE_VROEG_MS = 80


def wacht_op_knop(button, timeout_ms=5000):
    """Geef het aantal ms terug tussen oproep en knop-indruk, of None bij timeout."""
    start = time.ticks_ms()
    while button.value() == 1:
        if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
            return None
        time.sleep_ms(1)
    return time.ticks_diff(time.ticks_ms(), start)


def statistieken(metingen):
    """Bereken gemiddelde, min, max, populatie-standaarddeviatie."""
    n = len(metingen)
    gem = sum(metingen) / n
    mn = min(metingen)
    mx = max(metingen)
    var = sum((m - gem) ** 2 for m in metingen) / n
    sd = var ** 0.5
    return gem, mn, mx, sd


def main():
    led = Pin(LED_PIN, Pin.OUT)
    button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)

    print("Reactiemeting — {} rondes".format(ROUNDS))
    metingen = []
    ronde = 0
    while ronde < ROUNDS:
        led.off()
        wacht = random.randint(MIN_WACHT_MS, MAX_WACHT_MS)
        print("Ronde {}: wacht {} ms".format(ronde + 1, wacht))

        start_wacht = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start_wacht) < wacht:
            if button.value() == 0:
                print("  Te vroeg! Ronde opnieuw.")
                time.sleep(1)
                break
            time.sleep_ms(2)
        else:
            led.on()
            tijd = wacht_op_knop(button, timeout_ms=3000)
            led.off()
            if tijd is None:
                print("  Timeout, geen druk.")
            elif tijd < TE_VROEG_MS:
                print("  Onder drempel ({} ms), ongeldig.".format(tijd))
            else:
                print("  Reactietijd: {} ms".format(tijd))
                metingen.append(tijd)
                ronde += 1

        time.sleep_ms(500)

    if metingen:
        gem, mn, mx, sd = statistieken(metingen)
        print("--- Resultaten ---")
        print("Aantal:      ", len(metingen))
        print("Gemiddelde:  {:.1f} ms".format(gem))
        print("Min / max:   {} / {} ms".format(mn, mx))
        print("Std.dev.:    {:.1f} ms".format(sd))


main()
