from RPLCD.i2c import CharLCD

class LCD:
    def __init__(self):
        # Initialize LCD (I2C address may vary, use 'i2cdetect -y 1' to find it)
        self.lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=2, cols=20, rows=4)

    def lcd_display(self, message, line=1, clear=True):
        """
        Displays a message on the LCD.
        :param message: Text to display
        :param line: LCD line (1 or 2)
        :param clear: Whether to clear the display before writing
        """
        if clear:
            self.lcd.clear()
        self.lcd.cursor_pos = (line - 1, 0)  # Set cursor to desired line
        self.lcd.write_string(message[:16])  # Display first 16 characters