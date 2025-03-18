from temp_sensor import TempSensor
import time
import RPi.GPIO as GPIO

class Fan:
    def __init__(self, state = "off"):
        self.FAN_PIN = 5 # pin that fan is connected to
        GPIO.setmode(GPIO.BCM)  # set board pin reading to be the GPIO # ex. GPIO5 would be 5
        GPIO.setup(self.FAN_PIN, GPIO.OUT) # set GPIO5 to be an output
        self.state = state

    def turn_fan_on(self):
        # turn fan on
        GPIO.output(self.FAN_PIN, GPIO.LOW)
        time.sleep(1.25)

        # update state
        self.state = "on"
        print("Fan turned on \n")

    def turn_fan_off(self):
        #turn fan off
        GPIO.output(self.FAN_PIN, GPIO.HIGH)
        time.sleep(1.25)
    
        # update state
        self.state = "off"
        print("Fan turned off \n")

    def get_status(self):
        return self.state

    # automatically adjust the fan state based on a threshold temperature
    def adjust_temp(self, temp):
        # using temp sensor to get the current temp value
        if temp_sensor.temp > temp:
            self.turn_fan_on()
        else:
            self.turn_fan_off()