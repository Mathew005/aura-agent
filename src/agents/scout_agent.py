import google.generativeai as genai
import time
import json
from src.config import GOOGLE_API_KEY, GEMINI_MODEL_NAME
from src.prompts import SCOUT_PROMPT
from src.utils.rate_limiter import handle_rate_limit

class ScoutAgent:
    """
    The Scout Agent is responsible for gathering external intelligence to corroborate reports.
    
    Key Capabilities:
    - Strategy Generation: Uses LLM to formulate effective search queries based on incident context.
    - Information Retrieval: Executes searches using Google Search (via Gemini Grounding) to find real-time updates.
    - Recency Filtering: Enforces checks to ensure data is current (ignoring old news).
    """
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
        
        for attempt in range(3):
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
                if handle_rate_limit(e):
                    continue
                print(f"Scout Strategy Error: {e}")
                return [f"{incident_context} updates", f"site:twitter.com {incident_context}"]

    def fetch_updates(self, queries, mock_mode=True):
        """
        Executes the search queries. 
        If mock_mode is True, generates simulated 'real-time' social media snippets.
        If mock_mode is False, uses Gemini with Google Search Grounding.
        """
        results = []
        
        # Check for google.genai (V2 SDK) availability
        try:
            import google.genai
            genai_search_available = True
        except ImportError:
            genai_search_available = False
            print("Warning: google.genai not found. Search capabilities limited.")
        
        # Lazy import for Reddit
        from src.tools.reddit_tool import RedditTool
        reddit_tool = RedditTool()
        
        for query in queries:
            # Simulate "Thinking/Searching" time
            time.sleep(0.3)
            
            if mock_mode:
                # ... (Mock logic) ...
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
                # Real Data Integration
                
                if query.startswith("r/"):
                    # Specific Subreddit Targeting
                    subreddit = query.split(" ")[0].replace("r/", "")
                    posts = reddit_tool.fetch_subreddit_posts(subreddit)
                    for post in posts:
                        post["query"] = query
                        results.append(post)
                else:
                    # Broad Web Search using Gemini Grounding (V2 SDK)
                    if genai_search_available:
                        try:
                            # Use google.genai (V2 SDK) which supports google_search tool
                            from google import genai
                            from google.genai import types
                            
                            client = genai.Client(api_key=GOOGLE_API_KEY)
                            
                            # We ask Gemini to summarize the search results for the query
                            # We ask Gemini to summarize the search results for the query
                            search_prompt = f"Search for the LATEST updates on: {query}. Ignore any news older than 24 hours. Summarize the key facts found and explicitly state if the event is happening NOW."
                            
                            # Retry loop for search
                            for attempt in range(3):
                                try:
                                    response = client.models.generate_content(
                                        model=GEMINI_MODEL_NAME,
                                        contents=search_prompt,
                                        config=types.GenerateContentConfig(
                                            tools=[types.Tool(google_search=types.GoogleSearch())]
                                        )
                                    )
                                    
                                    # Extract content
                                    content = response.text.strip() if response.text else "No content generated."
                                    
                                    # Extract sources from grounding metadata if available
                                    citations = []
                                    # V2 SDK structure for grounding metadata
                                    if response.candidates and response.candidates[0].grounding_metadata:
                                        gm = response.candidates[0].grounding_metadata
                                        if hasattr(gm, 'grounding_chunks') and gm.grounding_chunks:
                                            for chunk in gm.grounding_chunks:
                                                if chunk.web:
                                                    citations.append({
                                                        "title": chunk.web.title,
                                                        "url": chunk.web.uri
                                                    })
                                    
                                    source_label = "Google Search"
                                    if citations:
                                        titles = [c['title'] for c in citations if c.get('title')]
                                        source_label += f" ({', '.join(titles[:2])})"
                                    
                                    results.append({
                                        "source": source_label,
                                        "citations": citations,
                                        "query": query,
                                        "content": content,
                                        "timestamp": "Just now"
                                    })
                                    break # Success, exit retry loop
                                    
                                except Exception as e:
                                    if handle_rate_limit(e):
                                        continue
                                    print(f"Gemini V2 Search Error: {e}")
                                    results.append({
                                        "source": "System",
                                        "query": query,
                                        "content": f"Failed to search: {e}",
                                        "timestamp": "Just now"
                                    })
                                    break
                            
                        except Exception as e:
                            print(f"Gemini V2 Search Error: {e}")
                            results.append({
                                "source": "System",
                                "query": query,
                                "content": f"Failed to search: {e}",
                                "timestamp": "Just now"
                            })
                    else:
                        # Fallback to NewsTool if Gemini Search is not available
                        from src.tools.news_tool import NewsTool
                        news_tool = NewsTool()
                        news_query = query.replace("site:twitter.com", "").replace("site:reddit.com", "").strip()
                        news_results = news_tool.fetch_news(news_query)
                        for res in news_results:
                            res["query"] = news_query
                            results.append(res)
                
        return results
