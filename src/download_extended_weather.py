
import requests
import pandas as pd
from pathlib import Path

# Same London-area location as your existing weather dataset
LATITUDE = 51.493847
LONGITUDE = -0.1630249

url = "https://archive-api.open-meteo.com/v1/archive"

params = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,
    "start_date": "2026-01-01",
    "end_date": "2026-08-31",
    "daily": [
        "temperature_2m_max",
        "temperature_2m_min",
        "relative_humidity_2m_mean"
    ],
    "timezone": "Europe/London"
}

response = requests.get(url, params=params, timeout=60)
response.raise_for_status()

data = response.json()
daily = pd.DataFrame({
    "Date": data["daily"]["time"],
    "Max_Temp_C": data["daily"]["temperature_2m_max"],
    "Min_Temp_C": data["daily"]["temperature_2m_min"],
    "Humidity_Pct": data["daily"]["relative_humidity_2m_mean"]
})

output = Path("data/original/weather")
output.mkdir(parents=True, exist_ok=True)

file_path = output / "weather_2026_daily.csv"
daily.to_csv(file_path, index=False)

print("Rows downloaded:", len(daily))
print("First date:", daily["Date"].min())
print("Last date:", daily["Date"].max())
print("Missing values:")
print(daily.isna().sum())
print("Saved:", file_path)

