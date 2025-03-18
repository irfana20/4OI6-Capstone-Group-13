from fan import Fan
from light_bulb import LightBulb
import time
FAN_PIN = 5

fan1 = Fan()
light1 = LightBulb()

fan1.turn_fan_on()
light1.turn_light_on()
time.sleep(1.25)


fan1.turn_fan_off()
time.sleep(1.25)
light1.turn_light_off()