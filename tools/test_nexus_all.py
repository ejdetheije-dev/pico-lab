"""Nexus volledige sensortest. Loopt alle componenten langs en rapporteert OK/FAIL."""

import time
from machine import Pin, ADC, I2C, PWM

results = []

def ok(naam):
    print(f"OK   {naam}")
    results.append((naam, True))

def fail(naam, reden):
    print(f"FAIL {naam}: {reden}")
    results.append((naam, False))


# --- DHT11 ---
try:
    import dht
    s = dht.DHT11(Pin(16, Pin.IN, Pin.PULL_UP))
    time.sleep(1)
    s.measure()
    t, h = s.temperature(), s.humidity()
    if 0 < t < 60 and 0 < h <= 100:
        ok(f"DHT11 ({t}C, {h}%)")
    else:
        fail("DHT11", f"waarden buiten bereik: {t}C {h}%")
except Exception as e:
    fail("DHT11", str(e))


# --- BMP180 ---
try:
    from sensors.bmp180 import BMP180
    i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)
    bmp = BMP180(i2c)
    druk = bmp.lees_druk()
    temp_bmp = bmp.lees_temperatuur()
    if 800 < druk < 1100:
        ok(f"BMP180 ({druk:.1f} hPa, {temp_bmp:.1f}C)")
    else:
        fail("BMP180", f"druk buiten bereik: {druk:.1f} hPa")
except Exception as e:
    fail("BMP180", str(e))


# --- LDR ---
try:
    ldr = ADC(Pin(26))
    raw = ldr.read_u16()
    if 1000 < raw < 64000:
        ok(f"LDR (raw={raw})")
    else:
        fail("LDR", f"waarde buiten bereik: {raw}")
except Exception as e:
    fail("LDR", str(e))


# --- HC-SR04 ---
try:
    trig = Pin(17, Pin.OUT)
    echo = Pin(18, Pin.IN)
    trig.low(); time.sleep_us(2)
    trig.high(); time.sleep_us(10)
    trig.low()
    timeout = time.ticks_add(time.ticks_us(), 30000)
    while echo.value() == 0:
        if time.ticks_diff(timeout, time.ticks_us()) <= 0:
            raise Exception("timeout wachten op echo")
        start = time.ticks_us()
    timeout = time.ticks_add(time.ticks_us(), 30000)
    while echo.value() == 1:
        if time.ticks_diff(timeout, time.ticks_us()) <= 0:
            raise Exception("timeout echo hoog")
        end = time.ticks_us()
    cm = (time.ticks_diff(end, start) * 0.0343) / 2
    if 2 < cm < 400:
        ok(f"HC-SR04 ({cm:.1f} cm)")
    else:
        fail("HC-SR04", f"afstand buiten bereik: {cm:.1f} cm")
except Exception as e:
    fail("HC-SR04", str(e))


# --- Buzzer ---
try:
    buz = PWM(Pin(9))
    buz.freq(880)
    buz.duty_u16(32768)
    time.sleep_ms(150)
    buz.duty_u16(0)
    buz.deinit()
    ok("Buzzer (kort gepiept)")
except Exception as e:
    fail("Buzzer", str(e))


# --- Relay / ventilator ---
try:
    relay = Pin(21, Pin.OUT)
    relay.low()
    relay.high()
    time.sleep_ms(500)
    relay.low()
    ok("Relay kanaal 2 (GPIO 21)")
except Exception as e:
    fail("Relay", str(e))


# --- Samenvatting ---
print()
print("=" * 30)
geslaagd = sum(1 for _, v in results if v)
print(f"Resultaat: {geslaagd}/{len(results)} OK")
if all(v for _, v in results):
    print("Alles werkt!")
else:
    for naam, v in results:
        if not v:
            print(f"  Controleer: {naam}")
