import firebase_admin
from firebase_admin import credentials, firestore
import RPi.GPIO as GPIO
import time

# GPIO Pin Setup
FAN_PIN = 5
LIGHT_PIN = 6

GPIO.setmode(GPIO.BCM)

GPIO.setup(FAN_PIN, GPIO.OUT)
GPIO.setup(LIGHT_PIN, GPIO.OUT)

# Initialize Firebase Admin SDK
cred = credentials.Certificate("/home/clara-capstone/Documents/capstone-app-59cf7.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://capstone-app-59cf7.firebaseio.com/'
})

db = firestore.client()

# collected is called "devices"
db_collect = db.collection("devices")

# within devices collection, device2 document is the fan
doc_ref_fan = db_collect.document("device2")

# within devices collection, device1 document is the light
doc_ref_light = db_collect.document("device1")

# Listener for Fan changes
def fan_listener(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        print(f"Fan Listener Snapshot: {doc.to_dict()}")  # Debugging: print the snapshot data
        fan_status = doc.get('Fan')
        if fan_status is not None:
            if fan_status:  # If fan is ON
                print("Fan on")
                GPIO.output(FAN_PIN, GPIO.LOW)  # Turn the fan on (active-low condition)
            else:  # If fan is OFF
                print("Fan off")
                GPIO.output(FAN_PIN, GPIO.HIGH)  # Turn the fan off (active-low condition)

# Listener for Light changes
def light_listener(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        print(f"Light Listener Snapshot: {doc.to_dict()}")  # Debugging: print the snapshot data
        light_status = doc.get('Living_Room_Light')
        if light_status is not None:
            if light_status:  # If light is ON
                print("Light on")
                GPIO.output(LIGHT_PIN, GPIO.LOW)  # Turn the light on (active-low condition)
            else:  # If light is OFF
                print("Light off")
                GPIO.output(LIGHT_PIN, GPIO.HIGH)  # Turn the light off (active-low condition)

# Attach listeners to Firestore documents
doc_ref_fan.on_snapshot(fan_listener)
doc_ref_light.on_snapshot(light_listener)

try:
    while True:
        # Keep the program running to listen for updates
        print("Listening for changes in Firestore...")
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting program now...")

    GPIO.output(FAN_PIN, GPIO.HIGH)
    print("turned off fan")

    GPIO.output(LIGHT_PIN, GPIO.HIGH)
    print("turned off light")

    GPIO.cleanup()  # Clean up GPIO resources
    print("GPIO cleanup complete")
