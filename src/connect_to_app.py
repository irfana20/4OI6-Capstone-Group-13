import firebase_admin
from firebase_admin import credentials, firestore
import time
import RPi.GPIO as GPIO
from datetime import datetime
from get_db import GetDB

class ConnectToApp:

    # fan and light inputs must be objects of the fan and light classes
    def __init__(self, living_fan, bed_fan, living_light, bed_light, entrance_light, motion_sensor):        
        self.living_fan = living_fan
        self.bed_fan = bed_fan
        self.living_light = living_light
        self.bed_light = bed_light
        self.entrance_light = entrance_light
        self.motion_sensor = motion_sensor

        # set database "db" to firestore client
        self.db, self.bucket = GetDB().get_db_bucket

        # collected is called "devices" for fan/light
        self.db_collect = self.db.collection("devices")

        # within devices collection, device1 document is the living room light
        self.doc_ref_living_light = self.db_collect.document("device1")

        # within devices collection, device2 document is the fan
        self.doc_ref_living_fan = self.db_collect.document("device2")

        # within devices collection, device3 document is the temp variables
        self.doc_ref_current_temp = self.db_collect.document("device3")
        self.doc_ref_desired_temp = self.db_collect.document("device3")

        # within devices collection, device4 document is the bedroom light
        self.doc_ref_bed_light = self.db_collect.document("device4")

        # within devices collection, device6 document is the entrance light
        self.doc_ref_entrance_light = self.db_collect.document("device6")

        # within devices collection, device2 document is the bedroom fan
        self.doc_ref_bed_fan = self.db_collect.document("device5")


        # collected is called "settings" for home/away mode
        self.db_settings = self.db.collection("settings")

        # within settings collection, awayMode document has the variable for isAway
        self.doc_ref_away = self.db_settings.document("awayMode")
    
    # Listener for Fan changes
    def living_fan_listener(self, doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            print(f"Fan Listener Snapshot: {doc.to_dict()}")  # Debugging: print the snapshot data
            fan_status = doc.get('Fan')
            if fan_status is not None:
                if fan_status:  # If fan is not 0
                    print(f"Fan on at speed mode: {fan_status}")
                    self.living_fan.change_fan_speed(fan_status)  # Turn the fan on (active-low condition)
                else:  # If fan is OFF
                    print("Fan off")
                    self.living_fan.turn_fan_off()  # Turn the fan off (active-low condition)

    # Listener for living room light changes
    def living_light_listener(self, doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            print(f"Light Listener Snapshot: {doc.to_dict()}")  # Debugging: print the snapshot data
            light_status = doc.get('Living_Room_Light')
            if light_status is not None:
                if light_status:  # If light is ON
                    print(f"Light on at: {light_status}")
                    self.living_light.change_brightness(light_status)  # Turn the light on (active-low condition)
                else:  # If light is OFF
                    print("Light off")
                    self.living_light.turn_light_off()  # Turn the light off (active-low condition)

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
    
    # Listener for bedroom light changes
    def entrance_light_listener(self, doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            print(f"Entrance Light Listener Snapshot: {doc.to_dict()}")  # Debugging: print the snapshot data
            light_status = doc.get('Entrance_Light')
            if light_status is not None:
                if light_status:  # If light is ON
                    print(f"Entrance Light on at: {light_status}")
                    self.entrance_light.change_brightness(light_status)  # Turn the light on (active-low condition)
                else:  # If light is OFF
                    print("Entrance Light off")
                    self.entrance_light.turn_light_off()  # Turn the light off (active-low condition)

    # Listener for awayMode changes
    def away_mode_listener(self, doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            print(f"AwayMode Listener Snapshot: {doc.to_dict()}")  # Debugging: print the snapshot data
            away_status = doc.get('isAway')
            if away_status is not None:
                if away_status:  # If away mode is ON
                    print(f"Away mode active: {away_status}")
                else:  # If away mode is OFF (i.e. home)
                    print(f"Away mode not active: {away_status}")
                
                # call motion detection to activate if away mode is set
                self.motion_detection(away_status)

    # motion detection using motion sensor for away mode (intruder alert)
    def motion_detection(self, away_mode):
        # use the motion sensor to check motion detection
        result = self.motion_sensor.check_motion()

        # if away mode active ("alarm")
        if(away_mode):
            # and there is motion detected, send an alert
            if(result == "Movement detected"):
                self.send_alert("Intruder!", "Intrusion")

    # Listener for desired temp changes ("currentTemp", "desiredTemp")
    def desired_temp_listener(self, doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            print(f"Desired Temp Listener Snapshot: {doc.to_dict()}")  # Debugging: print the snapshot data
            temp_status = doc.get('desiredTemp')
            if temp_status is not None:
                if temp_status:
                    print(f"Desired Temp: {temp_status}")
                    self.bed_light.change_brightness(temp_status)  # Turn the light on (active-low condition)

    def connect_listeners(self):
        # Attach listeners to Firestore documents
        self.doc_ref_living_fan.on_snapshot(self.living_fan_listener)
        self.doc_ref_bed_fan.on_snapshot(self.bed_fan_listener)
        
        self.doc_ref_living_light.on_snapshot(self.living_light_listener)
        self.doc_ref_bed_light.on_snapshot(self.bed_light_listener)
        self.doc_ref_entrance_light.on_snapshot(self.entrance_light_listener)
        
        self.doc_ref_away.on_snapshot(self.away_mode_listener)

        self.doc_ref_desired_temp.on_snapshot(self.desired_temp_listener)

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