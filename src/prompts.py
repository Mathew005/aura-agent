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
1. Target Twitter for recent posts (use site:twitter.com and include "latest" or "now").
2. Target Reddit: If you know a specific local subreddit (e.g., r/LosAngeles), use "r/LosAngeles". If not, use "site:reddit.com".
3. Target local news or official alerts with keywords like "today", "live", or "current".

Return ONLY a raw JSON list of strings. Example: ["site:twitter.com fire latest", "r/LosAngeles smoke", "site:reddit.com flood today"]
"""
# --- Verify Agent ---
VERIFY_PROMPT = """
You are a Fact-Checking Analyst.
Your task is to verify a reported incident using the provided search results (evidence).

Incident Report:
- Type: {incident_type}
- Location: {location}
- Summary: {summary}

Evidence (Search Results):
{evidence}

Instructions:
1. Compare the Incident Report with the Evidence.
2. **CRITICAL: Check for Recency.**
   - If the evidence describes an event from months or years ago, REJECT it (Score 0).
   - Look for keywords like "today", "just now", "hours ago", or current dates.
   - If the evidence is undated or old, do not verify.
3. Look for matching details: Location, Event Type, and specific descriptions.
4. Assign a Credibility Score (0-100).
   - 0-20: No evidence found, evidence contradicts report, or **EVIDENCE IS OUTDATED**.
   - 21-50: Weak evidence (vague mentions, unverified sources).
   - 51-79: Moderate evidence (multiple unverified sources or one reliable source).
   - 80-100: Strong evidence (multiple reliable sources, official accounts, photos/videos mentioned, **CONFIRMED RECENT**).
5. Provide a brief explanation for the score.

Return ONLY a JSON object:
{{
    "credibility_score": <int>,
    "verification_notes": "<string explanation>",
    "is_verified": <bool (true if score >= 70)>
}}
"""
