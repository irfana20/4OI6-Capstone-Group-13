import time
from datetime import datetime
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from initialize_app import InitApp

class ConnectToApp:

    # fan and light inputs must be objects of the fan and light classes
    def __init__(self, living_fan, bed_fan, living_light, bed_light, entrance_light, motion_sensor, temp_sensor):        
        # 2 fans total
        self.living_fan = living_fan
        self.bed_fan = bed_fan
        
        # 3 lights total
        self.living_light = living_light
        self.bed_light = bed_light
        self.entrance_light = entrance_light

        # sensors
        self.motion_sensor = motion_sensor
        self.temp_sensor = temp_sensor

        # away mode logic variable
        self.away_stop = False

        # set database "db" to firestore client
        init_app = InitApp()
        print("Firebase initialized from control")
        self.db, self.bucket = init_app.main()
        print("Firebase db receieved from control")

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
    
    def update_current_temp(self, new_temp):
        # Update the 'currentTemp' field in the 'device3' document
        self.doc_ref_current_temp.set({
            'currentTemp': new_temp
        }, merge=True)

    def update_living_fan(self, new_speed):
        # Update the 'Living_Room_Fan' field in the 'device3' document
        self.doc_ref_living_fan.set({
            'Living_Room_Fan': new_speed
        }, merge=True)

    def update_bed_fan(self, new_speed):
        # Update the 'Bedroom_Fan' field in the 'device3' document
        self.doc_ref_bed_fan.set({
            'Bedroom_Fan': new_speed
        }, merge=True)

    def update_living_light(self, new_brightness):
        # Update the 'Living_Room_Light' field in the 'device3' document
        self.doc_ref_living_light.set({
            'Living_Room_Light': new_brightness
        }, merge=True)

    def update_bed_light(self, new_brightness):
        # Update the 'Bedroom_Light' field in the 'device3' document
        self.doc_ref_bed_light.set({
            'Bedroom_Light': new_brightness
        }, merge=True)

    def update_entrance_light(self, new_brightness):
        # Update the 'Entrance_Light' field in the 'device3' document
        self.doc_ref_entrance_light.set({
            'Entrance_Light': new_brightness
        }, merge=True)

    # Listener for living room fan changes
    def living_fan_listener(self, doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            print(f"Fan Listener Snapshot: {doc.to_dict()}")  # Debugging: print the snapshot data
            fan_status = doc.get('Living_Room_Fan')
            if fan_status is not None:
                if fan_status:  # If fan is not 0
                    print(f"Fan on at speed mode: {fan_status}")
                    self.living_fan.change_fan_speed(fan_status)
                else:  # If fan is OFF
                    print("Fan off")
                    self.living_fan.turn_fan_off()  # Turn the fan off (active-low condition)
    
    # Listener for bedroom fan changes
    def bed_fan_listener(self, doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            print(f"Bedroom Fan Listener Snapshot: {doc.to_dict()}")  # Debugging: print the snapshot data
            fan_status = doc.get('Bedroom_Fan')
            if fan_status is not None:
                if fan_status:  # If fan is not 0
                    print(f"Bedroom Fan an on at speed mode: {fan_status}")
                    self.bed_fan.change_fan_speed(fan_status)  # Turn the fan off (active-low condition)
                else:  # If fan is OFF
                    print("Bedroom Fan off")
                    self.bed_fan.turn_fan_off()  # Turn the fan off (active-low condition)

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
                    self.living_light.turn_light_off()

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

    # Listener for entrance light changes
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
                    # call motion detection to activate if away mode is set
                    self.away_stop = False
                    self.motion_detection()
                else:  # If away mode is OFF (i.e. home)
                    print(f"Away mode not active: {away_status}")
                    self.away_stop = True

    # motion detection using motion sensor for away mode (intruder alert)
    def motion_detection(self):
        # turn off all the lights if isAway
        if not self.away_stop:
            self.living_light.turn_light_off()
            self.update_living_light(0)

            self.bed_light.turn_light_off()
            self.update_bed_light(0)

            self.entrance_light.turn_light_off()
            self.update_entrance_light(0)
            print("turned off all lights")

        # keep detecting motion while awaymode is turned on
        while not self.away_stop:
            # use the motion sensor to check motion detection
            result = self.motion_sensor.check_motion()
            # if there is motion detected, send an alert
            if(result == "Movement detected"):
                self.send_alert("Intruder!", "Intrusion_Alert")
            
            time.sleep(5)

    # Listener for desired temp changes
    def desired_temp_listener(self, doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            print(f"Desired Temp Listener Snapshot: {doc.to_dict()}")  # Debugging: print the snapshot data
            desired_temp_status = doc.get('desiredTemp')
            current_temp_status = doc.get('currentTemp')
            print(f"Desired Temp: {desired_temp_status}, Current Temp: {current_temp_status}")
            
            # if we want cooler, turn on fan
            if (desired_temp_status < current_temp_status):
                print("Cool down")
                self.living_fan.turn_fan_on()
                self.update_living_fan(3) # highest speed mode - 3
            # else warmer, turn off fan (future, can turn on heat)
            else:
                self.living_fan.turn_fan_off()
                self.update_living_fan(0) # off - speed mode 0

    # Listener for current temp changes
    def current_temp_listener(self, doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            print(f"Current Temp Listener Snapshot: {doc.to_dict()}")  # Debugging
            prev_temp = doc.get('currentTemp') # get the currentTemp on app
            self.update_temp(prev_temp)

    def update_temp(self, prev_temp):
        current_temp_val = self.temp_sensor.read_temp() # get the current temp from sensor

        # check if the temp changed
        if prev_temp != current_temp_val:
            print(f"Current temp (on app): {prev_temp}")
            print(f"Temperature Changed to: {current_temp_val}")
            # if temp changed, update currentTemp on app to the new temp
            self.update_current_temp(current_temp_val)


    def connect_listeners(self):
        # Attach listeners to Firestore documents
        self.doc_ref_living_fan.on_snapshot(self.living_fan_listener)
        self.doc_ref_bed_fan.on_snapshot(self.bed_fan_listener)
        
        self.doc_ref_living_light.on_snapshot(self.living_light_listener)
        self.doc_ref_bed_light.on_snapshot(self.bed_light_listener)
        self.doc_ref_entrance_light.on_snapshot(self.entrance_light_listener)
        
        self.doc_ref_away.on_snapshot(self.away_mode_listener)

        # self.doc_ref_desired_temp.on_snapshot(self.desired_temp_listener)
        self.doc_ref_current_temp.on_snapshot(self.current_temp_listener)

        # Keep the thread alive and listening
        while True:
            try:
                print("Listening for changes in Firestore...")
                time.sleep(10)  # Check every 10 seconds

            except KeyboardInterrupt:
                print("Exiting program now...")

                self.living_fan.turn_fan_off()
                self.bed_fan.turn_fan_off()
                print("turned off all fans")

                self.living_light.turn_light_off()
                self.bed_light.turn_light_off()
                self.entrance_light.turn_light_off()
                print("turned off all lights")

    def send_alert(self, message, doc_name=None):
        # if no document name is given
        if doc_name is None:
            # Use a timestamp-based document name
            doc_name = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        alert_data = {
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        # save the alert to firestore database under the alerts collection
        self.db.collection("alerts").document(doc_name).set(alert_data)
        print(f"Alert sent successfully with document name: {doc_name}")