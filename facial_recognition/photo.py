"""
This code captures and saves photos using a Raspberry Pi camera. It asks for a resident's name, creates a folder for them, 
and then continuously displays a live camera feed. The resident can press SPACEBAR to take a photo, which gets saved with a 
timestamp in the resident's folder, or press ESC to exit. At the end, it prints how many photos were saved and properly 
shuts down the camera and preview window.
"""

import os
from picamera2 import Picamera2, Preview
from datetime import datetime
import cv2

def create_folder(resident_name):

    # Create a folder for the person if it doesn't already exist
    folder_path = os.path.join(os.getcwd(), "dataset", resident_name)
    os.makedirs(folder_path, exist_ok=True)  # Ensure the folder exists
    return folder_path

def main():

    photo_num = 0 # Keep track of how many photos are taken 

    # Initialize Pi camera
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
    picam2.start()
    
    # Ask for the resident's name and create a folder for their photos
    resident_name = input("Enter the name of the resident: ").strip().title()
    folder_path = create_folder(resident_name)
    print(f"Photos will be saved in: {folder_path}")

    print("Press SPACEBAR to capture a photo, ESC to quit.")

    try:
        while True:
            # Capture the current frame
            frame = picam2.capture_array()
            
            # Display the frame using OpenCV
            cv2.imshow("Photo Capture", frame)
            
            # Wait for key press
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27:  # ESC key to quit
                print("Exiting...")
                break

            elif key == 32:  # SPACEBAR to capture a photo
                date_time = datetime.now().strftime("%Y%m%d_%H%M%S")  # YearMonthDay_HourMinuteSecond
                photo_name = f"{resident_name}_{date_time}.jpg"
                photo_path = os.path.join(folder_path, photo_name)
                cv2.imwrite(photo_path, frame)
                photo_num += 1  # Increment after saving
                print(f"{photo_num} photo(s) saved in {photo_path}")

    finally:
        # Clean up resources properly
        cv2.destroyAllWindows()
        picam2.stop()
        print(f"Photo capture completed. {photo_num} photos saved for {resident_name}.")

    # Clean up resources
    cv2.destroyAllWindows()
    picam2.stop()
    print(f"Photo capture completed. {photo_num} photos saved for {resident_name}.")

if __name__ == "__main__":
    main()

