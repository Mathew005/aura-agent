from src.tools.news_tool import NewsTool
import time

class RealIncidentFeed:
    def __init__(self):
        self.news_tool = NewsTool()
        self.cache = []
        self.last_fetch = 0
        self.fetch_interval = 300  # Fetch every 5 minutes
        self.queries = [
            "India disaster news breaking",
            "Mumbai fire update",
            "Delhi earthquake news",
            "Kerala flood warning",
            "Bangalore accident news",
            "cyclone warning India",
            "landslide Himachal Pradesh"
        ]
        self.current_index = 0

    def fetch_fresh_incidents(self):
        """Fetches new incidents from Google News RSS."""
        new_incidents = []
        for query in self.queries:
            results = self.news_tool.fetch_news(query, limit=5)
            for res in results:
                # Deduplicate based on title
                if not any(i['text'] == res['content'] for i in self.cache):
                    new_incidents.append({
                        "text": f"{res['content']} ({res['timestamp']})",
                        "source": "Google News RSS"
                    })
        
        # Add new unique incidents to cache
        self.cache.extend(new_incidents)
        self.last_fetch = time.time()
        return len(new_incidents)

    def get_next_incident(self):
        """Returns the next incident from the cache, fetching more if needed."""
        if time.time() - self.last_fetch > self.fetch_interval or not self.cache:
            self.fetch_fresh_incidents()
        
        if self.current_index < len(self.cache):
            incident = self.cache[self.current_index]
            self.current_index += 1
            return incident
        else:
            # Wrap around or fetch more? For now, wrap around if empty, but try to fetch.
            if self.fetch_fresh_incidents() == 0:
                 # If no new news, just return the last one or loop
                 if self.cache:
                     self.current_index = 0
                     return self.cache[0]
            return None
