#by StSkanta (TechCree) 838375

import machine
from machine import Pin
import utime
import time
import clock
import os

buzzer = Pin(21, Pin.OUT)

buzzer.value(1)
utime.sleep(1)
buzzer.value(0)
utime.sleep(1)

#Welcome Ende
led14.value(0)
led09.value(0)
led13.value(0)
led10.value(0)
#utime.sleep(1)

exec(open('clock.py').read())