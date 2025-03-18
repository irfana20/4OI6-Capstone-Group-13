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
def train_faces():
    print("[INFO] Starting training...")

    # Gets all image file paths inside the dataset folder
    print("[INFO] Processing faces for training...")
    image_files = list(paths.list_images(TRAINING_IMAGES_DIR))
    saved_names = []  # Stores extracted face encodings
    saved_encodings = []  # Stores the corresponding names of the residents

    for i, file_path in enumerate(image_files):
        print(f"[INFO] Processing image {i + 1} of {len(image_files)}")

        # Extract the folder name as the person's name
        person_name = os.path.basename(os.path.dirname(file_path))

        # OpenCV loads images in BGR format, but face_recognition requires RGB, so we convert it
        image = cv2.imread(file_path)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Finds all face locations in the image
        face_locations = face_recognition.face_locations(rgb_image, model="hog")
        
        # Extracts unique face encodings from those locations
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

        # Multiple faces????
        # Store the encodings and corresponding names
        saved_encodings.extend(face_encodings)  # Directly add all encodings
        saved_names.extend([person_name] * len(face_encodings))  # Store the name for each encoding

    print("[INFO] Saving face encodings to file...")

    # Create a dictionary to store encodings and names
    face_data = {
        "encodings": saved_encodings,
        "names": saved_names
    }

    # Open the file and save the data using pickle
    with open(FACE_DATA_FILE, "wb") as file:
        pickle.dump(face_data, file)  # Directly dump the dictionary into the file

    print("[INFO] Training complete. Encodings successfully stored.")

if __name__ == "__main__":
    train_faces()
