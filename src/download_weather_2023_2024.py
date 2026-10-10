
import requests
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = BASE_DIR / "data" / "original" / "weather"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Use the same location as the existing weather dataset.
LATITUDE = 51.493847
LONGITUDE = -0.1630249

URL = "https://archive-api.open-meteo.com/v1/archive"

params = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "start_date": "2023-01-01",
    "end_date": "2024-12-31",
    "daily": [
        "temperature_2m_max",
        "temperature_2m_min",
        "relative_humidity_2m_mean",
    ],
    "timezone": "Europe/London",
}

print("Downloading historical weather for 2023–2024...")

response = requests.get(URL, params=params, timeout=120)
response.raise_for_status()

data = response.json()

if "daily" not in data:
    raise ValueError(f"Daily weather data missing: {data}")

weather = pd.DataFrame(data["daily"])

weather = weather.rename(columns={
    "time": "Date",
    "temperature_2m_max": "Max_Temp_C",
    "temperature_2m_min": "Min_Temp_C",
    "relative_humidity_2m_mean": "Humidity_Pct",
})

weather["Date"] = pd.to_datetime(weather["Date"])

output_file = OUTPUT_DIR / "weather_2023_2024_daily.csv"
weather.to_csv(output_file, index=False)

print("\nDownload complete.")
print("Rows:", len(weather))
print("Start date:", weather["Date"].min().date())
print("End date:", weather["Date"].max().date())
print("Missing values:")
print(weather.isnull().sum())
print("Saved to:", output_file)