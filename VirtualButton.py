import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(16,GPIO.OUT)
GPIO.setup(18,GPIO.OUT)
GPIO.setup(11,GPIO.OUT)
GPIO.setup(13,GPIO.OUT)
try:
    GPIO.output(16,True)
    while(True):
        print("High")
        pass
except KeyboardInterrupt:
    pass
finally:
    print("Low")
    GPIO.cleanup()