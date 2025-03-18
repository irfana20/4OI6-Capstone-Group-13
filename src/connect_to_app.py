import firebase_admin
from firebase_admin import credentials, firestore
from fan import Fan
from light_bulb import LightBulb
import time
import RPi.GPIO as GPIO
import multiprocessing
from datetime import datetime

class ConnectToApp:

    # fan and light inputs must be objects of the fan and light classes
    def __init__(self, connected, fan1, light1):
        # Initialize Firebase Admin SDK
        cred = credentials.Certificate("/home/clara-capstone/Documents/capstone-app-59cf7.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://capstone-app-59cf7.firebaseio.com/'
        })
        
        self.connected = connected
        self.fan1 = fan1
        self.light1 = light1

        # set database "db" to firestore client
        self.db = firestore.client()

        # collected is called "devices"
        self.db_collect = self.db.collection("devices")

        # within devices collection, device2 document is the fan
        self.doc_ref_fan = self.db_collect.document("device2")

        # within devices collection, device1 document is the light
        self.doc_ref_light = self.db_collect.document("device1")

    def initialize_firebase(self):
        self.connected = True
    
    # Listener for Fan changes
    def fan_listener(self, doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            print(f"Fan Listener Snapshot: {doc.to_dict()}")  # Debugging: print the snapshot data
            fan_status = doc.get('Fan')
            if fan_status is not None:
                if fan_status:  # If fan is ON
                    print("Fan on")
                    self.fan1.turn_fan_on()  # Turn the fan on (active-low condition)
                else:  # If fan is OFF
                    print("Fan off")
                    self.fan1.turn_fan_off()  # Turn the fan off (active-low condition)

    # Listener for Light changes
    def light_listener(self, doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            print(f"Light Listener Snapshot: {doc.to_dict()}")  # Debugging: print the snapshot data
            light_status = doc.get('Living_Room_Light')
            if light_status is not None:
                if light_status:  # If light is ON
                    print("Light on")
                    self.light1.turn_light_on()  # Turn the light on (active-low condition)
                else:  # If light is OFF
                    print("Light off")
                    self.light1.turn_light_off()  # Turn the light off (active-low condition)

    def connect_listeners(self):
        # Attach listeners to Firestore documents
        self.doc_ref_fan.on_snapshot(self.fan_listener)
        self.doc_ref_light.on_snapshot(self.light_listener)

        try:
            while True:
                # Keep the program running to listen for updates
                print("Listening for changes in Firestore...")
                time.sleep(1)

        except KeyboardInterrupt:
            print("Exiting program now...")

            self.fan1.turn_fan_off()
            print("turned off fan")

            self.light1.turn_light_off()
            print("turned off light")

    def send_alert(self, message, doc_name=None):
        # if no document name is given
        if doc_name is None:
            # Use a timestamp-based document name
            doc_name = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        alert_data = {
            "message": message,
            "notification": {
                "title": "Motion Detected",
                "body": "Known vs unknown!"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # save the alert to firestore database under the alerts collection
        self.db.collection("alerts").document(doc_name).set(alert_data)
        print(f"Alert sent successfully with document name: {doc_name}")

    def is_connected(self):
        return self.connected