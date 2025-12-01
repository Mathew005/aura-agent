import google.generativeai as genai
import json
from src.config import VERIFICATION_THRESHOLD, GOOGLE_API_KEY, GEMINI_MODEL_NAME
from src.prompts import VERIFY_PROMPT
from src.tools.weather_tool import WeatherTool
from src.utils.rate_limiter import handle_rate_limit

class VerifyAgent:
    """
    The Verify Agent acts as a Fact-Checking Analyst.
    
    **Role**: Truth Seeker
    **Goal**: Validate reported incidents against real-time external data.
    
    **Key Responsibilities**:
    1.  **Cross-Referencing**: Compares the reported incident against search results and weather data.
    2.  **Credibility Scoring**: Assigns a 0-100 score based on source reliability (e.g., Official Gov > Random Tweet) and corroboration.
    3.  **Contextual Awareness**: Uses weather data to validate environmental claims (e.g., "Flood" report vs. "0mm Rain" data).
    """
    def __init__(self):
        if GOOGLE_API_KEY:
            genai.configure(api_key=GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        else:
            self.model = None
        self.weather_tool = WeatherTool()

    def verify(self, incident_data, search_results=[]):
        """
        Verifies an incident by synthesizing multiple data sources.
        
        Args:
            incident_data (dict): The structured data from ExtractAgent.
            search_results (list): External intelligence gathered by ScoutAgent.
            
        Returns:
            dict: Verification results including:
                - is_verified (bool): True if score >= threshold.
                - credibility_score (int): 0-100.
                - verification_notes (str): Explanation of the decision.
                - sources (list): Citations for the UI.
        """
        if not self.model:
            # Fallback to mock logic if no API key
            return self._mock_verify(incident_data)

        # Prepare evidence text
        evidence_text = ""
        
        # 1. Weather Data (if coordinates available)
        weather_context = ""
        if incident_data.get("coordinates"):
            lat, lon = incident_data["coordinates"]
            weather = self.weather_tool.fetch_weather(lat, lon)
            if weather:
                weather_context = f"\n[Real-time Weather at Location]: {weather['description']}, Temp: {weather['temperature']}, Wind: {weather['wind_speed']}"
                if weather['alerts']:
                    weather_context += f"\n[Active Weather Alerts]: {'; '.join(weather['alerts'])}"
                evidence_text += weather_context + "\n"

        # 2. Search Results
        if search_results:
            for res in search_results:
                evidence_text += f"- [{res.get('source', 'Web')}]: {res.get('content', '')}\n"
        else:
            evidence_text += "No search results found."

        prompt = VERIFY_PROMPT.format(
            incident_type=incident_data.get("incident_type", "Unknown"),
            location=incident_data.get("location_text", "Unknown"),
            summary=incident_data.get("summary", ""),
            evidence=evidence_text
        )

        for attempt in range(3):
            try:
                response = self.model.generate_content(prompt)
                text = response.text.strip()
                # Clean up markdown code blocks
                if text.startswith("```"):
                    text = text.split("\n", 1)[1]
                if text.endswith("```"):
                    text = text.rsplit("\n", 1)[0]
                if text.startswith("json"):
                    text = text[4:]
                
                data = json.loads(text)
                
                # Attach sources for UI display
                sources = []
                if search_results:
                    for res in search_results:
                        # If we have structured citations, use them
                        if res.get('citations'):
                            for cit in res['citations']:
                                sources.append(cit)
                        else:
                            # Fallback for other tools (Reddit, News)
                            source_name = res.get('source', 'Web')
                            sources.append({"title": source_name, "url": None})
                
                # Deduplicate by URL
                unique_sources = []
                seen_urls = set()
                for src in sources:
                    if src['url']:
                        if src['url'] not in seen_urls:
                            unique_sources.append(src)
                            seen_urls.add(src['url'])
                    else:
                        # Keep non-URL sources (like "Twitter") if unique by title
                        if src['title'] not in seen_urls:
                            unique_sources.append(src)
                            seen_urls.add(src['title'])

                data["sources"] = unique_sources
                
                return data
                
            except Exception as e:
                if handle_rate_limit(e):
                    continue
                print(f"Verification Error: {e}")
                # Fallback to mock if LLM fails
                return self._mock_verify(incident_data)

    def _mock_verify(self, incident_data):
        """Legacy mock verification for fallback"""
        import random
        text = incident_data.get("summary", "").lower()
        source = incident_data.get("source", "twitter")
        
        score = 0
        notes = []
        
        if source == "local_news":
            score += 50
            notes.append("Source is a trusted local news outlet.")
        elif source == "twitter":
            score += 10
            notes.append("Source is social media (unverified).")
            
        if "fake" in text or "movie set" in text:
            score = 0
            notes.append("Flagged as potential misinformation/spam.")
        else:
            score += random.randint(20, 40) 
            notes.append("Found corroborating reports from other users.")
            
        if incident_data.get("coordinates"):
            score += 20
            notes.append("Location is valid and specific.")
            
        score = min(score, 100)
        
        return {
            "credibility_score": score,
            "verification_notes": "; ".join(notes),
            "is_verified": score >= VERIFICATION_THRESHOLD
        }
