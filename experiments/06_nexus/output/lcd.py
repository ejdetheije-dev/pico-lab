import time
from machine import I2C, Pin

LCD_CLEAR = 0x01
LCD_ENTRY_MODE = 0x06
LCD_DISPLAY_ON = 0x0C
LCD_FUNCTION_SET = 0x28
LCD_SET_DDRAM = 0x80
BACKLIGHT = 0x08
ENABLE = 0x04
RS = 0x01


class LCD:
    """LCD 1602 met PCF8574-backpack op I2C0."""

    def __init__(self, sda=0, scl=1, addr=0x27):
        self.i2c = I2C(0, sda=Pin(sda), scl=Pin(scl), freq=400_000)
        self.addr = addr
        self.backlight = True
        self._init()

    def _write(self, data):
        if self.backlight:
            data |= BACKLIGHT
        else:
            data &= ~BACKLIGHT
        self.i2c.writeto(self.addr, bytes([data]))

    def set_backlight(self, aan):
        """Zet de backlight aan of uit zonder de getoonde tekst te wissen."""
        self.backlight = aan
        self._write(0x00)

    def _pulse(self, data):
        self._write(data | ENABLE)
        time.sleep_us(500)
        self._write(data & ~ENABLE)
        time.sleep_us(100)

    def _send(self, value, mode=0):
        self._pulse(mode | (value & 0xF0))
        self._pulse(mode | ((value << 4) & 0xF0))

    def _cmd(self, cmd):
        self._send(cmd)

    def _init(self):
        time.sleep_ms(50)
        for _ in range(3):
            self._pulse(0x30)
            time.sleep_ms(5)
        self._pulse(0x20)
        self._cmd(LCD_FUNCTION_SET)
        self._cmd(LCD_DISPLAY_ON)
        self._cmd(LCD_ENTRY_MODE)
        self.clear()

    def clear(self):
        self._cmd(LCD_CLEAR)
        time.sleep_ms(2)

    def toon(self, regel1="", regel2=""):
        """Toon twee regels op het LCD."""
        self.clear()
        self._cmd(LCD_SET_DDRAM | 0x00)
        for ch in regel1[:16]:
            self._send(ord(ch), RS)
        self._cmd(LCD_SET_DDRAM | 0x40)
        for ch in regel2[:16]:
            self._send(ord(ch), RS)
