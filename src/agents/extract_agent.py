import json
import google.generativeai as genai
from src.tools.map_tools import get_coordinates
from src.config import GOOGLE_API_KEY, GEMINI_MODEL_NAME, DEFAULT_MAP_CENTER
from src.prompts import EXTRACT_PROMPT

class ExtractAgent:
    def __init__(self):
        if GOOGLE_API_KEY:
            genai.configure(api_key=GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        else:
            self.model = None
            print("Warning: GOOGLE_API_KEY not found. ExtractAgent will use mock mode.")

    def extract(self, text, mock_mode=False):
        """
        Extracts structured data from unstructured text.
        Returns a dictionary with location, incident_type, severity, etc.
        """
        if not self.model or mock_mode:
            # Mock response for testing without API key or to save quota
            return {
                "location_text": "5th and Elm", # Default mock location
                "coordinates": [34.0430, -118.2673],
                "incident_type": "Fire" if "fire" in text.lower() else "Flood" if "water" in text.lower() else "Earthquake",
                "severity": "High",
                "summary": text,
                "confidence": 0.85
            }

        prompt = EXTRACT_PROMPT.format(text=text)
        
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
            print(f"Extraction error: {e}")
            return {
                "location_text": "Error",
                "coordinates": DEFAULT_MAP_CENTER,
                "incident_type": "Error",
                "severity": "Low",
                "summary": "Failed to extract data.",
                "confidence": 0.0
            }
