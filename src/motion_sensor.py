import RPi.GPIO as GPIO
from gpiozero import MotionSensor, LED

class Motion_Sensor:
    def __init__(self, pin=17, enable=True, motion_detected = False):
        LED_PIN = pin # pin that led is connected to
        MOTION_PIN = 4 # pin that motion sensor is connected to
        GPIO.setmode(GPIO.BCM) # set board pin reading to be the GPIO # ex. GPIO5 would be 5
        GPIO.setup(LED_PIN, GPIO.OUT) # set GPIO17 to be an output
        GPIO.setup(MOTION_PIN, GPIO.IN) # set GPIO4 to be an input

        self.led = LED(LED_PIN)
        self.pir = MotionSensor(MOTION_PIN)
        self.motion = motion_detected
        self.active = enable

    def check_motion(self):
        self.pir.wait_for_motion(timeout = 1)

        # if value obtained, there was movement detected
        if self.pir.value:
            self.led.on()
            self.motion = True
            print ("Movement detected")
            return ("Movement detected")

        # otherwise there was no movement
        else:
            self.led.off()
            self.motion = False
            print("No movement")
            return ("No movement")