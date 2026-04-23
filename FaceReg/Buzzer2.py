from __future__ import print_function

import time
import RPi.GPIO as GPIO

def play_tone(tone,dur):
    from grove.helper import helper
    
    pin = 12
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)

    pwm = GPIO.PWM(pin, 10)
    pwm.start(0) 

    try:
        for note in tone:
            pwm.ChangeFrequency(note)
            pwm.ChangeDutyCycle(95)
            time.sleep(dur) 
    finally:
        pwm.stop()
        GPIO.output(pin,GPIO.LOW)

    print("Exiting application")

