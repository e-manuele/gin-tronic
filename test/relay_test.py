from machine import Pin
import time

pin_relay = Pin(15, mode=Pin.OUT)

while True:
    print("Accendo")
    pin_relay.on()
    time.sleep_ms(500)
    pin_relay.off()
    print("Spengo")
    time.sleep_ms(500)