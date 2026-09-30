import time
import board
import adafruit_ads1x15 import ADS1115, AnalogIn, ads1x15 

# Importing board
i2c = board.I2C()
# Creaing a instance of  ADS1115 ADC (16 bit) instance
adc = ADS1115(i2c)
adc.gain = 1
channels = [None] *4
for num in range(4):
    channels[num] = exec(f"AnalogIn(adc,ads1x15.Pin.A{num})")

# Choose a gain of 1 for reading voltages from 0 to 4.09 V
# Or pick a different gain to change the range of voltages that are read:
# - 2/3 = +/-6.144V
# -   1 = +/-4.096V
# -   2 = +/-2.048V
# -   4 = +/-1.024V
# -   8 = +/-0.512V
# -  16 = +/-0.256V     


print("Reading ADS1x15 values, press Ctrl-C  to quit...")
# Printing nice channel column headers.
print("| {0:>6} | {1:>6} | {2:>6} | {3:>6} |".format(*range(4)))
print("-"*37)

# Main loop

while True:
    # Read all the ADC channel values in list
    values = [0]*4
    for i in range(4):
        # Read the specified ADC channel using the previously gain value
        values[i] = channels[i].value

    print("| {0:>6} | {1:>6} | {2:>6} | {3:>6} |".format(*values))
    time.sleep(0.5)