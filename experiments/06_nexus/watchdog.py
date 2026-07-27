"""Hardware-watchdog met opt-out, plus een voedende sleep.

Bewust zonder projectimports: supabase.py en ota.py mogen feed() aanroepen zonder
van main.py af te hangen. Zolang wapen() niet is gelopen is feed() een no-op, dus
losse scripts en REPL-werk blijven werken.
"""

import machine
import os
import time

MAX_TIMEOUT_MS = 8388  # hardgrens van de RP2350-watchdog
UIT_BESTAND = "wdt_uit"

_wdt = None


def wapen():
    """Wapen de watchdog. Slaat over als UIT_BESTAND bestaat (voor REPL-werk)."""
    global _wdt
    if UIT_BESTAND in os.listdir():
        print("WDT: uitgeschakeld via", UIT_BESTAND)
        return False
    _wdt = machine.WDT(timeout=MAX_TIMEOUT_MS)
    print("WDT: gewapend op", MAX_TIMEOUT_MS, "ms")
    return True


def feed():
    """Voed de watchdog. No-op zolang die niet gewapend is."""
    if _wdt is not None:
        _wdt.feed()


def sleep(seconden):
    """Blokkerende sleep die de watchdog blijft voeden. Voor pauzes > 8s."""
    einde = time.ticks_add(time.ticks_ms(), int(seconden * 1000))
    while time.ticks_diff(einde, time.ticks_ms()) > 0:
        feed()
        time.sleep_ms(200)
    feed()
