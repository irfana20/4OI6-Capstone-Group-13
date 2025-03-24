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
    def __init__(self, connected, fan1, bed_fan, light1, bed_light):
        # Initialize Firebase Admin SDK
        cred = credentials.Certificate("/home/clara-capstone/Documents/capstone-app-59cf7.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://capstone-app-59cf7.firebaseio.com/'
        })
        
        self.connected = connected
        self.fan1 = fan1
        self.bed_fan = bed_fan
        self.light1 = light1
        self.bed_light = bed_light

        # set database "db" to firestore client
        self.db = firestore.client()

        # collected is called "devices" for fan/light
        self.db_collect = self.db.collection("devices")

        # within devices collection, device1 document is the living room light
        self.doc_ref_light = self.db_collect.document("device1")

        # within devices collection, device2 document is the fan
        self.doc_ref_fan = self.db_collect.document("device2")

        # within devices collection, device3 document is the thermostat
        self.doc_ref_thermostat = self.db_collect.document("device3")

        # within devices collection, device4 document is the bedroom light
        self.doc_ref_bed_light = self.db_collect.document("device4")

        # within devices collection, device2 document is the bedroom fan
        self.doc_ref_bed_fan = self.db_collect.document("device5")


        # collected is called "settings" for home/away mode
        self.db_settings = self.db.collection("settings")

        # within settings collection, awayMode document has the variable for isAway
        self.doc_ref_away = self.db_settings.document("awayMode")

    def initialize_firebase(self):
        self.connected = True
    
    # Listener for Fan changes
    def fan_listener(self, doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            print(f"Fan Listener Snapshot: {doc.to_dict()}")  # Debugging: print the snapshot data
            fan_status = doc.get('Fan')
            if fan_status is not None:
                if fan_status:  # If fan is not 0
                    print(f"Fan on at speed mode: {fan_status}")
                    self.fan1.change_fan_speed(fan_status)  # Turn the fan on (active-low condition)
                else:  # If fan is OFF
                    print("Fan off")
                    self.fan1.turn_fan_off()  # Turn the fan off (active-low condition)

    # Listener for living room light changes
    def light_listener(self, doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            print(f"Light Listener Snapshot: {doc.to_dict()}")  # Debugging: print the snapshot data
            light_status = doc.get('Living_Room_Light')
            if light_status is not None:
                if light_status:  # If light is ON
                    print(f"Light on at: {light_status}")
                    self.light1.change_brightness(light_status)  # Turn the light on (active-low condition)
                else:  # If light is OFF
                    print("Light off")
                    self.light1.turn_light_off()  # Turn the light off (active-low condition)

    # Listener for bedroom fan changes
    def bed_fan_listener(self, doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            print(f"Bedroom Fan Listener Snapshot: {doc.to_dict()}")  # Debugging: print the snapshot data
            fan_status = doc.get('Bedroom_Fan')
            if fan_status is not None:
                if fan_status:  # If fan is not 0
                    print(f"Bedroom Fan an on at speed mode: {fan_status}")
                    self.bed_fan.change_fan_speed(fan_status)  # Turn the fan on (active-low condition)
                else:  # If fan is OFF
                    print("Bedroom Fan off")
                    self.bed_fan.turn_fan_off()  # Turn the fan off (active-low condition)

    # Listener for bedroom light changes
    def bed_light_listener(self, doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            print(f"Bedroom Light Listener Snapshot: {doc.to_dict()}")  # Debugging: print the snapshot data
            light_status = doc.get('Bedroom_Light')
            if light_status is not None:
                if light_status:  # If light is ON
                    print(f"Bedroom Light on at: {light_status}")
                    self.bed_light.change_brightness(light_status)  # Turn the light on (active-low condition)
                else:  # If light is OFF
                    print("Bedroom Light off")
                    self.bed_light.turn_light_off()  # Turn the light off (active-low condition)
    
    def activate_away_mode(self, away):
        if(away == True):
            # check motion detection
            return

    # Listener for awayMode changes
    def away_mode_listener(self, doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            print(f"AwayMode Listener Snapshot: {doc.to_dict()}")  # Debugging: print the snapshot data
            away_status = doc.get('isAway')
            if away_status is not None:
                if away_status:  # If away mode is ON
                    print(f"Away mode active: {away_status}")
                    self.activate_away_mode(True)
                else:  # If away mode is OFF (i.e. home)
                    print(f"Away mode not active: {away_status}")
                    self.activate_away_mode(False)

    # Listener for thermostat changes
    def thermo_listener(self, doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            print(f"Thermostat Listener Snapshot: {doc.to_dict()}")  # Debugging: print the snapshot data
            thermo_status = doc.get('Thermostat')
            if thermo_status is not None:
                if thermo_status:
                    print(f"Thermostat reading: {thermo_status}")
                    self.bed_light.change_brightness(thermo_status)  # Turn the light on (active-low condition)

    def connect_listeners(self):
        # Attach listeners to Firestore documents
        self.doc_ref_fan.on_snapshot(self.fan_listener)
        self.doc_ref_light.on_snapshot(self.light_listener)
        self.doc_ref_away.on_snapshot(self.away_mode_listener)
        self.doc_ref_bed_fan.on_snapshot(self.bed_fan_listener)
        self.doc_ref_bed_light.on_snapshot(self.bed_light_listener)
        self.doc_ref_thermostat.on_snapshot(self.thermo_listener)

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