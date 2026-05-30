from gpiozero import MCP3008
import board
from time import sleep
from adafruit_ads1x15 import ADS1115, AnalogIn, ads1x15
import numpy as np

i2c = board.I2C()
ads1115 = ADS1115(i2c)
ads1115_ch0 = AnalogIn(ads1115, ads1x15.Pin.A0)
ads1115.gain = 1

mcp3008 = MCP3008(1)
loop = 30
i = 0
var = 0
values = np.array([0,0],dtype=float)
while True:
    current_val = mcp3008.value*3.3
    ads_val = ads1115_ch0.voltage
    values[0] = current_val + values[0]
    values[1] = ads_val + values [1]
    i =i+1
    sleep(0.01)
    #print(f"Current = {current_val:.3f}, values = {values[0]:.3f}")
    if i>loop:
        values[:] = values/i
        #print(f"MCP3008 = {values[0]:.3f}")
        print(f"MCP3008 = {values[0]:.4f}, ADS1115 = {values[1]:.4f}")
        values[:] = 0
        #print(f"values = {values}")
        i = 0

# print(f"Average = {var/loop:.4f}")
