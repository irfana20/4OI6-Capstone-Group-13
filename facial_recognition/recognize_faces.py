import pickle
import cv2
import time
import numpy as np
import os
import sys
import face_recognition
from datetime import datetime, timedelta
from picamera2 import Picamera2

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from step_motor import Step_Motor
from connect_to_app import ConnectToApp


FACE_DATA_FILE = "encodings.pickle"
ALERT_COOLDOWN = 15 # Seconds
CV_SCALER = 5  # Scale factor for faster processing
OPEN_COOLDOWN = 10 # We will wait this many seconds to open the door again
OPEN_TIME = 10 # Keep the door open (seconds)

# Initialize Firebase Admin SDK
connect_app = ConnectToApp(
    connected = True,
    living_fan = None, bed_fan = None,
    living_light = None, bed_light = None,
    entrance_light = None, motion_sensor = None
    )

def recognize_faces():
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
    is_door_open = False
    
    # Track last alert time per person
    last_alert_time = {}
    
    face_locations = []  # Stores detected face positions
    face_encodings = []  # Stores numerical face data
    face_names = []  # Stores names of detected faces
    frame_count = 0  # Counts processed frames
    start_time = time.time()  # Time when processing started
    fps = 0  # Stores frames per second value

    def process_frame(frame):
        nonlocal face_locations, face_encodings, face_names
        nonlocal is_door_open, last_open_time 
        
        # Resize and convert the frame for faster processing
        resized_frame = cv2.resize(frame, (0, 0), fx=(1/CV_SCALER), fy=(1/CV_SCALER))
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
            if name != "Unknown" and not is_door_open and (current_time - last_open_time > OPEN_COOLDOWN):
                # ^ If a known person is detected, the door is currently closed AND it's been more than cooldown (s) since door was last opened, then open the door
                print(f"[INFO] Recognized a resident, opening door...")
                motor.open_door()
                last_open_time = current_time # Saving the current time so we know when the door was last opened
                is_door_open = True
                
        # Close the door after 10 seconds
        if is_door_open and (current_time - last_open_time > OPEN_TIME):
            print(f"[INFO] Closing door...")
            motor.close_door()
            is_door_open = False

        return frame

    def draw_results(frame):
        # Iterate through each detected face and its corresponding name
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Since face detection was performed on a resized frame, we scale up to match the original size
            top *= CV_SCALER
            right *= CV_SCALER
            bottom *= CV_SCALER
            left *= CV_SCALER

            # Draw a rectangle around the detected face
            cv2.rectangle(frame, (left, top), (right, bottom), (244, 42, 3), 3)

            # Draw a filled rectangle for the label background (so text is visible)
            cv2.rectangle(frame, (left - 3, top - 35), (right + 3, top), (244, 42, 3), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            # Write the name label on the face bounding box
            cv2.putText(frame, name, (left + 6, top - 6), font, 1.0, (255, 255, 255), 1)

        return frame

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

        cv2.imshow('Video', display_frame)

        if cv2.waitKey(1) == ord("q"):
            break

    cv2.destroyAllWindows()
    picam2.stop()
    print("[INFO] Face recognition stopped.")

if __name__ == "__main__":
    recognize_faces()


