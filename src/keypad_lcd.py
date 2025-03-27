from lcd_i2c import LCD
import RPi.GPIO as GPIO
import time
from step_motor import Step_Motor

door_motor = Step_Motor()

class Keypad:
    def __init__(self):
        # Define the GPIO pins for rows and columns
        #                8,  7,  6,  5
        self.ROW_PINS = [26, 25, 24, 23]  # BCM numbering (Rows)
        #                4,  3,  2,  1
        self.COL_PINS = [22, 27, 16, 12]  # BCM numbering (Columns)

        # Define the keypad layout
        self.KEYPAD = [
            ["1", "2", "3", "A"],
            ["4", "5", "6", "B"],
            ["7", "8", "9", "C"],
            ["*", "0", "#", "D"]
        ]

        self.lcd1 = LCD()
        self.changePin = False

        # Default secret PIN
        self.secretPin = "4568"
        self.attempts_left = 3  # Max attempts before lockout
        self.lockout_time = 60  # 1-minute lockout
        self.locked_until = 0   # Timestamp when user can try again

        # Set up GPIO mode
        GPIO.setmode(GPIO.BCM)

        # Set up the row pins as outputs and the column pins as inputs
        for row_pin in self.ROW_PINS:
            GPIO.setup(row_pin, GPIO.OUT)
            GPIO.output(row_pin, GPIO.HIGH)

        for col_pin in self.COL_PINS:
            GPIO.setup(col_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def read_keypad(self):
        """ Reads the keypad and returns the pressed key. Waits until a key is pressed. """
        while True:
            for row in range(4):
                for r in self.ROW_PINS:
                    GPIO.output(r, GPIO.HIGH)

                GPIO.output(self.ROW_PINS[row], GPIO.LOW)  # Activate the current row

                for col in range(4):
                    if GPIO.input(self.COL_PINS[col]) == GPIO.LOW:  # Key is pressed
                        key = self.KEYPAD[row][col]

                        # Wait for the key to be released to prevent multiple detections
                        while GPIO.input(self.COL_PINS[col]) == GPIO.LOW:
                            time.sleep(0.05)  # Debounce

                        GPIO.output(self.ROW_PINS[row], GPIO.HIGH)  # Reset row after key press
                        return key  # Return the detected key

                GPIO.output(self.ROW_PINS[row], GPIO.HIGH)  # Reset row before moving to next row

    def enter_pin(self):
        """ Allows user to enter the PIN and checks if it matches secretPin. Blocks user after 3 failed attempts. """
        if time.time() < self.locked_until:
            wait_time = int(self.locked_until - time.time())
            self.lcd1.lcd_display("    Locked Out", 1)
            self.lcd1.lcd_display(f"    Wait {wait_time}s", 2)
            time.sleep(1)  # Wait a bit before rechecking
            return False

        inputPin = ""
        self.lcd1.lcd_display("    Enter PIN:", 1)

        while True:
            key = self.read_keypad()
            if key == "C":  # Clear input
                inputPin = ""
                self.lcd1.lcd_display("    PIN Cleared", 2)
                time.sleep(1)
                self.lcd1.lcd_display("    Enter PIN:", 1)
                continue
            elif key == "#":  # Submit PIN
                break
            elif key.isdigit():  # Only accept numbers
                self.lcd1.lcd_display("*" * len(inputPin) + "*", 2, clear=True)
                inputPin += key

        # Check PIN
        if inputPin == self.secretPin:
            # only open the door if pin is entered, not when setting a new pin
            if self.changePin == False:
                self.lcd1.lcd_display("   Welcome Home!", 2)
                door_motor.open_door()
                time.sleep(3)
                door_motor.close_door()

            time.sleep(2)
            return True
        else:
            self.attempts_left -= 1
            self.lcd1.lcd_display(" Incorrect PIN", 2)
            self.lcd1.lcd_display(f"   Attempts: {self.attempts_left}", 2)
            time.sleep(2)

            if self.attempts_left == 0:
                self.locked_until = time.time() + self.lockout_time
                self.lcd1.lcd_display(" LOCKED OUT!", 2)
                time.sleep(1)
                self.lcd1.lcd_display(" Try in 1 min", 2)
                return False

        return False


    def set_new_pin(self):
        self.changePin = True
        self.lcd1.lcd_display("   Change PIN", 1)
        if self.enter_pin():
            newPin = ""
            self.lcd1.lcd_display("  New PIN:", 1)

            while True:
                key = self.read_keypad()
                if key == "C":
                    newPin = ""
                    self.lcd1.lcd_display("PIN Cleared", 2)
                    time.sleep(1)
                    self.lcd1.lcd_display("  New PIN:", 1)
                    continue
                elif key == "#":
                    if len(newPin) >= 4:
                        self.secretPin = newPin
                        self.lcd1.lcd_display("   PIN Changed!", 2)
                        time.sleep(2)
                        self.changePin = False
                        return
                    else:
                        self.lcd1.lcd_display("Min 4 Digits", 2)
                        time.sleep(2)
                        self.lcd1.lcd_display("   New PIN:", 1)
                        continue
                elif key.isdigit():
                    self.lcd1.lcd_display("*" * len(newPin) + "*", 2, clear=True)
                    newPin += key

    def main(self):
        try:
            while True:
                if time.time() < self.locked_until:
                    wait_time = int(self.locked_until - time.time())
                    self.lcd1.lcd_display(" Locked Out!", 2)
                    self.lcd1.lcd_display(f"   Wait {wait_time}s", 2)
                    time.sleep(5)
                    continue

                self.lcd1.lcd.clear()
                self.lcd1.lcd.write_string('    A: Enter PIN\r\n    B: Change PIN\r\n    C: Clear\r\n')
                choice = self.read_keypad()

                if choice == "A":
                    self.lcd1.lcd.clear()
                    self.enter_pin()
                elif choice == "B":
                    self.lcd1.lcd.clear()
                    self.set_new_pin()
                else:
                    self.lcd1.lcd.clear()
                    self.lcd1.lcd_display("  Invalid Choice", 2)
                    time.sleep(2)
        except KeyboardInterrupt:
            self.lcd1.lcd_display("    Goodbye!", 2)
            time.sleep(2)
            self.lcd1.lcd.clear()
            GPIO.cleanup()