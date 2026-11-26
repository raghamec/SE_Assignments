import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

# Check whichever env var name you use in .env
api_key =  os.getenv("SERPER_API_KEY")
print("Loaded key prefix:", api_key[:6] + "..." if api_key else "NONE")

url = "https://google.serper.dev/search"
headers = {
    "X-API-KEY": api_key,
    "Content-Type": "application/json",
}
payload = {"q": "latest AI news"}

response = requests.post(url, headers=headers, json=payload)
print("Status code:", response.status_code)
print(response.text[:500])