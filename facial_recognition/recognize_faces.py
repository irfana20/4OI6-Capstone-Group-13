import pickle
import cv2
import time
import numpy as np
import os
import face_recognition
from datetime import datetime, timedelta
from picamera2 import Picamera2
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from step_motor import Step_Motor
from connect_to_app import ConnectToApp

# DEFINE CONSTANTS
FACE_DATA_FILE = "encodings.pickle"
ALERT_COOLDOWN = 30 # Seconds

# Initialize Firebase Admin SDK
connect_app = ConnectToApp(
    connected = True,
    fan1 = None, bed_fan = None,
    light1 = None, bed_light = None
    )

# *Facial recognition*
def recognize_faces():
    """
    This function initializes the camera and recognizes faces in real-time.
    """
    print("[INFO] Loading saved face encodings...")

    # Open and load encodings from the pickle file
    with open(FACE_DATA_FILE, "rb") as file:
        face_data = pickle.load(file)  # Directly loads the dictionary

    # Extract encodings and names
    known_face_encodings = face_data["encodings"]
    known_face_names = face_data["names"]

    # Initialize the camera module
    print("[INFO] Initializing camera...")
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
    picam2.start()
    
    # Initialize motor and set time parameters
    print("[INFO] Initializing motor...")
    motor = Step_Motor()
    last_open_time = 0
    open_cooldown = 10 # We will wait this many seconds to open the door again
    open_time = 10 # Keep the door open (seconds)
    is_door_open = False

    cv_scaler = 5  # Scale factor for faster processing
    face_locations = []  # Stores detected face positions
    face_encodings = []  # Stores numerical face data
    face_names = []  # Stores names of detected faces
    frame_count = 0  # Counts processed frames
    start_time = time.time()  # Time when processing started
    fps = 0  # Stores frames per second value
    
    # Track last alert time per person
    last_alert_time = {}

    def process_frame(frame):
        nonlocal face_locations, face_encodings, face_names
        nonlocal is_door_open, last_open_time 
        
        # Resize and convert the frame for faster processing
        resized_frame = cv2.resize(frame, (0, 0), fx=(1/cv_scaler), fy=(1/cv_scaler))
        rgb_resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

        # Detect faces and extract encodings
        face_locations = face_recognition.face_locations(rgb_resized_frame)
        face_encodings = face_recognition.face_encodings(rgb_resized_frame, face_locations, model='large')

        # Get the current time
        current_time = time.time()

        # Loop through all detected face encodings
        face_names = []
        
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance = 0.5)
            name = "Unknown"

            # Compute the distance between the detected face and all known faces
            # The lower the distance, the better the match
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            face_names.append(name)
            
            # Send alert if someone is at the door
            now = datetime.now()
            last_sent = last_alert_time.get(name, datetime.min)
            if (now - last_sent).total_seconds() > ALERT_COOLDOWN:
                alert_msg = f"{name} is at the door" if name != "Unknown" else "Unknown person is at the door"
                connect_app.send_alert(alert_msg)
                last_alert_time[name] = now
            else:
                print(f"[INFO] Skipping alert for {name}, still in cooldown.")
            
            # If it's a known face AND door has not been opened
            if name != "Unknown" and not is_door_open and (current_time - last_open_time > open_cooldown):
                # ^ If a known person is detected, the door is currently closed AND it's been more than cooldown (s) since door was last opened, then open the door
                print(f"[INFO] Recognized a resident, opening door...")
                motor.open_door()
                last_open_time = current_time # Saving the current time so we know when the door was last opened
                is_door_open = True
                
        # Close the door after 10 seconds
        if is_door_open and (current_time - last_open_time > open_time):
            print(f"[INFO] Closing door...")
            motor.close_door()
            is_door_open = False

        return frame

    def draw_results(frame):
        # Iterate through each detected face and its corresponding name
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Since face detection was performed on a resized frame, we scale up to match the original size
            top *= cv_scaler
            right *= cv_scaler
            bottom *= cv_scaler
            left *= cv_scaler

            # Draw a rectangle around the detected face
            # cv2.rectangle(image, start_point, end_point, color, thickness)
            cv2.rectangle(frame, (left, top), (right, bottom), (244, 42, 3), 3)

            # Draw a filled rectangle for the label background (so text is visible)
            # cv2.rectangle(image, start_point, end_point, color, fill_type)
            cv2.rectangle(frame, (left - 3, top - 35), (right + 3, top), (244, 42, 3), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            # Write the name label on the face bounding box
            # cv2.putText(image, text, start_position, font, font_scale, color, thickness)
            cv2.putText(frame, name, (left + 6, top - 6), font, 1.0, (255, 255, 255), 1)

        return frame

    def calculate_fps():
        nonlocal frame_count, start_time, fps
        frame_count += 1
        # Calculate the elapsed time since the last FPS calculation
        elapsed_time = time.time() - start_time
        if elapsed_time > 1:
            # Compute FPS as the number of frames processed divided by the elapsed time
            fps = frame_count / elapsed_time
            frame_count = 0
            start_time = time.time()
        return fps

    print("[INFO] Face recognition is running... Press 'q' to quit.")
    # Start an infinite loop to continuously process video frames
    while True:
        # Capture a frame from the camera
        frame = picam2.capture_array()
#         time.sleep(5)
        # Process the frame 
        processed_frame = process_frame(frame)
        # Draw bounding boxes and labels around detected faces
        display_frame = draw_results(processed_frame)
        # Calculate the FPS
        current_fps = calculate_fps()

        # Overlay the FPS counter on the frame
        # cv2.putText(image, text, position, font, font_scale, color, thickness)
        cv2.putText(display_frame, f"FPS: {current_fps:.1f}", (display_frame.shape[1] - 150, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow('Video', display_frame)

        if cv2.waitKey(1) == ord("q"):
            break

    cv2.destroyAllWindows()
    picam2.stop()
    print("[INFO] Face recognition stopped.")

if __name__ == "__main__":
    recognize_faces()

