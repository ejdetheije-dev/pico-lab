"""BMP180 druk- en temperatuursensor via I2C."""

from machine import I2C, Pin
import time


class BMP180:
    ADRES = 0x77

    def __init__(self, i2c):
        self.i2c = i2c
        self._k = self._lees_kalibratie()

    def _lees_s16(self, msb, lsb):
        v = (msb << 8) | lsb
        return v - 65536 if v > 32767 else v

    def _lees_kalibratie(self):
        d = self.i2c.readfrom_mem(self.ADRES, 0xAA, 22)
        return {
            "AC1": self._lees_s16(d[0], d[1]),  "AC2": self._lees_s16(d[2], d[3]),
            "AC3": self._lees_s16(d[4], d[5]),  "AC4": (d[6] << 8) | d[7],
            "AC5": (d[8] << 8) | d[9],          "AC6": (d[10] << 8) | d[11],
            "B1":  self._lees_s16(d[12], d[13]),"B2":  self._lees_s16(d[14], d[15]),
            "MB":  self._lees_s16(d[16], d[17]),"MC":  self._lees_s16(d[18], d[19]),
            "MD":  self._lees_s16(d[20], d[21]),
        }

    def _lees_B5(self):
        self.i2c.writeto_mem(self.ADRES, 0xF4, bytes([0x2E]))
        time.sleep_ms(5)
        d = self.i2c.readfrom_mem(self.ADRES, 0xF6, 2)
        UT = (d[0] << 8) | d[1]
        k = self._k
        X1 = (UT - k["AC6"]) * k["AC5"] >> 15
        X2 = (k["MC"] << 11) // (X1 + k["MD"])
        return X1 + X2

    def lees_temperatuur(self):
        """Temperatuur in graden Celsius (float)."""
        return ((self._lees_B5() + 8) >> 4) / 10.0

    def lees_druk(self):
        """Luchtdruk in hPa (float)."""
        B5 = self._lees_B5()
        self.i2c.writeto_mem(self.ADRES, 0xF4, bytes([0x34]))
        time.sleep_ms(5)
        d = self.i2c.readfrom_mem(self.ADRES, 0xF6, 3)
        UP = ((d[0] << 16) | (d[1] << 8) | d[2]) >> 8
        k = self._k
        B6 = B5 - 4000
        X1 = (k["B2"] * (B6 * B6 >> 12)) >> 11
        X2 = k["AC2"] * B6 >> 11
        B3 = ((k["AC1"] * 4 + X1 + X2) + 2) >> 2
        X1 = k["AC3"] * B6 >> 13
        X2 = (k["B1"] * (B6 * B6 >> 12)) >> 16
        B4 = k["AC4"] * ((X1 + X2 + 2) // 4 + 32768) >> 15
        B7 = (UP - B3) * 50000
        p = (B7 * 2) // B4 if B7 < 0x80000000 else (B7 // B4) * 2
        X1 = (p >> 8) * (p >> 8)
        X1 = (X1 * 3038) >> 16
        X2 = (-7357 * p) >> 16
        return (p + ((X1 + X2 + 3791) >> 4)) / 100.0
