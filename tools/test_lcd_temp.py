"""Test LCD + DHT11: toont temperatuur en vochtigheid op het display."""

import time
import dht
from machine import I2C, Pin

# DHT11
sensor = dht.DHT11(Pin(16, Pin.IN, Pin.PULL_UP))

# LCD
LCD_CLEAR = 0x01
LCD_ENTRY_MODE = 0x06
LCD_DISPLAY_ON = 0x0C
LCD_FUNCTION_SET = 0x28
LCD_SET_DDRAM = 0x80
BACKLIGHT = 0x08
ENABLE = 0x04
RS = 0x01

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)

def write(data):
    i2c.writeto(0x27, bytes([data | BACKLIGHT]))

def pulse(data):
    write(data | ENABLE)
    time.sleep_us(500)
    write(data & ~ENABLE)
    time.sleep_us(100)

def send(value, mode=0):
    pulse(mode | (value & 0xF0))
    pulse(mode | ((value << 4) & 0xF0))

def cmd(c):
    send(c)

def init():
    time.sleep_ms(50)
    for _ in range(3):
        pulse(0x30)
        time.sleep_ms(5)
    pulse(0x20)
    cmd(LCD_FUNCTION_SET)
    cmd(LCD_DISPLAY_ON)
    cmd(LCD_ENTRY_MODE)
    clear()

def clear():
    cmd(LCD_CLEAR)
    time.sleep_ms(2)

def toon(r1, r2):
    clear()
    cmd(LCD_SET_DDRAM | 0x00)
    for ch in r1[:16]:
        send(ord(ch), RS)
    cmd(LCD_SET_DDRAM | 0x40)
    for ch in r2[:16]:
        send(ord(ch), RS)

init()
toon("Opstarten...", "")
time.sleep(2)

while True:
    sensor.measure()
    temp = sensor.temperature()
    vocht = sensor.humidity()
    toon(f"Temp: {temp} C", f"Vocht: {vocht} %")
    print(f"{temp} C  {vocht} %")
    time.sleep(2)
