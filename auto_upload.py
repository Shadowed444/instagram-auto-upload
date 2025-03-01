import os
import sys
import subprocess

sys.path.append('/workspace/.heroku/python/lib/python3.10/site-packages')

from moviepy.editor import VideoFileClip  # Now import moviepy

import time
import random
import dropbox
from flask import Flask
from datetime import datetime
import requests
import pytz  # Import timezone module
import instagrapi
import pickle
import pkg_resources

installed_packages = [pkg.key for pkg in pkg_resources.working_set]
print("[INFO] Installed packages:", installed_packages)

app = Flask(__name__)

# Environment Variables
PORT = int(os.getenv("PORT", 8080))
DROPBOX_APP_KEY = os.getenv("DROPBOX_APP_KEY")
DROPBOX_APP_SECRET = os.getenv("DROPBOX_APP_SECRET")
DROPBOX_REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")
DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
SESSION_FILE = "instagram_session.pkl"

# Dropbox Folder Paths
SCHEDULED_FOLDER = "/Scheduled_Videos"
TO_POST_FOLDER = "/To_Post"

# Define timezones
IST = pytz.timezone("Asia/Kolkata")
ET = pytz.timezone("America/New_York")  # Washington, DC time

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
        DROPBOX_ACCESS_TOKEN = new_token
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
    refresh_dropbox_token()
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
        print(f"[SUCCESS] Moved {selected_video} to {TO_POST_FOLDER} at {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')} IST")
        return selected_video
    except Exception as e:
        print(f"[ERROR] Failed to move {selected_video}: {e}")
        return None

# Instagram session handling
def load_instagram_session():
    client = instagrapi.Client()
    if os.path.exists(SESSION_FILE):
        try:
            client.load_settings(SESSION_FILE)
            client.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            print("[SUCCESS] Logged in using saved session.")
            return client
        except Exception as e:
            print(f"[WARNING] Failed to use saved session: {e}")
    
    # Fresh login if session fails
    try:
        client.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        client.dump_settings(SESSION_FILE)
        print("[SUCCESS] Logged in and session saved.")
        return client
    except Exception as e:
        print(f"[ERROR] Instagram login failed: {e}")
        return None

def upload_to_instagram(video_path, caption):
    client = load_instagram_session()
    if client:
        try:
            client.clip_upload(video_path, caption=caption)
            print(f"[SUCCESS] Uploaded {video_path} to Instagram.")
        except Exception as e:
            print(f"[ERROR] Failed to upload {video_path}: {e}")

@app.route("/")
def home():
    return "Server is running!"

def schedule_loop():
    while True:
        now = datetime.now(ET)  # Get current time in Washington, DC timezone
        ist_time = now.astimezone(IST).strftime("%H:%M")

        if ist_time in ["10:00", "19:30"]:  # Runs at 10:00 AM & 5:00 PM IST
            video = move_video()
            if video:
                video_path = f"/To_Post/{video}"
                caption = """Conquer yourself before you conquer the world

Find Your path here at @inspirexmarc

Check the link in bio for Internet resources fueled with inspiration👑...

#motivation #quotes #positivequotes #selfimprovement #mindset #growthmindset #discipline #proveyourself #inspirationalquotes #inspiration #positivity #relatable"""
                upload_to_instagram(video_path, caption)
            time.sleep(60)  # Prevent multiple moves within the same minute

        time.sleep(30)  # Check every 30 seconds

if __name__ == "__main__":
    from threading import Thread

    # Start the scheduled loop in a separate thread
    Thread(target=schedule_loop, daemon=True).start()

    # Start Flask server with the correct port logic
    app.run(host="0.0.0.0", port=PORT)
