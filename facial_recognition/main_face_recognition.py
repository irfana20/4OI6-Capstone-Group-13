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

from facial_recognition.train_faces import train_faces

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from initialize_app import InitApp
from src.step_motor import Step_Motor


class FacialRec:
    def __init__(self):
        # Constants
        self.FACE_DATA_FILE = "encodings.pickle"
        self.PROCESSED_PHOTOS_FILE = 'processed_photos.txt'
        self.ALERT_COOLDOWN = 15 # Time before sending alert for same person (s)
        self.CV_SCALER = 5 # Scale down frame
        self.OPEN_COOLDOWN = 10 # Open door cooldown
        self.OPEN_TIME = 10 # Time for door to open

        # Initializations 
        init_app = InitApp()
        self.db, self.bucket = init_app.main()

        self.motor = Step_Motor()

        self.last_open_time = 0 # Tracks when door was last open
        self.is_door_open = False

        self.last_alert_time = {} # Dictionary tracking alert time per person

        self.processed_photos = set() # Set of already-trained photos
        self.face_lock = threading.Lock()

        # Camera initialization
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_video_configuration(main={"size": (640, 480), "format": "RGB888"}))
        self.picam2.start()


    def send_alert(self, name):
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
        self.db.collection("alerts").document(doc_name).set(alert_data)
        print(f"[ALERT] {msg}")


    def load_face_data(self):
        '''
        load face encodings from pickle file
        '''
        if os.path.exists(self.FACE_DATA_FILE):
            with open(self.FACE_DATA_FILE, "rb") as file:
                face_data = pickle.load(file)
            return face_data["encodings"], face_data["names"]
        return [], []


    def recognize_faces(self):
        '''
        Detects and identifies faces
        Opens the door for known people and sends alerts
        '''
        self.is_door_open, self.last_open_time, self.last_alert_time
        last_reload_time = time.time()
        reload_interval = 10 # Seconds
        known_face_encodings, known_face_names = self.load_face_data()

        while True:
            current_time = time.time()
            
            if current_time - last_reload_time > reload_interval:
                print("[INFO] Reloading face encodings from file...")
                with self.face_lock:
                    known_face_encodings, known_face_names = self.load_face_data()
                last_reload_time = current_time
                
            frame = self.picam2.capture_array()
            # Resize and convert to RGB for recognition
            resized_frame = cv2.resize(frame, (0, 0), fx=(1/self.CV_SCALER), fy=(1/self.CV_SCALER))
            rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

            with self.face_lock: #lock to prevent interference with training
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
                last_sent = self.last_alert_time.get(name, datetime.min) # Get the last time alert was sent for the person
                
                if (now - last_sent).total_seconds() > self.ALERT_COOLDOWN:
                    self.send_alert(name)
                    self.last_alert_time[name] = now
                else:
                    print(f"[INFO] {name} alert cooldown")
                    
                # Door logic for residents
                if name != "Unknown" and not self.is_door_open and (current_time - self.last_open_time > self.OPEN_COOLDOWN):
                    print(f"[INFO] Opening door for {name}...")
                    self.motor.open_door()
                    self.last_open_time = current_time
                    self.is_door_open = True
            
            # Close the door after certain time
            if self.is_door_open and (current_time - self.last_open_time > self.OPEN_TIME):
                print(f"[INFO] Closing door...")
                self.motor.close_door()
                self.is_door_open = False


    def load_processed_photos(self):
        '''
        Load previously processed photos (through a combined URL text file)
        read from the text file to get photo URLS already trained on
        '''
        if not os.path.exists(self.PROCESSED_PHOTOS_FILE):
            return set() # If the file doesnt exist, return empty set
        with open(self.PROCESSED_PHOTOS_FILE, 'r') as file:
            return set(line.strip() for line in file)

    def save_processed_photo(self, photo_path):
        '''
        Save a newly processed photo URL
        adds a photo path to the log file to avoid retraining
        '''
        with open(self.PROCESSED_PHOTOS_FILE, 'a') as file:
            file.write(f"{photo_path}\n")

    def download_and_save_image(self, resident_name, image_url):
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

    def on_snapshot(self, col_snapshot, changes, read_time):
        '''
        Triggered when there are changes to the resident collection
        '''
        self.processed_photos
        
        for change in changes:
            if change.type.name in ('ADDED', 'MODIFIED'):
                doc = change.document.to_dict()
                resident_name = doc.get('resident')
                photo_paths = doc.get('photoPath', [])
                
                if not resident_name or not photo_paths:
                    continue

                new_photos = [] # Track only new photos for training
                for photo_url in photo_paths:
                    if photo_url not in self.processed_photos:
                        try:
                            # Downloaded, marked as processed, and add for training
                            local_file = self.download_and_save_image(resident_name, photo_url)
                            self.processed_photos.add(photo_url)
                            self.save_processed_photo(photo_url)
                            new_photos.append(local_file)
                        except Exception as e:
                            print(f"[ERROR] Failed to process {photo_url}: {e}")

                if new_photos:
                    # Train the new photos
                    train_faces(new_photos, resident_name, face_lock=self.face_lock)

    def start_camera(self):
        # Flask camera stream
        self.app = Flask(__name__)
        @self.app.route('/video_feed')
        def video_feed():
            def generate_frames():
                while True:
                    frame = self.picam2.capture_array()
                    frame = cv2.flip(frame, 1) # Flip the frame horizontally
                    ret, buffer = cv2.imencode('.jpg', frame)
                    yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def main(self):
        # Load URLs of previously processed photos to avoid reprocessing
        self.processed_photos = self.load_processed_photos()
        
        # Start facial_recognition in a seperate thread
        threading.Thread(target=self.recognize_faces, daemon=True).start()
        
        # Firestore listener
        col_query = self.db.collection(u'resident_photos')
        col_query.on_snapshot(self.on_snapshot)
        print("[INFO] Firestore listener started...")

        #User can view live camera stream at given URL
        self.start_camera()
        print("[INFO] Starting video stream server at http://<your-pi-ip>:5000/video_feed")
        self.app.run(host='0.0.0.0', port=5000)