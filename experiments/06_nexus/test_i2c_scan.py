from machine import I2C, Pin

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
adressen = i2c.scan()

if adressen:
    for a in adressen:
        print("Gevonden:", hex(a))
else:
    print("Geen I2C-apparaten gevonden")
