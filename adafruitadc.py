#!/usr/bin/python3

import signal
import sys
import time
import spidev
import math

from gpiozero import MCP3008



# Fixed resistor value in ohms
R1 = 100000.0

# Steinhart-Hart Coefficients
c1 = 0.76645043008e-03
c2 = 2.081779068e-04
c3 = 1.250512199e-07


def calculate_temperature(adc_value):
    # Calculate the thermistor resistance   
    voltage = adc_value * (3.3/ 255.0)  # Assuming 3.3V reference
    R2 = R1 * (3.3/ voltage - 1.0)

    # Calculate temperature using Steinhart-Hart equation
    logR2 = math.log(R2)
    temperature_kelvin = 1.0 / (c1 + c2 * logR2 + c3 * logR2**3)
    temperature_celsius = temperature_kelvin - 273.15
    print(f"ADC Value: {adc_value}")
    print(f"Voltage: {voltage}")
    print(f"Thermistor Resistance: {R2}")
    print(f"logR2: {logR2}")
    return temperature_celsius

if __name__ == '__main__':
    try:
        thermistor = MCP3008(0)
        while True:
            print(f"Temperature: {thermistor.value} ºC")
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nExiting...")
        
