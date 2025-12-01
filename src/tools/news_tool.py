import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote

class NewsTool:
    def __init__(self):
        # Global search
        self.base_url = "https://news.google.com/rss/search?q={}&hl=en-US&gl=US&ceid=US:en"

    def fetch_news(self, query, limit=3):
        """
        Fetches news headlines from Google News RSS.
        """
        encoded_query = quote(query)
        url = self.base_url.format(encoded_query)
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                items = root.findall(".//item")
                results = []
                
                for item in items[:limit]:
                    title = item.find("title").text
                    link = item.find("link").text
                    pub_date = item.find("pubDate").text
                    
                    results.append({
                        "source": "Google News",
                        "content": title,
                        "url": link,
                        "timestamp": pub_date
                    })
                return results
            else:
                return []
        except Exception as e:
            print(f"News Tool Error: {e}")
            return []
