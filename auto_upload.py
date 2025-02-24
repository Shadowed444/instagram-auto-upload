import os
import subprocess
import threading
import time
import requests
from flask import Flask

# Dropbox Credentials
CLIENT_ID = "wjub96mx3xfebsl"
CLIENT_SECRET = "4s2bt6ncmw7swf4"
REFRESH_TOKEN = "JfUGJd-z77MAAAAAAAAAAYo51xCsWrJAIFvaowichz17at3Y-FVOn5j9gxIedx5i"

# Koyeb API Credentials
KOYEB_API_KEY = "c4nw8bfzftp9rryluzgczgzl99wmtpui03ts8xaxk2fasfonlp7503ue0z27yqqa"
KOYEB_APP_ID = "marcsempire-8e608ee6"
KOYEB_ENV_VAR_NAME = "DROPBOX_ACCESS_TOKEN"

app = Flask(__name__)

@app.route('/')
def home():
    return "Instagram Auto Uploader is Running!"

def refresh_dropbox_token():
    """Refreshes the Dropbox access token every 3.5 hours."""
    while True:
        try:
            url = "https://api.dropbox.com/oauth2/token"
            data = {
                "grant_type": "refresh_token",
                "refresh_token": REFRESH_TOKEN,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET
            }
            response = requests.post(url, data=data)
            if response.status_code == 200:
                access_token = response.json().get("access_token")
                print("[INFO] New Access Token:", access_token)
                update_koyeb_env_var(access_token)
            else:
                print("[ERROR] Failed to refresh token:", response.json())
        except Exception as e:
            print("[ERROR] Exception in refreshing token:", str(e))
        
        time.sleep(12600)  # 3.5 hours (3.5 * 60 * 60 = 12600 seconds)

def update_koyeb_env_var(new_token):
    """Updates the Dropbox access token in Koyeb."""
    try:
        url = f"https://app.koyeb.com/v1/apps/{KOYEB_APP_ID}/services"
        headers = {"Authorization": f"Bearer {KOYEB_API_KEY}", "Content-Type": "application/json"}
        service_response = requests.get(url, headers=headers)
        if service_response.status_code != 200:
            print("[ERROR] Failed to fetch Koyeb services:", service_response.json())
            return
        service_id = service_response.json()["services"][0]["id"]
        env_vars = [{"key": KOYEB_ENV_VAR_NAME, "value": new_token, "visibility": "runtime"}]
        update_url = f"https://app.koyeb.com/v1/services/{service_id}/deploy"
        update_data = {"env": env_vars}
        update_response = requests.post(update_url, json=update_data, headers=headers)
        if update_response.status_code == 200:
            print("[SUCCESS] Dropbox token updated in Koyeb!")
        else:
            print("[ERROR] Failed to update Koyeb environment variable:", update_response.json())
    except Exception as e:
        print("[ERROR] Exception in updating Koyeb token:", str(e))

if __name__ == '__main__':
    # Install required dependencies (fix for missing dropbox module)
    subprocess.run(["pip", "install", "dropbox"])
    
    # Start video scheduler script
    try:
        subprocess.Popen(["python3", "video_scheduler.py"])
        print("[SUCCESS] Video scheduler script started successfully.")
    except Exception as e:
        print("[ERROR] Failed to start video scheduler:", e)
    
    # Start token refresh thread
    threading.Thread(target=refresh_dropbox_token, daemon=True).start()
    
    # Run Flask app (to keep Koyeb service running)
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
