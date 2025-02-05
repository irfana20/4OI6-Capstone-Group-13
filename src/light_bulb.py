import time
import RPi.GPIO as GPIO

class LightBulb:
    def __init__(self, state = "off"):
        LIGHT_PIN = 6 # pin that light is connected to
        GPIO.setmode(GPIO.BCM) # set board pin reading to be the GPIO # ex. GPIO6 would be 6
        GPIO.setup(LIGHT_PIN, GPIO.OUT) # set GPIO6 to be an output
        self.state = state

    def turn_light_on(self):
        # turn light on
        GPIO.output(light_PIN, GPIO.HIGH)
        time.sleep(1.25)

        # update state
        self.state = "on"
        print("light turned on \n")

    def turn_light_off(self):
        #turn light off
        GPIO.output(light_PIN, GPIO.LOW)
        time.sleep(1.25)

        # update state
        self.state = "off"
        print("light turned off \n")

    def get_status(self):
        return self.state