import board
from time import sleep
from adafruit_ads1x15 import ADS1115, AnalogIn, ads1x15
import numpy as np

i2c = board.I2C()
ads1115 = ADS1115(i2c)
ads1115_ch0 = AnalogIn(ads1115, ads1x15.Pin.A0)
ads1115.gain = 1

loop = 30
i = 0
var = 0
values = np.array([0,0],dtype=float)
while True:
    ads_val = ads1115_ch0.voltage
    values[1] = ads_val + values [1]
    i =i+1
    sleep(0.01)
    if i>loop:
        values[:] = values/i
        print(f"ADS1115 = {values[1]:.3f}")
        values[:] = 0
        i = 0
