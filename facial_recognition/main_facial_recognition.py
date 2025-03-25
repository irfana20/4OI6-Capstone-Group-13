import threading
import time
import sys
import os

from camera_stream import app as flask_app
from recognize_faces import recognize_faces
from listener_firestore import on_snapshot
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from initialize_app import InitApp

firebase = InitApp()
db, bucket = firebase.main()

def start_camera_stream():
    print("[MAIN] Starting Flask camera stream...")
    flask_app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
       
def start_face_recognition():
    print("[MAIN] Starting face recognition...")
    recognize_faces()
    
def main():
    camera_stream_thread = threading.Thread(target = start_camera_stream)
    firestore_thread = threading.Thread(target = start_firestore_listener)
    face_recognition_thread = threading.Thread(target = start_face_recognition)
    
    camera_stream_thread.start()
    firestore_thread.start()
    face_recognition_thread.start()
    
    
if __name__ == "__main__":
    main()

