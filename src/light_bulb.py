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
        self.pwm.start(0)  # Start with 100% duty cycle (which is OFF with inverted logic)
        
        # Set initial brightness (default is 0%)
        self.change_brightness(pwm_val)
        print(f"Light bulb initialized on pin {self.LIGHT_PIN} with frequency {self.PWM_FREQ}Hz")
        
    def change_brightness(self, brightness_percent):
        # Clamp the brightness value between 0 and 100%
        brightness_percent = max(0, min(100, brightness_percent))

        # # Map 0-100 input range to 75-100 brightness range
        # if brightness_percent < 100:
        #     brightness_percent_new = (brightness_percent * 30 / 100) + 70
        # else:
        #     brightness_percent_new = 100
        
        # inverted_percent = 100 - brightness_percent_new


        # Apply the inverted duty cycle
        self.pwm.ChangeDutyCycle(brightness_percent)
        
        print(f"Brightness set to: {brightness_percent}% (PWM duty cycle: {brightness_percent}%)")
        time.sleep(0.1)

    def turn_light_off(self):
        # With inverted logic, 100% duty cycle turns the light off
        self.pwm.ChangeDutyCycle(0)
        print("Light turned off\n")
        
    def turn_light_on(self):
        # With inverted logic, 0% duty cycle is full brightness
        self.pwm.ChangeDutyCycle(100)
        print("Light turned on (full brightness)\n")
        
    def get_status(self):
        # Note: RPi.GPIO doesn't have a direct way to get the current duty cycle
        print("Current brightness status cannot be retrieved with RPi.GPIO")
        return None
        
    def cleanup(self):
        # Turn off the light and clean up GPIO
        self.turn_light_off()
        self.pwm.stop()
        GPIO.cleanup()
        print("Cleaned up resources.")