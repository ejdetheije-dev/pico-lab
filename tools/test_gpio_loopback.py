"""GPIO loopback test voor een nieuwe Pico 2W.

Verbind de volgende pin-paren met jumpers voordat je dit script start:
  0-1, 2-3, 4-5, 6-7, 8-9, 10-11, 12-13, 14-15,
  16-17, 18-19, 20-21, 22-26, 27-28

Gebruik: mpremote connect COMx run tools/test_gpio_loopback.py
"""

from machine import Pin
import time

PAREN = [
    (0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11),
    (12, 13), (14, 15), (16, 17), (18, 19), (20, 21),
    (22, 26), (27, 28),
]

geslaagd = []
mislukt = []

for a, b in PAREN:
    fout = False
    for uit, in_ in [(a, b), (b, a)]:
        out = Pin(uit, Pin.OUT)
        inp = Pin(in_, Pin.IN)
        for waarde in (1, 0):
            out.value(waarde)
            time.sleep_ms(10)
            if inp.value() != waarde:
                fout = True
    if fout:
        mislukt.append((a, b))
        print("FAIL: GPIO", a, "<->", b)
    else:
        geslaagd.append((a, b))
        print("OK:   GPIO", a, "<->", b)

print()
print("Resultaat:", len(geslaagd), "/", len(PAREN), "geslaagd")
if not mislukt:
    print("Alle pins OK")
else:
    print("Mislukt:", mislukt)
