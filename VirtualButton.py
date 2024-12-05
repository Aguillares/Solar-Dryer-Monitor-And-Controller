import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12,GPIO.OUT)
try:
    GPIO.output(12,True)
    while(True):
        pass
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()