# prompts.py

# --- Extraction Agent ---
EXTRACT_PROMPT = """
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

# --- Memory Agent ---
SEMANTIC_SIMILARITY_PROMPT = """
Do these two disaster reports refer to the same specific event?

Report 1: "{text1}"
Report 2: "{text2}"

Answer ONLY "YES" or "NO".
"""

# --- Scout Agent ---
SCOUT_PROMPT = """
You are an intelligent Scout Agent for disaster response.
Context: "{incident_context}"

Generate 3 specific, high-value search queries to find real-time on-the-ground updates.
1. Target Twitter for recent posts (use site:twitter.com).
2. Target Reddit: If you know a specific local subreddit (e.g., r/LosAngeles), use "r/LosAngeles". If not, use "site:reddit.com".
3. Target local news or official alerts.

Return ONLY a raw JSON list of strings. Example: ["site:twitter.com fire", "r/LosAngeles", "site:reddit.com smoke"]
"""
