import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12,GPIO.OUT)
try:
    while(True):
        GPIO.output(12,True)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()