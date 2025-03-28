from src.fan import Fan
from src.light_bulb import LightBulb
from src.motion_sensor import Motion_Sensor
from src.temp_sensor import TempSensor
from src.connect_to_app import ConnectToApp
from src.keypad_lcd import Keypad

import RPi.GPIO as GPIO
import threading

class Control:
    def __init__(self):
        GPIO.cleanup  # Reset GPIO state
        GPIO.setwarnings(False)

    def start_keypad(self):
        door_keypad = Keypad()
        door_keypad.main()

    def start_connection(self):
        Living_Room_Fan = Fan(5)
        Bedroom_Fan = Fan(19)

        Living_Room_Light = LightBulb(6)
        Bedrooom_Light = LightBulb(7)
        Entrance_Light = LightBulb(21)

        motion_sensor = Motion_Sensor()
        temp_sensor = TempSensor()

        connection = ConnectToApp(Living_Room_Fan, Bedroom_Fan, Living_Room_Light, 
                    Bedrooom_Light, Entrance_Light, motion_sensor, temp_sensor)
        
        print("Starting start_connection() function")
        
        connection.connect_listeners()

    def main(self):
        thread_list = []

        # create keypad thread
        keypad_thread = threading.Thread(target = self.start_keypad, args=())
        # append to thread list for tracking
        thread_list.append(keypad_thread)
        # daemon process runs in the background
        keypad_thread.daemon = True
        # start the keypad thread
        keypad_thread.start()

        # create connection thread
        connect_thread = threading.Thread(target = self.start_connection, args=())
        # append to thread list for tracking
        thread_list.append(connect_thread)
        # daemon process runs in the background
        connect_thread.daemon = True
        # start the keypad thread
        connect_thread.start()

        # Wait for threads to complete
        for thread in thread_list:
            thread.join()
