"""Watchdog met expliciete deadline, gevoed door een timer.

De hardware-WDT van de RP2350 kan maximaal 8388 ms, terwijl een enkele
Supabase-call routinematig 6-13 s duurt (nieuwe TLS-handshake per request door
Connection: close). Direct voeden rond elke call gaf daarom valse resets:
timeout= begrenst per socket-operatie, niet de totale call, en de DNS-lookup
valt er helemaal buiten.

Daarom voedt een timer de WDT, maar alleen zolang de deadline niet verstreken
is; de loop schuift die deadline elke iteratie op met leef(). Blijft de loop
langer dan MARGE_S weg, dan stopt het voeden en reset de hardware het bord.
Gemeten 2026-07-27: een timer-callback vuurt ook tijdens een blokkerende
socket-read (18 ticks tijdens een blokkade van 19 s), dus dit werkt midden in
een hangende call.
"""

import machine
import os
import time

WDT_MS = 8388  # hardgrens van de RP2350-watchdog
TICK_MS = 1000  # hoe vaak de timer de deadline controleert
MARGE_S = 45  # hoe lang de loop mag wegblijven voordat het bord reset
UIT_BESTAND = "wdt_uit"

_wdt = None
_timer = None
_deadline = 0


def _tick(t):
    """Voed de WDT alleen zolang de loop nog leeft."""
    if time.ticks_diff(_deadline, time.ticks_ms()) > 0:
        _wdt.feed()


def leef(marge_s=MARGE_S):
    """Schuif de deadline op: de loop maakt nog voortgang."""
    global _deadline
    _deadline = time.ticks_add(time.ticks_ms(), int(marge_s * 1000))


def feed():
    """Alias van leef(), zodat supabase.py en ota.py voortgang kunnen melden."""
    leef()


def wapen():
    """Wapen de watchdog. Slaat over als UIT_BESTAND bestaat (voor REPL-werk)."""
    global _wdt, _timer
    if UIT_BESTAND in os.listdir():
        print("WDT: uitgeschakeld via", UIT_BESTAND)
        return False
    leef()
    _wdt = machine.WDT(timeout=WDT_MS)
    _timer = machine.Timer()
    _timer.init(period=TICK_MS, mode=machine.Timer.PERIODIC, callback=_tick)
    print("WDT: gewapend, loop mag", MARGE_S, "s wegblijven")
    return True


def sleep(seconden):
    """Blokkerende sleep die de deadline blijft opschuiven."""
    einde = time.ticks_add(time.ticks_ms(), int(seconden * 1000))
    while time.ticks_diff(einde, time.ticks_ms()) > 0:
        leef()
        time.sleep_ms(200)
    leef()
