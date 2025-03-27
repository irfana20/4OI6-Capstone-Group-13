import RPi.GPIO as GPIO
import time

# Clean up
GPIO.cleanup()

LIGHT_PIN = 6

# Set up
GPIO.setmode(GPIO.BCM)
GPIO.setup(LIGHT_PIN, GPIO.OUT)

print("Light ON")
GPIO.output(LIGHT_PIN, GPIO.HIGH)  # Assuming LOW turns it on based on your inverted logic
time.sleep(5)

print("Light OFF")
GPIO.output(LIGHT_PIN, GPIO.LOW)  # Assuming HIGH turns it off
time.sleep(2)

# Clean up
GPIO.cleanup()