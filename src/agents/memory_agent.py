import numpy as np
from datetime import datetime
import google.generativeai as genai
from src.config import GOOGLE_API_KEY, GEMINI_MODEL_NAME
from src.prompts import SEMANTIC_SIMILARITY_PROMPT

class MemoryAgent:
    def __init__(self):
        # In-memory storage for incidents
        # Each incident is a dict with: id, type, location, severity, reports (list), last_updated
        self.incidents = []
        self.next_id = 1
        
        if GOOGLE_API_KEY:
            # Note: genai.configure is often called once, but this ensures it's set if other agents aren't used.
            genai.configure(api_key=GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        else:
            self.model = None

    def _calculate_distance(self, coord1, coord2):
        """
        Calculate euclidean distance between two lat/long points.
        For small distances, this is a sufficient approximation.
        """
        return np.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

    def _check_semantic_similarity(self, text1, text2, mock_mode=False):
        """
        Uses LLM to check if two incident descriptions refer to the same event.
        """
        if not self.model or mock_mode:
            # Simple keyword matching for mock mode
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            overlap = len(words1.intersection(words2))
            return overlap >= 2 # Arbitrary threshold for mock

        prompt = SEMANTIC_SIMILARITY_PROMPT.format(text1=text1, text2=text2)
        try:
            response = self.model.generate_content(prompt)
            return "YES" in response.text.strip().upper()
        except:
            return False

    def consolidate(self, new_report, mock_mode=False):
        """
        Checks if a new report matches an existing incident.
        If yes, merges it. If no, creates a new incident.
        """
        # Threshold for spatial merging (approx 1km or less)
        DISTANCE_THRESHOLD = 0.01 
        
        best_match = None
        min_dist = float('inf')
        
        new_coords = new_report.get("coordinates")
        if not new_coords:
            return None # Can't plot without location
            
        for incident in self.incidents:
            # Check incident type match
            if incident["type"] != new_report["incident_type"]:
                continue
                
            # Check distance
            dist = self._calculate_distance(new_coords, incident["coordinates"])
            
            # Semantic Check: If close by, check if it's the same event
            if dist < DISTANCE_THRESHOLD:
                # Get the summary of the first report in the incident to compare
                existing_summary = incident["reports"][0].get("summary", "")
                new_summary = new_report.get("summary", "")
                
                if self._check_semantic_similarity(existing_summary, new_summary, mock_mode):
                    if dist < min_dist:
                        min_dist = dist
                        best_match = incident
        
        if best_match:
            # Merge into existing incident
            best_match["reports"].append(new_report)
            best_match["last_updated"] = datetime.now().isoformat()
            best_match["confidence"] = min(1.0, best_match["confidence"] + 0.1) # Increase confidence
            
            # Update severity if new report is higher
            # (Simple logic: Critical > High > Medium > Low)
            severity_levels = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
            current_sev = severity_levels.get(best_match["severity"], 1)
            new_sev = severity_levels.get(new_report["severity"], 1)
            if new_sev > current_sev:
                best_match["severity"] = new_report["severity"]
                
            return {
                "action": "merged",
                "incident_id": best_match["id"],
                "incident_title": f"{best_match['type']} at {best_match['location_text']}"
            }
        else:
            # Create new incident
            new_incident = {
                "id": self.next_id,
                "type": new_report["incident_type"],
                "location_text": new_report["location_text"],
                "coordinates": new_report["coordinates"],
                "severity": new_report["severity"],
                "confidence": new_report["confidence"],
                "reports": [new_report],
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            self.incidents.append(new_incident)
            self.next_id += 1
            
            return {
                "action": "created",
                "incident_id": new_incident["id"],
                "incident_title": f"{new_incident['type']} at {new_incident['location_text']}"
            }

    def get_all_incidents(self):
        return self.incidents
