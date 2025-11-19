import random
from src.config import VERIFICATION_THRESHOLD

class VerifyAgent:
    def __init__(self):
        pass

    def verify(self, incident_data):
        """
        Verifies an incident by cross-referencing with "search results".
        Returns a credibility score (0-100) and verification notes.
        """
        # In a real production system, this would call Google Search API
        # and use an LLM to check if search results match the incident claim.
        
        # For this hackathon/demo, we simulate verification logic based on keywords.
        
        text = incident_data.get("summary", "").lower()
        source = incident_data.get("source", "twitter")
        
        score = 0
        notes = []
        
        # 1. Source Credibility
        if source == "local_news":
            score += 50
            notes.append("Source is a trusted local news outlet.")
        elif source == "twitter":
            score += 10
            notes.append("Source is social media (unverified).")
            
        # 2. Content Analysis (Simulated Search Cross-Reference)
        # We simulate that "Fire", "Flood", "Earthquake" are being reported by others.
        if "fake" in text or "movie set" in text:
            score = 0
            notes.append("Flagged as potential misinformation/spam.")
        else:
            # Simulate finding other corroborating reports
            score += random.randint(20, 40) 
            notes.append("Found corroborating reports from other users.")
            
        # 3. Location Verification
        if incident_data.get("coordinates"):
            score += 20
            notes.append("Location is valid and specific.")
            
        # Cap score at 100
        score = min(score, 100)
        
        return {
            "credibility_score": score,
            "verification_notes": "; ".join(notes),
            "is_verified": score >= VERIFICATION_THRESHOLD
        }
