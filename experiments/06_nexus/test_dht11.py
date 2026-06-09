import dht
from machine import Pin
import time

sensor = dht.DHT11(Pin(16, Pin.IN, Pin.PULL_UP))

while True:
    try:
        sensor.measure()
        print("Temp:", sensor.temperature(), "C  Vocht:", sensor.humidity(), "%")
    except OSError as e:
        print("Fout:", e)
    time.sleep(2)
