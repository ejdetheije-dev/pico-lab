"""Helper voor het LCD 1602 via PCF8574 I2C-backpack.

Minimaal: init, schrijven van een regel, scherm wissen. Geen zware
library — alleen wat we nodig hebben in deze experimenten.
"""

import time
from machine import I2C, Pin


LCD_CLEAR = 0x01
LCD_HOME = 0x02
LCD_ENTRY_MODE = 0x06
LCD_DISPLAY_ON = 0x0C
LCD_FUNCTION_SET = 0x28
LCD_SET_DDRAM = 0x80

BACKLIGHT = 0x08
ENABLE = 0x04
RS = 0x01


class Lcd1602:
    """LCD 1602 met PCF8574-backpack op I2C."""

    def __init__(self, sda=0, scl=1, addr=0x27, freq=400_000):
        self.i2c = I2C(0, sda=Pin(sda), scl=Pin(scl), freq=freq)
        self.addr = addr
        self._init_display()

    def _write_byte(self, data):
        self.i2c.writeto(self.addr, bytes([data | BACKLIGHT]))

    def _pulse(self, data):
        self._write_byte(data | ENABLE)
        time.sleep_us(500)
        self._write_byte(data & ~ENABLE)
        time.sleep_us(100)

    def _send(self, value, mode=0):
        high = mode | (value & 0xF0)
        low = mode | ((value << 4) & 0xF0)
        self._pulse(high)
        self._pulse(low)

    def _command(self, cmd):
        self._send(cmd, 0)

    def _data(self, value):
        self._send(value, RS)

    def _init_display(self):
        time.sleep_ms(50)
        for _ in range(3):
            self._pulse(0x30)
            time.sleep_ms(5)
        self._pulse(0x20)
        self._command(LCD_FUNCTION_SET)
        self._command(LCD_DISPLAY_ON)
        self._command(LCD_ENTRY_MODE)
        self.clear()

    def clear(self):
        """Wis het scherm en zet de cursor linksboven."""
        self._command(LCD_CLEAR)
        time.sleep_ms(2)

    def move_to(self, col, row):
        """Verplaats de cursor naar kolom (0-15), rij (0-1)."""
        offset = 0x40 if row else 0x00
        self._command(LCD_SET_DDRAM | (col + offset))

    def write(self, text):
        """Schrijf tekst vanaf de huidige cursorpositie."""
        for ch in text:
            self._data(ord(ch))

    def show(self, line1="", line2=""):
        """Toon twee regels (handig voor snel updaten)."""
        self.clear()
        self.move_to(0, 0)
        self.write(line1[:16])
        self.move_to(0, 1)
        self.write(line2[:16])
