"""BMP180 sensortest — leest temperatuur en luchtdruk via I2C0 (SDA=0, SCL=1)."""

from machine import I2C, Pin
import time

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)

def lees_s16(msb, lsb):
    v = (msb << 8) | lsb
    return v - 65536 if v > 32767 else v

def lees_kalibratie():
    d = i2c.readfrom_mem(0x77, 0xAA, 22)
    return {
        "AC1": lees_s16(d[0], d[1]),  "AC2": lees_s16(d[2], d[3]),
        "AC3": lees_s16(d[4], d[5]),  "AC4": (d[6] << 8) | d[7],
        "AC5": (d[8] << 8) | d[9],    "AC6": (d[10] << 8) | d[11],
        "B1":  lees_s16(d[12], d[13]),"B2":  lees_s16(d[14], d[15]),
        "MB":  lees_s16(d[16], d[17]),"MC":  lees_s16(d[18], d[19]),
        "MD":  lees_s16(d[20], d[21]),
    }

def lees_temperatuur(k):
    i2c.writeto_mem(0x77, 0xF4, bytes([0x2E]))
    time.sleep_ms(5)
    d = i2c.readfrom_mem(0x77, 0xF6, 2)
    UT = (d[0] << 8) | d[1]
    X1 = (UT - k["AC6"]) * k["AC5"] >> 15
    X2 = (k["MC"] << 11) // (X1 + k["MD"])
    B5 = X1 + X2
    return (B5 + 8) >> 4, B5

def lees_druk(k, B5):
    i2c.writeto_mem(0x77, 0xF4, bytes([0x34]))
    time.sleep_ms(5)
    d = i2c.readfrom_mem(0x77, 0xF6, 3)
    UP = ((d[0] << 16) | (d[1] << 8) | d[2]) >> 8
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
    return p + ((X1 + X2 + 3791) >> 4)

k = lees_kalibratie()
print("Kalibratie geladen")

while True:
    temp_raw, B5 = lees_temperatuur(k)
    druk_pa = lees_druk(k, B5)
    print("Temp: %.1f C  Druk: %.1f hPa" % (temp_raw / 10, druk_pa / 100))
    time.sleep(2)
