from flask import Flask
import threading
import time
import os

app = Flask(__name__)

# Function to run your automation script in the background
def run_automation():
    while True:
        print("Running automation script...")
        os.system("python auto_upload.py")  # Replace with your actual script
        time.sleep(3600)  # Runs every hour (adjust as needed)

# Start automation in a separate thread
threading.Thread(target=run_automation, daemon=True).start()

@app.route('/')
def home():
    return "Instagram Auto Upload is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
