import os
import requests

class GoogleSearchTool:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.cx = os.getenv("GOOGLE_SEARCH_CX")

    def search(self, query, limit=3):
        """
        Performs a Google Search using the Custom Search JSON API.
        """
        if not self.api_key or not self.cx:
            return [{
                "source": "System",
                "content": "Google Search API Key or CX not configured.",
                "url": "",
                "timestamp": ""
            }]

        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.api_key,
            "cx": self.cx,
            "q": query,
            "num": limit
        }

        try:
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                results = []
                for item in data.get("items", []):
                    results.append({
                        "source": "Google Search",
                        "content": f"{item.get('title')}: {item.get('snippet')}",
                        "url": item.get("link"),
                        "timestamp": "" # Google Search doesn't always provide a clear timestamp
                    })
                return results
            else:
                return [{
                    "source": "System",
                    "content": f"Search Error: {response.status_code}",
                    "url": "",
                    "timestamp": ""
                }]
        except Exception as e:
            print(f"Google Search Tool Error: {e}")
            return []
