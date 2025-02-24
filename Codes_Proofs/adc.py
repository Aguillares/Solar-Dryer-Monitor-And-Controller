#!/usr/bin/python3

import signal
import sys
import time
import spidev
import math

# SPI Channel
spi_ch = 0

# Enable SPI
spi = spidev.SpiDev(0, spi_ch)
spi.max_speed_hz = 1200000

# Fixed resistor value in ohms
R1 = 100000.0

# Steinhart-Hart Coefficients
c1 = 0.76645043008e-03
c2 = 2.081779068e-04
c3 = 1.250512199e-07

def close(signal, frame):
    spi.close()
    sys.exit(0)

signal.signal(signal.SIGINT, close)

def get_adc(channel):
    """
    Read the ADC value from the MCP3008.
    """
    if channel < 0 or channel > 7:
        raise ValueError("ADC channel must be between 0 and 7.")

    # Construct the SPI command
    start_bit = 1
    single_mode = 1
    command = (start_bit << 2) | (single_mode << 1) | (channel >> 2)
    data = [(command << 4) | ((channel & 3) << 6), 0]

    # Send and receive data via SPI
    reply = spi.xfer2(data)

    # Combine the two bytes into a single integer (10 bits)
    adc_value = ((reply[0] & 3) << 8) | reply[1]
    return adc_value

def calculate_temperature(adc_value):
    """
    Convert the ADC value to temperature using the Steinhart-Hart equation.
    """
    if adc_value == 0:
        raise ValueError("ADC value is 0, possible open circuit.")

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
        while True:
            adc_value = get_adc(0)  # Reading from channel 0
            temperature = calculate_temperature(adc_value)
            print(f"Temperature: {round(temperature, 2)} ºC")
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nExiting...")
        spi.close()
