import firebase_admin
import os
from firebase_admin import credentials, firestore, storage

class InitApp:

    def __init__(self):
        self.db = None
        self.bucket = None
        
    
    def main(self):
        # Initialize Firebase Admin SDK once
        if not firebase_admin._apps:
            cred_path = os.path.join(os.path.dirname(__file__),"capstone-app-59cf7-firebase-adminsdk-62bt7-539d8787a6.json")
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                'storageBucket': "capstone-app-59cf7.appspot.com",
                'databaseURL': 'https://capstone-app-59cf7.firebaseio.com/'
            })

        self.db = firestore.client()
        self.bucket = storage.bucket()

        return self.db, self.bucket
