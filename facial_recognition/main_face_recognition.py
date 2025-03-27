import os
import sys
import cv2
import pickle
import time
import threading
import urllib.request
import face_recognition
import numpy as np
from flask import Flask, Response
from datetime import datetime
from picamera2 import Picamera2

from train_faces import train_faces

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from initialize_app import InitApp
from src.step_motor import Step_Motor

# Constants
FACE_DATA_FILE = "encodings.pickle"
PROCESSED_PHOTOS_FILE = 'processed_photos.txt'
ALERT_COOLDOWN = 15 # Time before sending alert for same person (s)
CV_SCALER = 5 # Scale down frame
OPEN_COOLDOWN = 10 # Open door cooldown
OPEN_TIME = 10 # Time for door to open

# Initializations 
init_app = InitApp()
db, bucket = init_app.main()

motor = Step_Motor()

last_open_time = 0 # Tracks when door was last open
is_door_open = False

last_alert_time = {} # Dictionary tracking alert time per person

processed_photos = set() # Set of already-trained photos
face_lock = threading.Lock()

# Camera initialization
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480), "format": "RGB888"}))
picam2.start()


def send_alert(name):
    doc_name = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    msg = f"{name} is at the door" if name != "Unknown" else "Unknown person is at the door"
    alert_data = {
        "message": msg,
        "notification": {
            "title": "Motion Detected",
            "body": "Known vs unknown!"
        },
        "timestamp": datetime.now().isoformat()
    }
    db.collection("alerts").document(doc_name).set(alert_data)
    print(f"[ALERT] {msg}")


def load_face_data():
    '''
    load face encodings from pickle file
    '''
    if os.path.exists(FACE_DATA_FILE):
        with open(FACE_DATA_FILE, "rb") as file:
            face_data = pickle.load(file)
        return face_data["encodings"], face_data["names"]
    return [], []


def recognize_faces():
    '''
    Detects and identifies faces
    Opens the door for known people and sends alerts
    '''
    global is_door_open, last_open_time, last_alert_time
    last_reload_time = time.time()
    reload_interval = 10 # Seconds
    known_face_encodings, known_face_names = load_face_data()

    while True:
        current_time = time.time()
        
        if current_time - last_reload_time > reload_interval:
            print("[INFO] Reloading face encodings from file...")
            with face_lock:
                known_face_encodings, known_face_names = load_face_data()
            last_reload_time = current_time
            
        frame = picam2.capture_array()
        # Resize and convert to RGB for recognition
        resized_frame = cv2.resize(frame, (0, 0), fx=(1/CV_SCALER), fy=(1/CV_SCALER))
        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

        with face_lock: #lock to prevent interference with training
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations, model='large')

        #current_time = time.time() #track time for cooldown

        # Compare faces for recognition
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
            name = "Unknown"
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances) # Get the cloest match
                if matches[best_match_index]:
                    name = known_face_names[best_match_index] # Retrieve the name

            now = datetime.now()
            last_sent = last_alert_time.get(name, datetime.min) # Get the last time alert was sent for the person
            
            if (now - last_sent).total_seconds() > ALERT_COOLDOWN:
                send_alert(name)
                last_alert_time[name] = now
            else:
                print(f"[INFO] {name} alert cooldown")
                
            # Door logic for residents
            if name != "Unknown" and not is_door_open and (current_time - last_open_time > OPEN_COOLDOWN):
                print(f"[INFO] Opening door for {name}...")
                motor.open_door()
                last_open_time = current_time
                is_door_open = True
        
        # Close the door after certain time
        if is_door_open and (current_time - last_open_time > OPEN_TIME):
            print(f"[INFO] Closing door...")
            motor.close_door()
            is_door_open = False


def load_processed_photos():
    '''
    Load previously processed photos (through a combined URL text file)
    read from the text file to get photo URLS already trained on
    '''
    if not os.path.exists(PROCESSED_PHOTOS_FILE):
        return set() # If the file doesnt exist, return empty set
    with open(PROCESSED_PHOTOS_FILE, 'r') as file:
        return set(line.strip() for line in file)

def save_processed_photo(photo_path):
    '''
    Save a newly processed photo URL
    adds a photo path to the log file to avoid retraining
    '''
    with open(PROCESSED_PHOTOS_FILE, 'a') as file:
        file.write(f"{photo_path}\n")

def download_and_save_image(resident_name, image_url):
    '''
    Download an image from firestore storage
    '''
    dataset_folder = os.path.join(os.getcwd(), 'dataset', resident_name)
    os.makedirs(dataset_folder, exist_ok=True) # Create folder if it doesn't exist
    
    image_name = os.path.basename(image_url.split('?')[0])
    local_path = os.path.join(dataset_folder, image_name)
    
    print(f"[INFO] Downloading {image_url} to {local_path}")
    urllib.request.urlretrieve(image_url, local_path)
    return local_path # Return path to use for training

def on_snapshot(col_snapshot, changes, read_time):
    '''
    Triggered when there are changes to the resident collection
    '''
    global processed_photos
    
    for change in changes:
        if change.type.name in ('ADDED', 'MODIFIED'):
            doc = change.document.to_dict()
            resident_name = doc.get('resident')
            photo_paths = doc.get('photoPath', [])
            
            if not resident_name or not photo_paths:
                continue

            new_photos = [] # Track only new photos for training
            for photo_url in photo_paths:
                if photo_url not in processed_photos:
                    try:
                        # Downloaded, marked as processed, and add for training
                        local_file = download_and_save_image(resident_name, photo_url)
                        processed_photos.add(photo_url)
                        save_processed_photo(photo_url)
                        new_photos.append(local_file)
                    except Exception as e:
                        print(f"[ERROR] Failed to process {photo_url}: {e}")

            if new_photos:
                # Train the new photos
                train_faces(new_photos, resident_name, face_lock=face_lock)

# Flask camera stream
app = Flask(__name__)
@app.route('/video_feed')
def video_feed():
    def generate_frames():
        while True:
            frame = picam2.capture_array()
            frame = cv2.flip(frame, 1) # Flip the frame horizontally
            ret, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Load URLs of previously processed photos to avoid reprocessing
    processed_photos = load_processed_photos()
    
    # Start facial_recognition in a seperate thread
    threading.Thread(target=recognize_faces, daemon=True).start()
    
    # Firestore listener
    col_query = db.collection(u'resident_photos')
    col_query.on_snapshot(on_snapshot)
    print("[INFO] Firestore listener started...")

    #User can view live camera stream at given URL
    print("[INFO] Starting video stream server at http://<your-pi-ip>:5000/video_feed")
    app.run(host='0.0.0.0', port=5000)
