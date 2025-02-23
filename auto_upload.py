import os
import time
import logging
from flask import Flask

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_automation():
    logging.info("Running automation script...")
    try:
        # Run your Instagram automation script here
        os.system("python auto_upload.py")  # Replace with your actual script
    except Exception as e:
        logging.error(f"Error running script: {e}")

@app.route('/')
def home():
    return "Instagram Auto Upload Service is Running!"

if __name__ == "__main__":
    # Use dynamic port assignment from the environment variable
    port = int(os.environ.get("PORT", 8080))  # Default to 8080 if PORT is not set
    logging.info(f"Starting server on port {port}...")
    
    # Run the automation script in a separate thread (optional)
    time.sleep(5)  # Small delay before execution
    run_automation()
    
    # Start Flask server
    app.run(host="0.0.0.0", port=port)
