from fan import Fan
from light_bulb import LightBulb
from motion_sensor import Motion_Sensor
from temp_sensor import TempSensor
from connect_to_app import ConnectToApp

def main():
    fan1 = Fan()
    light1 = LightBulb()
    motion_sensor1 = Motion_Sensor()
    temp_sensor1 = TempSensor()
    connection = ConnectToApp(False, fan1, light1)

    # initialize firebase
    connection.initialize_firebase()

    # check if connected to mobile app
    if (connection.is_connected()):
        print("Connected to mobile app")
    else:
        ("Could not connect to mobile app")

    # listen for changes in status for fan and light bulb
    connection.connect_listeners()


if __name__ == "__main__":
    main()
