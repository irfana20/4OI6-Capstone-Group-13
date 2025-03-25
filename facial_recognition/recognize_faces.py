from flask import Flask, Response
import threading
import time
import cv2
import pickle
import numpy as np
import face_recognition
from datetime import datetime
from picamera2 import Picamera2
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from initialize_app import InitApp
from src.step_motor import Step_Motor

# Initialize Flask app
app = Flask(__name__)

# Initialize Picamera2 only once
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

# Shared global frame
latest_frame = None

# Camera stream for the app
def generate_frames():
    global latest_frame
    while True:
        frame = picam2.capture_array()
        latest_frame = frame.copy()  # Save for face recognition

        # Convert to JPEG for MJPEG streaming
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


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


def run_face_recognition():
    print("[INFO] Waiting for encodings.pickle to be created...")
    while not os.path.exists("encodings.pickle"):
        time.sleep(2)
        
    print("[INFO] Loading saved face encodings...")
    # Open and load encodings from the pickle file
    with open("encodings.pickle", "rb") as file:
        face_data = pickle.load(file)

    known_face_encodings = face_data["encodings"]
    known_face_names = face_data["names"]

    # Initialize Firebase + Step Motor
    firebase = InitApp()
    db, _ = firebase.main()
    motor = Step_Motor()

    ALERT_COOLDOWN = 15
    OPEN_COOLDOWN = 10
    OPEN_TIME = 10

    last_open_time = 0
    last_alert_time = {}
    is_door_open = False

    print("[INFO] Face recognition is running in the background...")

    while True:
        if latest_frame is None:
            time.sleep(0.1)
            continue

        frame = latest_frame.copy()

        # Resize for faster processing
        resized_frame = cv2.resize(frame, (0, 0), fx=0.2, fy=0.2)
        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

        # Detect faces
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        current_time = time.time()

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
            name = "Unknown"
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

            # Handle alert cooldown
            now = datetime.now()
            last_sent = last_alert_time.get(name, datetime.min)
            if (now - last_sent).total_seconds() > ALERT_COOLDOWN:
                msg = f"{name} is at the door" if name != "Unknown" else "Unknown person is at the door"
                send_alert(db, msg)
                last_alert_time[name] = now
            else:
                print(f"[INFO] Skipping alert for {name}, still in cooldown.")

            # Handle motor door open
            if name != "Unknown" and not is_door_open and (current_time - last_open_time > OPEN_COOLDOWN):
                print(f"[INFO] Recognized {name}, opening door...")
                motor.open_door()
                last_open_time = current_time
                is_door_open = True

        # Handle door close after delay
        if is_door_open and (current_time - last_open_time > OPEN_TIME):
            print("[INFO] Closing door...")
            motor.close_door()
            is_door_open = False

        time.sleep(0.5)  # Prevents 100% CPU usage


# -------------------------------
# MAIN ENTRY POINT
# -------------------------------
if __name__ == "__main__":
    print("[MAIN] Starting combined stream and recognition...")

    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False))
    face_thread = threading.Thread(target=run_face_recognition)

    flask_thread.start()
    face_thread.start()

    flask_thread.join()
    face_thread.join()
