import os
import time
import random
import dropbox
from flask import Flask
from datetime import datetime
import requests

app = Flask(__name__)

# Environment Variables
PORT = int(os.getenv("PORT", 8080))
DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")
DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")

# Dropbox Folder Paths
SCHEDULED_FOLDER = "/Scheduled_Videos"
TO_POST_FOLDER = "/To_Post"

# Function to Refresh Dropbox Access Token
def refresh_dropbox_token():
    global DROPBOX_ACCESS_TOKEN
    try:
        response = requests.post(
            "https://api.dropbox.com/oauth2/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": DROPBOX_REFRESH_TOKEN,
                "client_id": DROPBOX_APP_KEY,
                "client_secret": DROPBOX_APP_SECRET,
            },
        )
        response.raise_for_status()
        new_token = response.json()["access_token"]
        DROPBOX_ACCESS_TOKEN = new_token  # Update variable in script
        print("[SUCCESS] Dropbox access token refreshed.")
    except Exception as e:
        print(f"[ERROR] Failed to refresh Dropbox access token: {e}")

# Initialize Dropbox Client
def get_dropbox_client():
    return dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

def list_files(dbx, folder_path):
    try:
        files = dbx.files_list_folder(folder_path).entries
        return [file.name for file in files if isinstance(file, dropbox.files.FileMetadata)]
    except Exception as e:
        print(f"[ERROR] Failed to list files in {folder_path}: {e}")
        return []

def move_video():
    refresh_dropbox_token()  # Refresh token before making API calls
    dbx = get_dropbox_client()
    files = list_files(dbx, SCHEDULED_FOLDER)
    
    if not files:
        print("[INFO] No videos left to schedule.")
        return None

    selected_video = random.choice(files)
    source_path = f"{SCHEDULED_FOLDER}/{selected_video}"
    destination_path = f"{TO_POST_FOLDER}/{selected_video}"

    try:
        dbx.files_move_v2(source_path, destination_path)
        print(f"[SUCCESS] Moved {selected_video} to {TO_POST_FOLDER} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return selected_video
    except Exception as e:
        print(f"[ERROR] Failed to move {selected_video}: {e}")
        return None

@app.route("/")
def home():
    return "Server is running!"

if __name__ == "__main__":
    move_video()
    app.run(host="0.0.0.0", port=PORT)
