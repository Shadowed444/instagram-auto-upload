import os
import subprocess
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Instagram Auto Uploader is Running!"

if __name__ == '__main__':
    # Start video scheduler script and ensure logs are visible
    try:
        print("Starting video scheduler script...")
        subprocess.run(["python3", "video_scheduler.py"], check=True)
    except Exception as e:
        print("Error running video scheduler:", e)
    
    # Run Flask app (to keep Koyeb service running)
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
