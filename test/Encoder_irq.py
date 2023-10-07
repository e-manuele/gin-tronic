import time
from machine import Pin
from rotary_irq_rp2 import RotaryIRQ

button_pin = Pin(2, Pin.IN, Pin.PULL_UP) 
r = RotaryIRQ(
    pin_num_clk=1,
    pin_num_dt=0,
    reverse=False,
    incr=1,
    range_mode=RotaryIRQ.RANGE_UNBOUNDED,
    pull_up=True,
    half_step=False,
)

val_old = r.value()
while True:
    val_new = r.value()
    if not button_pin.value():
        print("Encoder button pressed")
    if val_old != val_new:
        val_old = val_new
        print("step =", val_new)
    time.sleep_ms(50)