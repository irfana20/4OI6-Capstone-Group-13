import RPi.GPIO as GPIO
import time

# Clean up
GPIO.cleanup()

# Set up
GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.OUT)

print("Fan ON")
GPIO.output(5, GPIO.HIGH)  # Assuming HIGH turns it off
time.sleep(2)

print("Fan OFF")
GPIO.output(5, GPIO.LOW)  # Assuming LOW turns it on based on your inverted logic
time.sleep(5)

# Clean up
# GPIO.cleanup()