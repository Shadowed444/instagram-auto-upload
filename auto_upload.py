import os
import subprocess
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Instagram Auto Uploader is Running!"

if __name__ == '__main__':
    # Install required dependencies (fix for missing dropbox module)
    subprocess.run(["pip", "install", "dropbox"])

    # Start video scheduler script
    try:
        subprocess.Popen(["python3", "video_scheduler.py"])
        print("Video scheduler script started successfully.")
    except Exception as e:
        print("Error running video scheduler:", e)

    # Run Flask app (to keep Koyeb service running)
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
