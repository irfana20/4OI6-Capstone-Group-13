
import pickle
import cv2
import time
import numpy as np
import os
import sys
import face_recognition
from datetime import datetime
from picamera2 import Picamera2

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from initialize_app import InitApp

from src.step_motor import Step_Motor

FACE_DATA_FILE = "encodings.pickle"
ALERT_COOLDOWN = 15
CV_SCALER = 5
OPEN_COOLDOWN = 10
OPEN_TIME = 10

# Face recognition (background thread)
def send_alert(db, message, doc_name=None):
    if doc_name is None:
        doc_name = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    alert_data = {
        "message": message,
        "notification": {
            "title": "Motion Detected",
            "body": "Known vs unknown!"
        },
        "timestamp": datetime.now().isoformat()
    }
    db.collection("alerts").document(doc_name).set(alert_data)
    print(f"Alert sent successfully with document name: {doc_name}")

def recognize_faces():
    print("[INFO] Loading saved face encodings...")
    with open(FACE_DATA_FILE, "rb") as file:
        face_data = pickle.load(file)

    known_face_encodings = face_data["encodings"]
    known_face_names = face_data["names"]

    print("[INFO] Initializing camera...")
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
    picam2.start()

   # Initialize Firebase + Step Motor
    firebase = InitApp()
    db, _ = firebase.main()
    motor = Step_Motor()
    
    last_open_time = 0
    is_door_open = False
    last_alert_time = {}

    def process_frame(frame):
        nonlocal is_door_open, last_open_time

        resized_frame = cv2.resize(frame, (0, 0), fx=(1/CV_SCALER), fy=(1/CV_SCALER))
        rgb_resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_resized_frame)
        face_encodings = face_recognition.face_encodings(rgb_resized_frame, face_locations, model='large')
        current_time = time.time()

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
            name = "Unknown"
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            now = datetime.now()
            last_sent = last_alert_time.get(name, datetime.min)
            if (now - last_sent).total_seconds() > ALERT_COOLDOWN:
                msg = f"{name} is at the door" if name != "Unknown" else "Unknown person is at the door"
                send_alert(db, msg)
                last_alert_time[name] = now
            else:
                print(f"[INFO] Skipping alert for {name}, still in cooldown.")

            if name != "Unknown" and not is_door_open and (current_time - last_open_time > OPEN_COOLDOWN):
                print(f"[INFO] Recognized {name}, opening door...")
                motor.open_door()
                last_open_time = current_time
                is_door_open = True

        if is_door_open and (current_time - last_open_time > OPEN_TIME):
            print(f"[INFO] Closing door...")
            motor.close_door()
            is_door_open = False

    print("[INFO] Face recognition is running... Press 'q' to quit.")
    while True:
        frame = picam2.capture_array()
        process_frame(frame)
        cv2.imshow('Video', frame)
        if cv2.waitKey(1) == ord("q"):
            break

    cv2.destroyAllWindows()
    picam2.stop()
    
if __name__ == "__main__":
    recognize_faces()