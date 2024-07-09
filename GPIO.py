import RPi.GPIO as GPIO
GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.OUT)
GPIO.setup(4, GPIO.OUT)

class Lights:
    def on(pin):
        GPIO.output(pin, GPIO.HIGH)

    def off(pin):
        GPIO.output(pin, GPIO.LOW)