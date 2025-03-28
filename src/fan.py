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
        self.fan_mode = 0 # Start with off mode

        print(f"Fan initialized on pin {self.FAN_PIN} with frequency {self.PWM_FREQ}Hz")
        
    def change_fan_speed(self, speed_mode):
        # Ensure the speed mode value is within the valid range (0-2)
        speed_mode = max(0, min(2, speed_mode))

        # OFF
        if speed_mode == 0:
            speed_percent = 0

        # MEDIUM
        elif speed_mode == 1:
            speed_percent = 15

        # MAX
        else:
            speed_percent = 100
        
        # Apply the duty cycle
        self.pwm.ChangeDutyCycle(speed_percent)
        self.fan_mode = speed_mode

        print(f"Fan speed mode set to {speed_mode}% (PWM duty cycle: {speed_percent}%)")
        time.sleep(0.5)  # Give time for the change to take effect
        
    def turn_fan_off(self):
        # To turn off, we need to set the PWM to 100% (inverted logic)
        self.pwm.ChangeDutyCycle(0)

        # Update fan mode
        self.fan_mode = 0
        print("Fan turned off")
        
    def turn_fan_on(self):
        # To turn on fully, we need to set the PWM to 0% (inverted logic)
        self.pwm.ChangeDutyCycle(100)

        # Update fan mode
        self.fan_mode = 2
        print("Fan turned on at full speed")

    def get_status(self):
        print("Current fan speed status: ", self.fan_mode)
        return self.fan_mode
        
    def cleanup(self):
        self.turn_fan_off()
        self.pwm.stop()
        GPIO.cleanup()
        print("Cleaned up resources")