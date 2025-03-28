import time
import RPi.GPIO as GPIO

class LightBulb:
    def __init__(self,  pin, pwm_val=0, freq=70):
        # Pin that the light is connected to
        self.LIGHT_PIN = pin
        self.PWM_FREQ = freq
        
        # Use BCM numbering
        GPIO.setmode(GPIO.BCM)
        
        # Set pin as output
        GPIO.setup(self.LIGHT_PIN, GPIO.OUT)
        
        # Initialize PWM
        self.pwm = GPIO.PWM(self.LIGHT_PIN, self.PWM_FREQ)
        self.pwm.start(0)  # Start with 0% duty cycle (which is off)
        self.light_mode = 0 # Start with light mode set to off
        
        # Set initial brightness (default is 0%)
        self.change_brightness(pwm_val)
        print(f"Light bulb initialized on pin {self.LIGHT_PIN} with frequency {self.PWM_FREQ}Hz")
        
    def change_brightness(self, mode):
        # Clamp the brightness value between 0 and 100%
        brightness_percent = max(0, min(2, mode))

        if(mode == 0):
            brightness_percent = 0
        
        elif (mode == 1):
            brightness_percent = 40
        
        else:
            brightness_percent = 60

        # Apply the duty cycle
        self.pwm.ChangeDutyCycle(brightness_percent)

        # Update light mode
        self.light_mode = mode
        
        print(f"Brightness mode set to: {mode}% (PWM duty cycle: {brightness_percent}%)")
        time.sleep(0.1)

    def turn_light_off(self):
        # 0% turn off light
        self.pwm.ChangeDutyCycle(0)
        self.light_mode = 0
        print("Light turned off\n")
        
    def turn_light_on(self):
        # Max brightness set to 60% for on
        self.pwm.ChangeDutyCycle(60)
        self.light_mode = 2
        print("Light turned on (full brightness)\n")
        
    def get_status(self):
        print("Current brightness status: ", self.light_mode)
        return self.light_mode
        
    def cleanup(self):
        # Turn off the light and clean up GPIO
        self.turn_light_off()
        self.pwm.stop()
        GPIO.cleanup()
        print("Cleaned up resources.")