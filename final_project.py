import threading
from facial_recognition.main_face_recognition import FacialRec
from src.control_logic import Control

def start_facial():
    run_facial = FacialRec()
    run_facial.main()

def start_control():
    run_control = Control()
    run_control.main()

if __name__ == '__main__':
    
    thread_list = []

    # create facial rec thread
    facial_thread = threading.Thread(target = start_facial, args=())
    # append to thread list for tracking
    thread_list.append(facial_thread)
    # daemon process runs in the background
    facial_thread.daemon = True
    # start the keypad thread
    facial_thread.start()

    # create control thread
    control_thread = threading.Thread(target = start_control, args=())
    # append to thread list for tracking
    thread_list.append(control_thread)
    # daemon process runs in the background
    control_thread.daemon = True
    # start the keypad thread
    control_thread.start()
    
    # Wait for threads to complete
    for thread in thread_list:
        thread.join()