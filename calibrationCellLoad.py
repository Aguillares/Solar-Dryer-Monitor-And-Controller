import RPi.GPIO as GPIO
from hx711 import HX711
import statistics

try:
    # set GPIO pin mode to BCM numbering
    # To create an object hx which represent the real hx711 chip.
    GPIO.setmode(GPIO.BCM) 
    hx = HX711(dout_pin = 21,
                  pd_sck_pin = 20,
                  )
    # Measure tare and save the value as offset for current channel
    # and gain selected. That means channel A and gain 128.
    
    err = hx.zero()
    # Check if it is successful
    if err:
        raise ValueError('Tare is unsuccessful')
    
    reading = hx.get_raw_data_mean(readings=100)
    # We need to check if we get a correct value or only False.
    if reading:
        # Now the value is close to 0
        print('Data subtracted by offset but still not converted to units:',reading)
    else:
        print('Invalid data ', reading)
    # In order to calculate the conversion ratio to some units, in this case is used grams.
    input('Put known weight on the scale and then press Enter')
    reading = hx.get_data_mean(readings=100)
    if reading:
        print('Mean value from HX711 subtracted by offset: ', reading)
        known_weight_grams = input('Write how many grams it was and press Enter: ')
        try:
            value = float(known_weight_grams)
            print(value,'grams')
        except ValueError:
            print('Expected integer or float and it was typed: ',known_weight_grams)
            
        # set scale ratio for paritcular channel and gain which is
        # used to calculate the conversion to units. Required argument is only
        # scale ratio. Without arguments 'channel' and 'gain_A' it sets
        # the ratio for current channel and gain.
        ratio = reading/value # Calculate the ratio for channel A and gain 128
        print(f"The ratio is {ratio}")
        hx.set_scale_ratio(ratio) # Set ratio for current channel
        print('Ratio is set.')
    else:
        raise ValueError('Cannot calculate mean value. Try debug mode. Variable reading: ', reading)
    
    # Read data several time and return mean value
    # subtracted by offset and converted by scale ratio to
    # desired units. In this case grams.
    print("Data will be read in an infinite loop. To exit press 'CTRL + C'")
    input('Press Enter to beigin reading')
    print('Current weight on the scale in grams is: ')
    while True:
        value = hx.get_weight_mean(30)
        if value >= 0:
            value=round(value,1)
        else:
            value = 0
        print(value,'g')
        
except (KeyboardInterrupt, SystemExit):
    print('Closing')
except RuntimeWarning:
    print("It wasn't closed properly previously")
finally:
    GPIO.cleanup()
