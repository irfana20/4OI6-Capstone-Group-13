import pickle
import cv2
import time
import numpy as np
import os
import face_recognition
from picamera2 import Picamera2

# DEFINE CONSTANTS
FACE_DATA_FILE = "encodings.pickle"

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
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (1024, 768)}))
    picam2.start()

    cv_scaler = 10  # Scale factor for faster processing
    face_locations = []  # Stores detected face positions
    face_encodings = []  # Stores numerical face data
    face_names = []  # Stores names of detected faces
    frame_count = 0  # Counts processed frames
    start_time = time.time()  # Time when processing started
    fps = 0  # Stores frames per second value

    def process_frame(frame):
        nonlocal face_locations, face_encodings, face_names
        
        # Resize and convert the frame for faster processing
        resized_frame = cv2.resize(frame, (0, 0), fx=(1/cv_scaler), fy=(1/cv_scaler))
        rgb_resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

        # Detect faces and extract encodings
        face_locations = face_recognition.face_locations(rgb_resized_frame)
        face_encodings = face_recognition.face_encodings(rgb_resized_frame, face_locations, model='large')

        # Loop through all detected face encodings
        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # Compute the distance between the detected face and all known faces
            # The lower the distance, the better the match
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            face_names.append(name)

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
