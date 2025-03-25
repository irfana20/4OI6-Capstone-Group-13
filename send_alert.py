import firebase_admin
import os
from firebase_admin import credentials, firestore, storage
from datetime import datetime

cred_path = os.path.join(os.path.dirname(__file__),"capstone-app-59cf7-firebase-adminsdk-62bt7-539d8787a6.json")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {
    'storageBucket': "capstone-app-59cf7.appspot.com",
    'databaseURL': 'https://capstone-app-59cf7.firebaseio.com/'
})

db = firestore.client()

def send_alert(self, message, doc_name=None):
    # if no document name is given
    if doc_name is None:
        # Use a timestamp-based document name
        doc_name = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    alert_data = {
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    
    # save the alert to firestore database under the alerts collection
    db.collection("alerts").document(doc_name).set(alert_data)
    print(f"Alert sent successfully with document name: {doc_name}")

send_alert("Testing!", "Test_Alert")