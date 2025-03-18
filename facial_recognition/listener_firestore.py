import firebase_admin
from firebase_admin import credentials, firestore, storage
import urllib.request
import os
import time
from train_faces import train_faces  # Import your training function

# Initialize Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'your-project-id.appspot.com'  # Replace with your actual bucket name
})

db = firestore.client()
bucket = storage.bucket()

def on_snapshot(col_snapshot, changes, read_time):
    for change in changes:
        if change.type.name == 'ADDED':
            doc = change.document.to_dict()
            resident_name = doc['resident_name']
            image_url = doc['image_url']

            print(f"[INFO] New photo detected for {resident_name}: {image_url}")
            download_and_save_image(resident_name, image_url)

            # Retrain the model after new images are downloaded
            print(f"[INFO] Retraining with new data...")
            train_faces()

def download_and_save_image(resident_name, image_url):
    dataset_folder = os.path.join(os.getcwd(), 'dataset')
    resident_folder = os.path.join(dataset_folder, resident_name)
    os.makedirs(resident_folder, exist_ok=True)

    # Extract file name and download image
    image_name = os.path.basename(image_url.split('?')[0])
    local_file_path = os.path.join(resident_folder, image_name)

    print(f"[INFO] Downloading {image_url} to {local_file_path}")
    urllib.request.urlretrieve(image_url, local_file_path)
    print(f"[INFO] Image saved to {local_file_path}")

# Start listening to Firestore collection 'photos'
col_query = db.collection(u'photos')
col_query.on_snapshot(on_snapshot)

print("[INFO] Listening for new Firestore uploads...")
while True:
    time.sleep(60)  # Keep the script alive
