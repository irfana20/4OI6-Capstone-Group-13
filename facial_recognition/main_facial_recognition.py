import threading
import time
import sys
import os

#from camera_stream import app as flask_app
from recognize_faces import app as flask_app, run_face_recognition
from listener_firestore import on_snapshot, start_firestore_listener
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from initialize_app import InitApp

firebase = InitApp()
db, bucket = firebase.main()
#
# def start_camera_stream():
#     print("[MAIN] Starting Flask camera stream...")
#     flask_app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
       
def start_face_recognition():
    print("[MAIN] Starting face recognition and Flask camera stream...")
    
    face_thread = threading.Thread(target = run_face_recognition)
    face_thread.start()
    flask_app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    
def main():
    firestore_thread = threading.Thread(target = start_firestore_listener)
    camera_stream_thread = threading.Thread(target = start_face_recognition)
    
    firestore_thread.start()
    camera_stream_thread.start()
    
    
if __name__ == "__main__":
    main()

