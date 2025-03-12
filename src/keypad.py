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
        print(f"\n⏳ Too many failed attempts. Try again in {wait_time} seconds.")
        return False

    while attempts_left > 0:
        inputPin = ""
        print("\nEnter PIN (Press # to submit, C to clear):")

        while True:
            key = read_keypad()
            if key == "C":  # Clear the input
                print("\n🔄 PIN entry cleared. Start again:")
                inputPin = ""
                continue
            elif key == "#":  # Submit PIN
                break
            elif key.isdigit():  # Only accept numbers
                print("*", end="", flush=True)  # Masked input
                inputPin += key

        # Check PIN
        if inputPin == secretPin:
            print("\n✅ PIN is correct! Access granted.")
            attempts_left = 3  # Reset attempts after successful login
            return True
        else:
            attempts_left -= 1
            print(f"\n❌ Incorrect PIN. Attempts left: {attempts_left}")

            if attempts_left == 0:
                locked_until = time.time() + lockout_time
                print("\n🚫 Too many incorrect attempts! You are locked out for 1 minute.")
                return False

    return False

def set_new_pin():
    """ Allows the user to set a new PIN after entering the correct current PIN. """
    global secretPin

    print("\n🔒 Changing PIN...")

    # Verify the current PIN first
    if enter_pin():
        newPin = ""
        print("\nEnter new PIN (Press # to confirm, C to clear):")

        while True:
            key = read_keypad()
            if key == "C":  # Clear the input
                print("\n🔄 PIN entry cleared. Start again:")
                newPin = ""
                continue
            elif key == "#":  # Confirm PIN
                if len(newPin) >= 4:
                    secretPin = newPin
                    print("\n✅ PIN changed successfully!")
                    return
                else:
                    print("\n⚠️ PIN must be at least 4 digits.")
                    continue
            elif key.isdigit():  # Only accept numbers
                print("*", end="", flush=True)  # Masked input
                newPin += key

try:
    while True:
        # Check if the user is locked out before showing the menu
        if time.time() < locked_until:
            wait_time = int(locked_until - time.time())
            print(f"\n⏳ Locked out. Please wait {wait_time} seconds.")
            time.sleep(5)  # Avoid spamming messages
            continue

        print("\nOptions:\n1️ Enter PIN\nA Change PIN\nPress * to exit.")

        choice = read_keypad()

        if choice == "1":
            enter_pin()
        elif choice == "A":
            set_new_pin()
        elif choice == "*":
            print("\nExiting...")
            break
        else:
            print("Invalid selection. Try again.")

except KeyboardInterrupt:
    print("\nExiting...")
    GPIO.cleanup()