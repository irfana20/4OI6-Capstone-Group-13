import firebase_admin
from firebase_admin import credentials, firestore, storage

class InitApp:

    def __init__(self):
        # Initialize Firebase Admin SDK once
        if not firebase_admin._apps:
            cred = credentials.Certificate("../capstone-app-59cf7.json")
            firebase_admin.initialize_app(cred, {
                'storageBucket': "capstone-app-59cf7.appspot.com",
                'databaseURL': 'https://capstone-app-59cf7.firebaseio.com/'
            })

        db = firestore.client()
        bucket = storage.bucket()

        return db, bucket