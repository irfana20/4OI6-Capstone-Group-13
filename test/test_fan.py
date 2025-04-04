import RPi.GPIO as GPIO
import time

# Clean up
GPIO.cleanup()

FAN_PIN = 5

# Set up
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT)

print("Fan ON")
GPIO.output(FAN_PIN, GPIO.HIGH)  # Assuming HIGH turns it off
time.sleep(5)

print("Fan OFF")
GPIO.output(FAN_PIN, GPIO.LOW)  # Assuming LOW turns it on based on your inverted logic
time.sleep(5)

# Clean up
GPIO.cleanup()