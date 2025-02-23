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
        print("Error listing files:", e)
        return []

# Function to move a file
def move_video():
    files = list_files(SCHEDULED_FOLDER)
    if not files:
        print("No videos left to schedule.")
        return None  # No video to post

    # Select a random video
    selected_video = random.choice(files)
    source_path = f"{SCHEDULED_FOLDER}/{selected_video}"
    destination_path = f"{TO_POST_FOLDER}/{selected_video}"

    try:
        dbx.files_move_v2(source_path, destination_path)
        print(f"Moved {selected_video} to {TO_POST_FOLDER} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return selected_video  # Return the moved file name
    except Exception as e:
        print("Error moving video:", e)
        return None

# Function to delete the uploaded video
def delete_uploaded_video(video_name):
    video_path = f"{TO_POST_FOLDER}/{video_name}"
    try:
        dbx.files_delete_v2(video_path)
        print(f"Deleted {video_name} from {TO_POST_FOLDER} after uploading.")
    except Exception as e:
        print("Error deleting video:", e)

# Run the scheduler every 24 hours
while True:
    video = move_video()
    if video:
        time.sleep(60 * 60)  # Wait 1 hour (so Instagram has time to upload)
        delete_uploaded_video(video)
    
    time.sleep(24 * 60 * 60)  # Wait 24 hours before moving the next video
