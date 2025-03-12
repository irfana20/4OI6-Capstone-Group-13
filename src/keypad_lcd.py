from lcd_i2c import LCD

import RPi.GPIO as GPIO
import time

# Define the GPIO pins for rows and columns
ROW_PINS = [26, 25, 24, 23]  # BCM numbering (Rows)
COL_PINS = [22, 27, 16, 12]  # BCM numbering (Columns)

# Define the keypad layout
KEYPAD = [
    ["1", "2", "3", "A"],
    ["4", "5", "6", "B"],
    ["7", "8", "9", "C"],
    ["*", "0", "#", "D"]
]

lcd1 = LCD()

# Default secret PIN
secretPin = "4578"
attempts_left = 3  # Max attempts before lockout
lockout_time = 60  # 1-minute lockout
locked_until = 0   # Timestamp when user can try again

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)

# Set up the row pins as outputs and the column pins as inputs
for row_pin in ROW_PINS:
    GPIO.setup(row_pin, GPIO.OUT)
    GPIO.output(row_pin, GPIO.HIGH)

for col_pin in COL_PINS:
    GPIO.setup(col_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def read_keypad():
    """ Reads the keypad and returns the pressed key. Waits until a key is pressed. """
    while True:
        for row in range(4):
            for r in ROW_PINS:
                GPIO.output(r, GPIO.HIGH)

            GPIO.output(ROW_PINS[row], GPIO.LOW)  # Activate the current row

            for col in range(4):
                if GPIO.input(COL_PINS[col]) == GPIO.LOW:  # Key is pressed
                    key = KEYPAD[row][col]

                    # Wait for the key to be released to prevent multiple detections
                    while GPIO.input(COL_PINS[col]) == GPIO.LOW:
                        time.sleep(0.05)  # Debounce

                    GPIO.output(ROW_PINS[row], GPIO.HIGH)  # Reset row after key press
                    return key  # Return the detected key

            GPIO.output(ROW_PINS[row], GPIO.HIGH)  # Reset row before moving to next row

def enter_pin():
    """ Allows user to enter the PIN and checks if it matches secretPin. Blocks user after 3 failed attempts. """
    global attempts_left, locked_until

    if time.time() < locked_until:
        wait_time = int(locked_until - time.time())
        lcd1.lcd_display("Locked Out", 1)
        lcd1.lcd_display(f"Wait {wait_time}s", 2)
        time.sleep(1)  # Wait a bit before rechecking
        return False

    inputPin = ""
    lcd1.lcd_display("Enter PIN:", 1)

    while True:
        key = read_keypad()
        if key == "C":  # Clear input
            inputPin = ""
            lcd1.lcd_display("PIN Cleared", 2)
            time.sleep(1)
            lcd1.lcd_display("Enter PIN:", 1)
            continue
        elif key == "#":  # Submit PIN
            break
        elif key.isdigit():  # Only accept numbers
            lcd1.lcd_display("*" * len(inputPin) + "*", 2, clear=True)
            inputPin += key

    # Check PIN
    if inputPin == secretPin:
        lcd1.lcd_display("Access Granted", 1)
        time.sleep(2)
        return True
    else:
        attempts_left -= 1
        lcd1.lcd_display("Incorrect PIN", 1)
        lcd1.lcd_display(f"Attempts: {attempts_left}", 2)
        time.sleep(2)

        if attempts_left == 0:
            locked_until = time.time() + lockout_time
            lcd1.lcd_display("LOCKED OUT!", 1)
            lcd1.lcd_display("Try in 1 min", 2)
            return False

    return False


def set_new_pin():
    global secretPin

    lcd1.lcd_display("Change PIN", 1)
    if enter_pin():
        newPin = ""
        lcd1.lcd_display("New PIN:", 1)

        while True:
            key = read_keypad()
            if key == "C":
                newPin = ""
                lcd1.lcd_display("PIN Cleared", 2)
                time.sleep(1)
                lcd1.lcd_display("New PIN:", 1)
                continue
            elif key == "#":
                if len(newPin) >= 4:
                    secretPin = newPin
                    lcd1.lcd_display("PIN Changed", 1)
                    time.sleep(2)
                    return
                else:
                    lcd1.lcd_display("Min 4 Digits", 2)
                    time.sleep(2)
                    lcd1.lcd_display("New PIN:", 1)
                    continue
            elif key.isdigit():
                lcd1.lcd_display("*" * len(newPin) + "*", 2, clear=True)
                newPin += key

try:
    while True:
        if time.time() < locked_until:
            wait_time = int(locked_until - time.time())
            lcd1.lcd_display("Locked Out", 1)
            lcd1.lcd_display(f"Wait {wait_time}s", 2)
            time.sleep(5)
            continue

        lcd1.lcd_display("1: Enter PIN", 1)
        lcd1.lcd_display("A: Change PIN", 2)
        choice = read_keypad()

        if choice == "1":
            enter_pin()
        elif choice == "A":
            set_new_pin()
        elif choice == "*":
            lcd1.lcd_display("Exiting...", 1)
            break
        else:
            lcd1.lcd_display("Invalid Choice", 1)
            time.sleep(2)
except KeyboardInterrupt:
    lcd1.lcd_display("Goodbye!", 1)
    time.sleep(2)
    GPIO.cleanup()