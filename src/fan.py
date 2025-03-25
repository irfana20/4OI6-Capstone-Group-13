import RPi.GPIO as GPIO
import time

class Fan:
    def __init__(self, pin, freq=20):
        self.FAN_PIN = pin
        self.PWM_FREQ = freq
        
        # Set up GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.FAN_PIN, GPIO.OUT)
        
        # Initialize PWM
        self.pwm = GPIO.PWM(self.FAN_PIN, self.PWM_FREQ)
        self.pwm.start(0)  # Start with 0% duty cycle
        print(f"Fan initialized on pin {self.FAN_PIN} with frequency {self.PWM_FREQ}Hz")
        
    def change_fan_speed(self, speed_mode):
        # Ensure the speed mode value is within the valid range (0-5)
        speed_mode = max(0, min(3, speed_mode))

        if speed_mode == 0:
            speed_percent = 0

        elif speed_mode == 1:
            speed_percent = 32

        elif speed_mode == 2:
            speed_percent = 67

        elif speed_mode == 3:
            speed_percent = 100
        
        # Invert the percentage (100% becomes 0%, 0% becomes 100%)
        inverted_percent = 100 - speed_percent
        
        # Apply the duty cycle
        self.pwm.ChangeDutyCycle(inverted_percent)
        print(f"Fan speed set to {speed_percent}% (PWM duty cycle: {inverted_percent}%)")
        time.sleep(0.5)  # Give time for the change to take effect
        
    def turn_fan_off(self):
        # To turn off, we need to set the PWM to 100% (inverted logic)
        self.pwm.ChangeDutyCycle(100)
        print("Fan turned off")
        
    def turn_fan_on(self):
        # To turn on fully, we need to set the PWM to 0% (inverted logic)
        self.pwm.ChangeDutyCycle(0)
        print("Fan turned on at full speed")
        
    def cleanup(self):
        self.turn_fan_off()
        self.pwm.stop()
        GPIO.cleanup()
        print("Cleaned up resources")