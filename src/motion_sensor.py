import RPi.GPIO as GPIO
from gpiozero import MotionSensor, LED

class Motion_Sensor:
    def __init__(self, motion_detected = False):
        LED_PIN = 17 # pin that led is connected to
        MOTION_PIN = 4 # pin that motion sensor is connected to
        GPIO.setmode(GPIO.BCM) # set board pin reading to be the GPIO # ex. GPIO5 would be 5
        GPIO.setup(LED_PIN, GPIO.OUT) # set GPIO17 to be an output
        GPIO.setup(MOTION_PIN, GPIO.IN) # set GPIO4 to be an input

        led = LED(LED_PIN)
        pir = MotionSensor(MOTION_PIN)
        self.motion = motion_detected

    def check_motion(self):
        pir.wait_for_motion(timeout = 1)

        # if value obtained, there was movement detected
        if pir.value:
            led.on()
            self.motion = True
            print ("Movement detected")

        # otherwise there was no movement
        else:
            led.off()
            self.motion = False
            print("No movement")