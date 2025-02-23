import requests
import os

# Your Dropbox App Credentials
CLIENT_ID = "wjub96mx3xfebsl"
CLIENT_SECRET = "4s2bt6ncmw7swf4"
REFRESH_TOKEN = "JfUGJd-z77MAAAAAAAAAAYo51xCsWrJAIFvaowichz17at3Y-FVOn5j9gxIedx5i"

# Koyeb API Credentials
KOYEB_API_KEY = "c4nw8bfzftp9rryluzgczgzl99wmtpui03ts8xaxk2fasfonlp7503ue0z27yqqa"  # Get this from Koyeb API settings
KOYEB_APP_ID = "marcsempire-8e608ee6"    # Find this in your Koyeb app URL
KOYEB_ENV_VAR_NAME = "DROPBOX_ACCESS_TOKEN"  # The environment variable in Koyeb

def refresh_dropbox_token():
    """Refreshes the Dropbox access token using the refresh token."""
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
        print("New Access Token:", access_token)
        update_koyeb_env_var(access_token)
    else:
        print("Error refreshing token:", response.json())

def update_koyeb_env_var(new_token):
    """Updates the Dropbox access token in Koyeb."""
    url = f"https://app.koyeb.com/v1/apps/{KOYEB_APP_ID}/services"
    headers = {"Authorization": f"Bearer {KOYEB_API_KEY}", "Content-Type": "application/json"}
    
    # Fetch the current service ID
    service_response = requests.get(url, headers=headers)
    if service_response.status_code != 200:
        print("Failed to fetch Koyeb services:", service_response.json())
        return

    service_id = service_response.json()["services"][0]["id"]
    env_vars = [
        {
            "key": KOYEB_ENV_VAR_NAME,
            "value": new_token,
            "visibility": "runtime"
        }
    ]

    # Update Environment Variable
    update_url = f"https://app.koyeb.com/v1/services/{service_id}/deploy"
    update_data = {"env": env_vars}
    
    update_response = requests.post(update_url, json=update_data, headers=headers)
    
    if update_response.status_code == 200:
        print("Successfully updated Dropbox token in Koyeb!")
    else:
        print("Failed to update Koyeb environment variable:", update_response.json())

if __name__ == "__main__":
    refresh_dropbox_token()
