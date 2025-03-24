#!/usr/bin/python3
import RPi.GPIO as GPIO
import time

class Step_Motor:
    def __init__(self, direction=False):
        self.in1 = 8
        self.in2 = 9
        self.in3 = 10
        self.in4 = 11

        # careful lowering this, at some point you run into the mechanical limitation of how quick your motor can move
        self.step_sleep = 0.002

        # 5.625*(1/64) per step, 4096 steps is 360°
        # 1024 steps for 90°
        self.step_count = 1024

        # True for clockwise, False for counter-clockwise
        self.direction = direction

        # defining stepper motor sequence
        self.step_sequence = [[1,0,0,1],
                        [1,0,0,0],
                        [1,1,0,0],
                        [0,1,0,0],
                        [0,1,1,0],
                        [0,0,1,0],
                        [0,0,1,1],
                        [0,0,0,1]]

        # setting up GPIO mode to BCM
        GPIO.setmode(GPIO.BCM)

        # setting up GPIO as output
        GPIO.setup(self.in1, GPIO.OUT)
        GPIO.setup(self.in2, GPIO.OUT)
        GPIO.setup(self.in3, GPIO.OUT)
        GPIO.setup(self.in4, GPIO.OUT)

        # initializing pins to low
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW)
        GPIO.output(self.in3, GPIO.LOW)
        GPIO.output(self.in4, GPIO.LOW)

        self.motor_pins = [self.in1, self.in2, self.in3, self.in4]
        self.motor_step_counter = 0

    def change_direction(self, direction):
        self.direction = direction

    def rotate_step_motor(self):
            i = 0
            for i in range(self.step_count):
                for pin in range(0, len(self.motor_pins)):
                    GPIO.output(self.motor_pins[pin], self.step_sequence[self.motor_step_counter][pin] )
                if self.direction==True:
                
                    self.motor_step_counter = (self.motor_step_counter - 1) % 8
                
                elif self.direction==False:
                    self.motor_step_counter = (self.motor_step_counter + 1) % 8
                
                # defensive programming
                else:
                    print( "Direction should *always* be either True or False" )
                    self.cleanup()

                time.sleep(self.step_sleep)

    def open_door(self):
        self.direction = False
        self.rotate_step_motor()

    def close_door(self):
        self.direction = True
        self.rotate_step_motor()

    def cleanup(self):
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW)
        GPIO.output(self.in3, GPIO.LOW)
        GPIO.output(self.in4, GPIO.LOW)
        GPIO.cleanup()