import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from src.tools.map_tools import get_coordinates

load_dotenv()

class ExtractAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-flash-lite-latest")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
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

        prompt = f"""
        You are an expert disaster response coordinator. 
        Analyze the following social media post and extract structured data.
        
        Post: "{text}"
        
        Return ONLY a JSON object with the following keys:
        - location_text: The specific location mentioned (e.g., "5th and Elm").
        - incident_type: The type of incident (e.g., "Fire", "Flood", "Earthquake").
        - severity: "Low", "Medium", "High", or "Critical".
        - summary: A brief 1-sentence summary of the situation.
        - confidence: A score from 0.0 to 1.0 indicating how confident you are that this is a real actionable incident.
        
        JSON:
        """
        
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
                data["coordinates"] = [34.0522, -118.2437] # Default fallback
                
            return data
            
        except Exception as e:
            print(f"Extraction error: {e}")
            return {
                "location_text": "Error",
                "coordinates": [34.0522, -118.2437],
                "incident_type": "Error",
                "severity": "Low",
                "summary": "Failed to extract data.",
                "confidence": 0.0
            }
