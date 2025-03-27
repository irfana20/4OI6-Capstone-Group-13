import bme280
import smbus2
from time import sleep

class TempSensor:
    def __init__(self, current_temp = 0):
        port = 1
        self.address = 0x76 # Adafruit BME280 address. Other BME280s may be different
        self.bus = smbus2.SMBus(port)
        bme280.load_calibration_params(self.bus, self.address)
        self.ambient_temperature = current_temp

    def read_temp(self):
        bme280_data = bme280.sample(self.bus, self.address)
        try:
            bme280_data = bme280.sample(self.bus, self.address)
            self.ambient_temperature = bme280_data.temperature
            print(self.ambient_temperature)

            return self.ambient_temperature
        except RuntimeError as error:
                print(error.args[0])