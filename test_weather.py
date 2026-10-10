
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not API_KEY:
    print("ERROR: API key not found in .env")
    raise SystemExit(1)

city = "Pune"
url = "https://api.openweathermap.org/data/2.5/weather"

params = {
    "q": city,
    "appid": API_KEY,
    "units": "metric"
}

try:
    response = requests.get(url, params=params, timeout=15)

    if response.status_code == 200:
        data = response.json()
        print("Weather API connected successfully!")
        print("City:", data["name"])
        print("Temperature:", data["main"]["temp"], "°C")
        print("Humidity:", data["main"]["humidity"], "%")
    else:
        print("API error:", response.status_code)
        print(response.json().get("message", "Unknown error"))

except requests.RequestException as error:
    print("Connection error:", error)