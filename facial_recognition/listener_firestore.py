import firebase_admin
from firebase_admin import credentials, firestore, storage
import urllib.request
import os
import time
from train_faces import train_faces  # Your existing training function

# ------------------------- #
# ✅ CONFIGURATION
# ------------------------- #
CREDENTIALS_FILE = "capstone-app-59cf7-firebase-adminsdk-62bt7-90f6bae67f.json"
BUCKET_NAME = "capstone-app-59cf7.appspot.com"  # Match your Firebase bucket exactly
PROCESSED_PHOTOS_FILE = 'processed_photos.txt'

# ------------------------- #
# ✅ INITIALIZE FIREBASE
# ------------------------- #
cred = credentials.Certificate(CREDENTIALS_FILE)
firebase_admin.initialize_app(cred, {
    'storageBucket': BUCKET_NAME
})

db = firestore.client()
bucket = storage.bucket()

# ------------------------- #
# ✅ PROCESSED PHOTOS TRACKING
# ------------------------- #
def load_processed_photos():
    """Load already processed photo paths from a file."""
    if not os.path.exists(PROCESSED_PHOTOS_FILE):
        return set()

    with open(PROCESSED_PHOTOS_FILE, 'r') as file:
        return set(line.strip() for line in file)

def save_processed_photo(photo_path):
    """Save a newly processed photo path to the file."""
    with open(PROCESSED_PHOTOS_FILE, 'a') as file:
        file.write(f"{photo_path}\n")

# Initialize processed photos tracking at startup
processed_photos = load_processed_photos()

# ------------------------- #
# ✅ DOWNLOAD IMAGE
# ------------------------- #
def download_and_save_image(resident_name, image_url):
    """Download a photo from Firebase Storage URL and save it locally."""
    dataset_folder = os.path.join(os.getcwd(), 'dataset')
    resident_folder = os.path.join(dataset_folder, resident_name)
    os.makedirs(resident_folder, exist_ok=True)

    # Extract the image file name from the URL
    image_name = os.path.basename(image_url.split('?')[0])
    local_file_path = os.path.join(resident_folder, image_name)

    print(f"[INFO] Downloading {image_url} to {local_file_path}")
    urllib.request.urlretrieve(image_url, local_file_path)
    print(f"[INFO] Image saved to {local_file_path}")

# ------------------------- #
# ✅ FIRESTORE SNAPSHOT LISTENER
# ------------------------- #
def on_snapshot(col_snapshot, changes, read_time):
    global processed_photos
    for change in changes:
        if change.type.name in ('ADDED', 'MODIFIED'):
            doc = change.document.to_dict()

            # Expecting these fields in Firestore document
            resident_name = doc.get('resident')
            photo_paths = doc.get('photoPath', [])

            if not resident_name or not photo_paths:
                print("[WARN] Missing resident name or photo paths. Skipping...")
                continue

            print(f"[INFO] Processing photos for resident: {resident_name}")

            new_photos = []

            # Iterate over each photo in the document
            for photo_url in photo_paths:
                if photo_url not in processed_photos:
                    try:
                        # Download the image
                        download_and_save_image(resident_name, photo_url)

                        # Mark as processed
                        processed_photos.add(photo_url)
                        save_processed_photo(photo_url)

                        # Get the local path of the saved image
                        image_name = os.path.basename(photo_url.split('?')[0])
                        local_file_path = os.path.join(os.getcwd(), 'dataset', resident_name, image_name)

                        # Append local file path to new_photos (not URL)
                        new_photos.append(local_file_path)

                    except Exception as e:
                        print(f"[ERROR] Failed to download {photo_url}: {e}")

            # Retrain if there are new photos
            if new_photos:
                print(f"[INFO] New photos detected for {resident_name}. Retraining model...")
                train_faces(new_photos, resident_name)
            else:
                print(f"[INFO] No new photos to process for {resident_name}.")

# ------------------------- #
# ✅ START LISTENING
# ------------------------- #
col_query = db.collection(u'resident_photos')
col_query.on_snapshot(on_snapshot)

print("[INFO] Listening for new or updated Firestore documents...")

# Keep the script alive
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    print("[INFO] Exiting listener.")
