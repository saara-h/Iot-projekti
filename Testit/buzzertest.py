from __future__ import print_function

import time
import RPi.GPIO as GPIO

def main():
    from grove.helper import helper
    # helper.root_check()

    print("Insert Grove-Buzzer to Grove-Base-Hat slot PWM[12 13 VCC GND]")
    # Grove Base Hat for Raspberry Pi
    pin = 12
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)

    # create PWM instance
    pwm = GPIO.PWM(pin, 10)
    pwm.start(0) 

    chords = [16.35, 32.70, 65.41, 130.8, 261.6, 523.3, 1047, 2093, 4186]
    # Play sound (DO, RE, MI, etc.), pausing for 0.5 seconds between notes
    try:
        for note in chords:
            pwm.ChangeFrequency(note)
            pwm.ChangeDutyCycle(50)
            time.sleep(5) 
    finally:
        pwm.stop()
        GPIO.cleanup()

    print("Exiting application")

if __name__ == '__main__':
    main()
