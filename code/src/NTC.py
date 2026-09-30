import time
import board
import math
from adafruit_ads1x15 import ADS1115, AnalogIn, ads1x15 

def avg_result(channels):
    total_readings = int(30)
    values = [0]*len(channels)
    for _ in range(total_readings):
        for i,channel in enumerate(channels):
            values[i]=channel.value +values[i]

    return [value // total_readings for value in values]

def get_temperature(bits_array:list[int],full_range:int):
    R2_array = [R1*(full_range//bits-1) for bits in bits_array ]
    logR2_array = [math.log10(R2) for R2 in R2_array ]
    # Equation S-H
    T_array = [1.0 /(A + B*logR2 + C*logR2**3) for logR2 in logR2_array]
    return [T - 273.15 for T in T_array]


# Importing board
i2c = board.I2C()
# Creaing a instance of  ADS1115 ADC (16 bit) instance
adc = ADS1115(i2c)
adc.gain = 1
# Constants
FULL_RANGE = 32767
R1 = 100000
A = 0.6991663435*10**-3
B = 2.175231274*10**-4
C = 0.9757198585*10**-7
# To calculate the constants.
# http://www.thinksrs.com/downloads/programs/therm%20calc/ntccalibrator/ntccalculator.html
num_sensors = 1
channels = [None] *num_sensors
for num in range(num_sensors):
    channels[num] = AnalogIn(adc,num)

# Choose a gain of 1 for reading voltages from 0 to 4.09 V
# Or pick a different gain to change the range of voltages that are read:
# - 2/3 = +/-6.144V
# -   1 = +/-4.096V
# -   2 = +/-2.048V
# -   4 = +/-1.024V
# -   8 = +/-0.512V
# -  16 = +/-0.256V     


print("Reading ADS1x15 values, press Ctrl-C to quit...")
# Printing nice channel column headers.
for i in range(num_sensors):
    print("| {:>6} ".format(i),end='')
print("|")
print("-"*37)

# Main loop

while True:
    # Read all the ADC channel values in list
    avg_results = avg_result(channels)

    for channel in channels:
        # Read the specified ADC channel using the previously gain value
        print("| {:>6.4} ".format(channel.value),end='')
    print("|")

    time.sleep(0.5)