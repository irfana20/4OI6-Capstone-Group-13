import os
import cv2
import pickle
import numpy as np
import face_recognition

FACE_DATA_FILE = "encodings.pickle"

def train_faces(new_photo_paths, resident_name, face_lock=None):
    print("[INFO] Starting incremental training...")

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

    for i, file_path in enumerate(new_photo_paths):
        print(f"[INFO] Processing new image {i + 1} of {len(new_photo_paths)}: {file_path}")

        image = cv2.imread(file_path)
        if image is None:
            print(f"[WARNING] Could not read image: {file_path}. Skipping.")
            continue

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        with face_lock or dummy_context():
            face_locations = face_recognition.face_locations(rgb_image, model="hog")
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

        if not face_encodings:
            print(f"[WARNING] No faces found in {file_path}. Skipping.")
            continue

        saved_encodings.extend(face_encodings)
        saved_names.extend([resident_name] * len(face_encodings))

    face_data = {
        "encodings": saved_encodings,
        "names": saved_names
    }

    with open(FACE_DATA_FILE, "wb") as file:
        pickle.dump(face_data, file)

    print("[INFO] Incremental training complete.")

# If no face_lock is passed
from contextlib import contextmanager
@contextmanager
def dummy_context():
    yield

if __name__ == "__main__":
    train_faces([], "")