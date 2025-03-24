from fan import Fan
from light_bulb import LightBulb
from motion_sensor import Motion_Sensor
from temp_sensor import TempSensor
from connect_to_app import ConnectToApp
from keypad_lcd import Keypad

import time
import RPi.GPIO as GPIO
import threading

# To-do:
# motion turn on light
# motion send alert if away
# send alerts
# logic for away vs home
# desired temp logic

thread_list = []

fan1 = Fan()
Living_Room_Light = LightBulb()
motion_sensor1 = Motion_Sensor()
temp_sensor1 = TempSensor()
connection = ConnectToApp(False, fan1, Living_Room_Light)
door_keypad = Keypad()

def start_keypad():
    try:
        while True:
            if time.time() < door_keypad.locked_until:
                wait_time = int(door_keypad.locked_until - time.time())
                door_keypad.lcd1.lcd_display("Locked Out", 1)
                door_keypad.lcd1.lcd_display(f"Wait {wait_time}s", 2)
                time.sleep(5)
                continue

            #self.lcd1.lcd_display("1: Enter PIN", 1)
            #self.lcd1.lcd_display("A: Change PIN", 2)
            door_keypad.lcd1.lcd.write_string('    A: Enter PIN\r\n    B: Change PIN\r\n    C: Clear\r\n    D: Exit')
            choice = door_keypad.read_keypad()

            if choice == "A":
                door_keypad.enter_pin()
            elif choice == "B":
                door_keypad.set_new_pin()
            elif choice == "D":
                door_keypad.lcd1.lcd_display("Exiting...", 1)
                door_keypad.lcd1.lcd_display("Have a great day!", 1)
                break
            else:
                door_keypad.lcd1.lcd_display("Invalid Choice", 1)
                time.sleep(2)
    except KeyboardInterrupt:
        door_keypad.lcd1.lcd_display("Goodbye!", 1)
        time.sleep(2)
        GPIO.cleanup()

def motion_detection():
    # use the motion sensor to check motion detection
    result = motion_sensor1.check_motion()

    # if there was motion detected, send an alert
    if(result == "Movement detected"):
        connection.send_alert("Movement detected at front door!", "movement")

def main():

    # create keypad thread
    keypad_thread = threading.Thread(target = start_keypad, args=())
    # append to thread list for tracking
    thread_list.append(keypad_thread)
    # daemon process runs in the background
    keypad_thread.daemon = True
    # start the keypad thread
    keypad_thread.start()
    
    # initialize firebase
    connection.initialize_firebase()

    # check if connected to database
    if (connection.is_connected()):
        print("Connected to database")
    else:
        ("Could not connect to database")

    # listen for changes in status for fan and light bulb
    connection.connect_listeners()


if __name__ == "__main__":
    main()
