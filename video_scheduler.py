import dropbox
import os
import random
import time
import requests
from datetime import datetime

# Dropbox API Setup
DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")
DROPBOX_CLIENT_ID = os.getenv("DROPBOX_CLIENT_ID")
DROPBOX_CLIENT_SECRET = os.getenv("DROPBOX_CLIENT_SECRET")

SCHEDULED_FOLDER = "/Scheduled_Videos"
TO_POST_FOLDER = "/To_Post"

# Function to refresh Dropbox access token
def refresh_dropbox_token():
    global DROPBOX_ACCESS_TOKEN
    try:
        response = requests.post(
            "https://api.dropbox.com/oauth2/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": DROPBOX_REFRESH_TOKEN,
                "client_id": DROPBOX_CLIENT_ID,
                "client_secret": DROPBOX_CLIENT_SECRET,
            },
        )
        if response.status_code == 200:
            new_access_token = response.json()["access_token"]
            DROPBOX_ACCESS_TOKEN = new_access_token
            print("[SUCCESS] Dropbox access token refreshed.")
        else:
            print(f"[ERROR] Failed to refresh token: {response.text}")
    except Exception as e:
        print(f"[ERROR] Exception while refreshing token: {e}")

# Function to list files in a Dropbox folder
def list_files(folder_path):
    try:
        dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
        files = dbx.files_list_folder(folder_path).entries
        return [file.name for file in files if isinstance(file, dropbox.files.FileMetadata)]
    except dropbox.exceptions.AuthError:
        print("[WARNING] Access token expired, refreshing...")
        refresh_dropbox_token()
        return list_files(folder_path)  # Retry after refresh
    except Exception as e:
        print(f"[ERROR] Failed to list files in {folder_path}: {e}")
        return []

# Function to move a video from Scheduled to To_Post
def move_video():
    files = list_files(SCHEDULED_FOLDER)
    
    if not files:
        print("[INFO] No videos left to schedule.")
        return None

    selected_video = random.choice(files)
    source_path = f"{SCHEDULED_FOLDER}/{selected_video}"
    destination_path = f"{TO_POST_FOLDER}/{selected_video}"

    try:
        dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
        dbx.files_move_v2(source_path, destination_path)
        print(f"[SUCCESS] Moved {selected_video} to {TO_POST_FOLDER} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return selected_video
    except dropbox.exceptions.AuthError:
        print("[WARNING] Access token expired, refreshing...")
        refresh_dropbox_token()
        return move_video()  # Retry after refresh
    except Exception as e:
        print(f"[ERROR] Failed to move {selected_video}: {e}")
        return None

if __name__ == "__main__":
    video = move_video()
    if video:
        print(f"[INFO] {video} is now in the To_Post folder.")
