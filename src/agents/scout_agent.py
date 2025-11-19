import google.generativeai as genai
import time
import json
from src.config import GOOGLE_API_KEY, GEMINI_MODEL_NAME
from src.prompts import SCOUT_PROMPT

class ScoutAgent:
    def __init__(self):
        if GOOGLE_API_KEY:
            genai.configure(api_key=GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        else:
            self.model = None

    def generate_strategy(self, incident_context):
        """
        Generates a search strategy based on the incident context (e.g., "Fire reported").
        Returns a list of search queries targeting different platforms.
        """
        if not self.model:
            return [
                f"site:twitter.com {incident_context}",
                f"site:reddit.com {incident_context}",
                f"{incident_context} news updates"
            ]

        prompt = SCOUT_PROMPT.format(incident_context=incident_context)
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            # Clean up markdown code blocks if present
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text.rsplit("\n", 1)[0]
            return json.loads(text)
        except Exception as e:
            print(f"Scout Strategy Error: {e}")
            return [f"{incident_context} updates", f"site:twitter.com {incident_context}"]

    def fetch_updates(self, queries, mock_mode=True):
        """
        Executes the search queries. 
        If mock_mode is True, generates simulated 'real-time' social media snippets.
        If mock_mode is False, uses RedditTool and GoogleSearchTool to simulate a "Grounded" agent experience.
        """
        results = []
        
        # Lazy import
        from src.tools.reddit_tool import RedditTool
        from src.tools.search_tool import GoogleSearchTool
        
        reddit_tool = RedditTool()
        search_tool = GoogleSearchTool()
        
        for query in queries:
            # Simulate "Thinking/Searching" time
            time.sleep(0.3)
            
            if mock_mode:
                # ... (Mock logic remains same) ...
                platform = "Twitter" if "twitter" in query else "Reddit" if "reddit" in query else "Web"
                keywords = query.replace("site:twitter.com", "").replace("site:reddit.com", "").strip()
                
                mock_content = f"LIVE REPORT: Situation regarding '{keywords}' is developing. Authorities are on scene. #alert"
                if platform == "Twitter":
                    mock_content = f"@{platform}User: Can see the {keywords} from my window! It's getting huge. #emergency"
                elif platform == "Reddit":
                    mock_content = f"r/{keywords}: Anyone else hearing those sirens near downtown? {keywords} confirmed."
                
                results.append({
                    "source": platform,
                    "query": query,
                    "content": mock_content,
                    "timestamp": "Just now"
                })
            else:
                # Real Data Integration (Native Grounding Simulation)
                # We use our tools to "ground" the agent's knowledge
                
                if query.startswith("r/"):
                    # Specific Subreddit Targeting (High Precision)
                    subreddit = query.split(" ")[0].replace("r/", "")
                    posts = reddit_tool.fetch_subreddit_posts(subreddit)
                    for post in posts:
                        post["query"] = query
                        results.append(post)
                else:
                    # Broad Web Search (Grounding)
                    # This acts as the "Google Search Retrieval" tool
                    search_results = search_tool.search(query)
                    for res in search_results:
                        res["query"] = query
                        results.append(res)
                        
                    # Fallback/Supplement: Check News
                    # ALWAYS check news to ensure real data flow
                    from src.tools.news_tool import NewsTool
                    news_tool = NewsTool()
                    # Use the raw query or extract keywords
                    news_query = query.replace("site:twitter.com", "").replace("site:reddit.com", "").strip()
                    news_results = news_tool.fetch_news(news_query)
                    for res in news_results:
                        res["query"] = news_query
                        results.append(res)
                
        return results
