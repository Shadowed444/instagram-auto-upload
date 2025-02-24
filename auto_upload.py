import requests
import os
import time

# Dropbox App Credentials (Get from Dropbox Developers Console)
CLIENT_ID = os.getenv("DROPBOX_CLIENT_ID")  # Store in Koyeb
CLIENT_SECRET = os.getenv("DROPBOX_CLIENT_SECRET")  # Store in Koyeb
REFRESH_TOKEN = os.getenv("DROPBOX_REFRESH_TOKEN")  # Store in Koyeb
KOYEB_API_KEY = os.getenv("KOYEB_API_KEY")  # Store in Koyeb
KOYEB_APP_ID = os.getenv("KOYEB_APP_ID")  # Store in Koyeb
KOYEB_ENV_VAR_NAME = "DROPBOX_ACCESS_TOKEN"  # Name of the token variable in Koyeb

def home():
    return "Service is running!"


def refresh_dropbox_token():
    """Refresh the Dropbox access token using the refresh token."""
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
        update_koyeb_env_var(access_token)  # Store it in Koyeb
    else:
        print("[ERROR] Failed to refresh access token:", response.json())

def update_koyeb_env_var(new_token):
    """Updates the Dropbox access token in Koyeb environment variables."""
    url = f"https://app.koyeb.com/v1/apps/{KOYEB_APP_ID}/services"
    headers = {"Authorization": f"Bearer {KOYEB_API_KEY}", "Content-Type": "application/json"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
    
    # Fetch the current service ID
    service_response = requests.get(url, headers=headers)
    if service_response.status_code != 200:
        print("[ERROR] Failed to fetch Koyeb services:", service_response.json())
        return

    service_id = service_response.json()["services"][0]["id"]
    env_vars = [
        {"key": KOYEB_ENV_VAR_NAME, "value": new_token, "visibility": "runtime"}
    ]

    # Update Environment Variable
    update_url = f"https://app.koyeb.com/v1/services/{service_id}/deploy"
    update_data = {"env": env_vars}
    
    update_response = requests.post(update_url, json=update_data, headers=headers)
    
    if update_response.status_code == 200:
        print("[SUCCESS] Dropbox token updated in Koyeb!")
    else:
        print("[ERROR] Failed to update Koyeb variable:", update_response.json())

# Schedule Token Refresh every 3.5 hours (12,600 seconds)
while True:
    refresh_dropbox_token()
    time.sleep(12600)

