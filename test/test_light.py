import RPi.GPIO as GPIO
import time

# Clean up
GPIO.cleanup()

# Set up
GPIO.setmode(GPIO.BCM)
GPIO.setup(6, GPIO.OUT)

print("Light ON")
GPIO.output(6, GPIO.LOW)  # Assuming LOW turns it on based on your inverted logic
time.sleep(5)

print("Light OFF")
GPIO.output(6, GPIO.HIGH)  # Assuming HIGH turns it off
time.sleep(2)

# Clean up
GPIO.cleanup()