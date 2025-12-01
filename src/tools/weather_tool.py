import requests
import time
from src.config import OPEN_WEATHER_API

class WeatherTool:
    def __init__(self):
        self.api_key = OPEN_WEATHER_API
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    def fetch_weather(self, lat, lon):
        """
        Fetches current weather data for a given latitude and longitude.
        """
        if not self.api_key:
            print("Warning: OPEN_WEATHER_API key not found.")
            return None

        try:
            url = f"{self.base_url}?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Extract relevant current weather info (v2.5 structure)
            weather_desc = data.get("weather", [{}])[0].get("description", "Unknown")
            main = data.get("main", {})
            temp = main.get("temp", "Unknown")
            humidity = main.get("humidity", "Unknown")
            wind = data.get("wind", {})
            wind_speed = wind.get("speed", "Unknown")
            
            # v2.5 weather endpoint doesn't usually provide alerts in the same way as OneCall
            # We'll omit alerts for now or check if they exist in a different key if applicable
            alert_summary = [] 

            return {
                "description": weather_desc,
                "temperature": f"{temp}°C",
                "humidity": f"{humidity}%",
                "wind_speed": f"{wind_speed} m/s",
                "alerts": alert_summary
            }

        except Exception as e:
            print(f"Weather Fetch Error: {e}")
            return None
