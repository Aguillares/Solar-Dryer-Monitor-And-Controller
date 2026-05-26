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
        # set scale ratio for paritcular channel and gain which is
        # used to calculate the conversion to units. Required argument is only
        # scale ratio. Without arguments 'channel' and 'gain_A' it sets
        # the ratio for current channel and gain.
    ratio = 1433.2647
    hx.set_scale_ratio(ratio) # Set ratio for current channel
    print('Ratio is set.')

   # Read data several time and return mean value
    # subtracted by offset and converted by scale ratio to
    # desired units. In this case grams.
    print("Data will be read in an infinite loop. To exit press 'CTRL + C'")
    input('Press Enter to beigin reading')
    print('Current weight on the scale in grams is: ')
    while True:
        print(hx.get_weight_mean(30),'g')
        
except (KeyboardInterrupt, SystemExit):
    print('Closing')
# except RuntimeWarning:
#     print('Hello dude')
finally:
    GPIO.cleanup()