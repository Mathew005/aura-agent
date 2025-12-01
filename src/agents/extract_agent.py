import json
import google.generativeai as genai
from src.tools.map_tools import get_coordinates
from src.config import GOOGLE_API_KEY, GEMINI_MODEL_NAME, DEFAULT_MAP_CENTER
from src.prompts import EXTRACT_PROMPT
from src.utils.rate_limiter import handle_rate_limit

class ExtractAgent:
    """
    The Extract Agent is the first line of defense in the AURA pipeline.
    
    **Role**: Intelligence Officer
    **Goal**: Convert unstructured chaos (raw text) into structured order (JSON).
    
    **Key Responsibilities**:
    1.  **Entity Extraction**: Identifies location, incident type, and severity from raw reports.
    2.  **Geocoding**: Converts vague location names (e.g., "near the old bridge") into precise Lat/Lon coordinates.
    3.  **Noise Filtering**: Discards irrelevant data before it enters the system.
    """
    def __init__(self):
        if GOOGLE_API_KEY:
            genai.configure(api_key=GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        else:
            self.model = None
            print("Warning: GOOGLE_API_KEY not found. ExtractAgent will use mock mode.")

    def extract(self, text, mock_mode=False):
        """
        Extracts structured data from unstructured text using Gemini 2.5 Flash.
        
        Args:
            text (str): The raw input text (tweet, news headline, etc.).
            mock_mode (bool): If True, uses regex/keyword matching instead of LLM (for testing).
            
        Returns:
            dict: A dictionary containing:
                - location_text (str): The identified location name.
                - coordinates (list): [Lat, Lon].
                - incident_type (str): e.g., "Fire", "Flood".
                - severity (str): "Low", "Medium", "High", "Critical".
                - confidence (float): The agent's confidence in the extraction.
        """
        if not self.model or mock_mode:
            # Smart Mock: Detect specific locations in text
            cities = {
                "Shinjuku": [35.6938, 139.7034],
                "Tokyo": [35.6762, 139.6503],
                "Dadar": [19.0178, 72.8478],
                "Mumbai": [19.0760, 72.8777],
                "Katoomba": [-33.7125, 150.3119],
                "Leura": [-33.7120, 150.3300],
                "Blue Mountains": [-33.7125, 150.3119],
                "Miami Beach": [25.7906, -80.1300],
                "Ocean Drive": [25.7800, -80.1300],
                "Grindavik": [63.8424, -22.4338],
                "Keflavik": [63.9960, -22.5640],
                "Turkana": [3.1167, 35.6000],
                "Lodwar": [3.1167, 35.6000],
                "Cusco": [-13.5319, -71.9675],
                "Machu Picchu": [-13.1631, -72.5450],
                "Valparaiso": [-33.0472, -71.6127],
                "Munich": [48.1351, 11.5820],
                "Cox's Bazar": [21.4272, 92.0058]
            }
            
            detected_city = "Unknown Location"
            coords = DEFAULT_MAP_CENTER
            
            for city, city_coords in cities.items():
                if city.lower() in text.lower():
                    detected_city = city
                    coords = city_coords
                    break
            
            # Fallback for "5th and Elm" if no city found but it looks like a local report
            if detected_city == "Unknown Location":
                detected_city = "Global Monitor"
            
            return {
                "location_text": detected_city,
                "coordinates": coords,
                "incident_type": "Fire" if "fire" in text.lower() else "Flood" if "flood" in text.lower() or "water" in text.lower() else "Earthquake" if "quake" in text.lower() else "Hazard",
                "severity": "Critical" if "severe" in text.lower() or "massive" in text.lower() else "High",
                "summary": text,
                "confidence": 0.95
            }

        prompt = EXTRACT_PROMPT.format(text=text)
        
        retries = 3
        last_error = None
        
        import time
        import re
        
        for attempt in range(retries):
            try:
                response = self.model.generate_content(prompt)
                # Clean up response to ensure it's valid JSON
                content = response.text.strip()
                if content.startswith("```json"):
                    content = content[7:-3]
                elif content.startswith("```"):
                    content = content[3:-3]
                
                data = json.loads(content)
                
                # Geocode the location
                coords = get_coordinates(data.get("location_text", ""), mock_mode=mock_mode)
                if coords:
                    data["coordinates"] = coords
                else:
                    data["coordinates"] = DEFAULT_MAP_CENTER # Default fallback
                    
                return data
                
            except Exception as e:
                last_error = e
                print(f"Extraction error (Attempt {attempt+1}/{retries}): {e}")
                
                if handle_rate_limit(e):
                    continue # Retry immediately after sleeping
                else:
                    time.sleep(2 ** attempt) # Exponential backoff for non-rate-limit errors
        
        return {
            "location_text": "Error",
            "coordinates": DEFAULT_MAP_CENTER,
            "incident_type": "Error",
            "severity": "Low",
            "summary": f"Failed to extract data. Error: {last_error}",
            "confidence": 0.0
        }
