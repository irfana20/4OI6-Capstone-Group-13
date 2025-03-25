import os
import cv2
import pickle  # Used for saving and loading trained face encodings

import numpy as np
from imutils import paths
import face_recognition

# DEFINE CONSTANTS
FACE_DATA_FILE = "encodings.pickle"
TRAINING_IMAGES_DIR = "dataset"

# *Training the model*

"""
This function scans images from the dataset directory, encodes faces, and saves them in encodings.pickle.
"""
def train_faces(new_photo_paths, resident_name):
    print("[INFO] Starting incremental training...")
 
    # Load existing encodings if available
    if os.path.exists(FACE_DATA_FILE):
        with open(FACE_DATA_FILE, "rb") as file:
            face_data = pickle.load(file)
        saved_encodings = face_data["encodings"]
        saved_names = face_data["names"]
        print(f"[INFO] Loaded {len(saved_names)} existing encodings.")
    else:
        saved_encodings = []
        saved_names = []
        print("[INFO] No existing encodings found. Creating new dataset.")
 
    # Process only new photos
    for i, file_path in enumerate(new_photo_paths):
        print(f"[INFO] Processing new image {i + 1} of {len(new_photo_paths)}: {file_path}")
 
        # OpenCV loads images in BGR format, but face_recognition requires RGB
        image = cv2.imread(file_path)
        if image is None:
            print(f"[WARNING] Could not read image: {file_path}. Skipping.")
            continue
 
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
 
        # Find face locations and encodings
        face_locations = face_recognition.face_locations(rgb_image, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
 
        if not face_encodings:
            print(f"[WARNING] No faces found in {file_path}. Skipping.")
            continue
 
        # Save encodings and resident names
        saved_encodings.extend(face_encodings)
        saved_names.extend([resident_name] * len(face_encodings))
 
    # Save updated encodings to file
    print(f"[INFO] Saving {len(saved_names)} total encodings to file...")
    face_data = {
        "encodings": saved_encodings,
        "names": saved_names
    }
 
    with open(FACE_DATA_FILE, "wb") as file:
        pickle.dump(face_data, file)
 
    print("[INFO] Incremental training complete.")

if __name__ == "__main__":
    train_faces()


