from fan import Fan
from light_bulb import LightBulb
from motion_sensor import Motion_Sensor
from temp_sensor import TempSensor
from connect_to_app import ConnectToApp
from keypad_lcd import Keypad
import RPi.GPIO as GPIO
import threading

GPIO.cleanup  # Reset GPIO state
GPIO.setwarnings(False)

def start_keypad():
    door_keypad = Keypad()
    door_keypad.main()

def start_connection():
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

def main():
    thread_list = []

    # create keypad thread
    keypad_thread = threading.Thread(target = start_keypad, args=())
    # append to thread list for tracking
    thread_list.append(keypad_thread)
    # daemon process runs in the background
    keypad_thread.daemon = True
    # start the keypad thread
    keypad_thread.start()

    # create connection thread
    connect_thread = threading.Thread(target = start_connection, args=())
    # append to thread list for tracking
    thread_list.append(connect_thread)
    # daemon process runs in the background
    connect_thread.daemon = True
    # start the keypad thread
    connect_thread.start()

    # Wait for threads to complete
    for thread in thread_list:
        thread.join()

if __name__ == "__main__":
    main()