import threading
import time
import sys
import os

from camera_stream import app as flask_app
from listener_firestore import os_snapshot, db
from recognize_faces import recognize_faces

def start_camera_stream():
    print("[MAIN] Starting Flask camera stream...")
    flask_app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    
def start_firestore():
    print
    col_query = db.collection(u'resident_photos')
    col_query.on_snapshot(on_snapshot)
    while True:
        time.sleep(60)
        
def start_face_recognition():
    print("[MAIN] Starting face recognition...")
    recognize_faces()
    
def main():
    camera_stream_thread = threading.thread(target = start_camera_stream)
    firestore_thread = threading.thread(target = start_firestore)
    face_recognition_thread = threading.thread(target = start_face_recognition)
    
    camera_stream_thread.start()
    firestore_thread.start()
    face_recognition_thread.start()
    
    
if __name__ == "__main__":
    main()
