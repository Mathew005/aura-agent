import requests
import time
from src.config import OPEN_WEATHER_API

class WeatherTool:
    def __init__(self):
        self.api_key = OPEN_WEATHER_API
        self.base_url = "https://api.openweathermap.org/data/3.0/onecall"

    def fetch_weather(self, lat, lon):
        """
        Fetches current weather data for a given latitude and longitude.
        """
        if not self.api_key:
            print("Warning: OPEN_WEATHER_API key not found.")
            return None

        try:
            url = f"{self.base_url}?lat={lat}&lon={lon}&exclude=minutely,hourly,daily&appid={self.api_key}&units=metric"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Extract relevant current weather info
            current = data.get("current", {})
            weather_desc = current.get("weather", [{}])[0].get("description", "Unknown")
            temp = current.get("temp", "Unknown")
            humidity = current.get("humidity", "Unknown")
            wind_speed = current.get("wind_speed", "Unknown")
            
            # Check for alerts
            alerts = data.get("alerts", [])
            alert_summary = []
            for alert in alerts:
                alert_summary.append(f"{alert.get('event', 'Alert')}: {alert.get('description', '')[:100]}...")

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
