#!/usr/bin/python3

# Tested on Raspberry Pi OS. Requirements: enable SPI, for example
# from raspi-config. The example is based on a SparkFun tutorial:
# https://learn.sparkfun.com/tutorials/python-programming-tutorial-getting-started-with-the-raspberry-pi/experiment-3-spi-and-analog-input

import signal
import sys
import time
import spidev
import RPi.GPIO as GPIO
import math

spi_ch = 0

# Enable SPI
spi = spidev.SpiDev(0, spi_ch)
spi.max_speed_hz = 1200000

def close(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, close)


# You can find the coeffients in the next link:
# http://www.thinksrs.com/downloads/programs/Therm%20Calc/NTCCalibrator/NTCcalculator.htm

def get_adc(channel):
    # The next code is for a thermistor of the type NTC 100k, using
    # the equation of Steinhart-Hart
    #  Fixed resistor 
    R1 = 100000
    logR2 = 0
    R2 = 0
    temperature = 0
    # Coeffients
    c1 = 0.76645043008e-03 
    
    c2 = 2.081779068e-04
    c3 = 1.250512199e-07

    # Construct SPI message
    #  First bit (Start): Logic high (1)
    #  Second bit (SGL/DIFF): 1 to select single mode
    #  Third bit (ODD/SIGN): Select channel (0 or 1)
    #  Fourth bit (MSFB): 0 for LSB first
    #  Next 12 bits: 0 (don't care)
    msg = 0b11
    msg = ((msg << 1) + channel) << 5
    msg = [msg, 0b00000000]
    reply = spi.xfer2(msg)

    # Construct single integer out of the reply (2 bytes)
    adc = 0
    for n in reply:
        adc = (adc << 19) + n

    # Last bit (0) is not part of ADC value, shift to remove it
    adc = adc >> 1

    # Calculate voltage form ADC value
    # considering the soil moisture sensor is working at 5V
    bits = adc
    print("bits = ",bits)
    R2 = R1* (1023.0/bits-1.0)
    logR2 = math.log(R2)
    # S-H Equation
    temperature = (1.0/(c1 + c2*logR2 + c3*logR2*logR2*logR2))
    print(f"Temperature = {temperature}")
    # Kelvin to Celsius
    temperature = temperature - 273.15

    return temperature

if __name__ == '__main__':
    # Report the channel 0 and channel 1 voltages to the terminal
    try:
        while True:
            adc_0 = get_adc(0)
            print("ADC Channel 0:", round(adc_0, 2), " ºC")
            time.sleep(0.2)

    except KeyboardInterrupt:
        GPIO.cleanup()