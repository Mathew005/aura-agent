import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_coordinates(address, mock_mode=False):
    """
    Geocodes an address using Google Maps Geocoding API.
    Returns (lat, lng) tuple or None if not found.
    """
    api_key = os.getenv("MAPS_API_KEY")
    if not api_key or mock_mode:
        # Fallback/Mock for testing if no key is present
        # In a real scenario, we might want to raise an error or log a warning.
        # For this hackathon demo, we can return a default location or mock based on known addresses.
        if "5th" in address and "Elm" in address:
            return 34.0430, -118.2673 # Example coords
        if "West LA" in address:
            return 34.0500, -118.4400
        if "Downtown" in address or "downtown" in address:
            return 34.0407, -118.2468
        return 34.0522, -118.2437 # Default Los Angeles

    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": api_key
    }
    
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            print(f"Geocoding error: {data['status']}")
            return None
    except Exception as e:
        print(f"Geocoding exception: {e}")
        return None
