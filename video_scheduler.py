import dropbox
import os
import random
import time
from datetime import datetime

# Dropbox API Setup
DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

# Folder paths
SCHEDULED_FOLDER = "/Scheduled_Videos"
TO_POST_FOLDER = "/To_Post"

# Function to list files in a Dropbox folder
def list_files(folder_path):
    try:
        files = dbx.files_list_folder(folder_path).entries
        return [file.name for file in files if isinstance(file, dropbox.files.FileMetadata)]
    except Exception as e:
        print(f"[ERROR] Failed to list files in {folder_path}: {e}")
        return []

# Function to move a video from Scheduled to To_Post
def move_video():
    files = list_files(SCHEDULED_FOLDER)
    
    if not files:
        print("[INFO] No videos left to schedule.")
        return None  # No video to post

    # Select a random video
    selected_video = random.choice(files)
    source_path = f"{SCHEDULED_FOLDER}/{selected_video}"
    destination_path = f"{TO_POST_FOLDER}/{selected_video}"

    try:
        dbx.files_move_v2(source_path, destination_path)
        print(f"[SUCCESS] Moved {selected_video} to {TO_POST_FOLDER} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return selected_video  # Return the moved file name
    except Exception as e:
        print(f"[ERROR] Failed to move {selected_video}: {e}")
        return None

# **Run only once, no infinite loop**
if __name__ == "__main__":
    video = move_video()
    if video:
        print(f"[INFO] {video} is now in the To_Post folder.")

