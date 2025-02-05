import adafruit_dht
import board
import RPi.GPIO as GPIO

class TempSensor:
    def __init__(self, current_temp = 0):
        TEMP_PIN = 13 # pin that temp sensor is connected to
        GPIO.setmode(GPIO.BCM) # set board pin reading to be the GPIO # ex. GPIO5 would be 5
        GPIO.setup(TEMP_PIN, GPIO.IN) # set GPIO13 to be an input
        dht_device = adafruit_dht.DHT11(board.D13)
        self.temp = current_temp

    def get_temp(self):
        try:
            print("Reading data from DHT11 sensor...")
            # Read the temperature and humidity
            temperature = dht_device.temperature

            if temperature is not None:
                print(f"Temperature: {temperature:.1f}°C")
            else:
                print("Failed to get reading. Try again!")
    
        except RuntimeError as error:
                print(error.args[0])