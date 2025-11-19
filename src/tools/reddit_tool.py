import requests
import time
import random

class RedditTool:
    def __init__(self):
        # Rotate user agents to avoid strict rate limiting
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
        ]

    def fetch_subreddit_posts(self, subreddit, limit=5):
        """
        Fetches recent posts from a subreddit using the .json hack.
        """
        url = f"https://www.reddit.com/r/{subreddit}/new.json?limit={limit}"
        headers = {"User-Agent": random.choice(self.user_agents)}
        
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                posts = []
                for child in data.get("data", {}).get("children", []):
                    post = child.get("data", {})
                    posts.append({
                        "source": f"Reddit (r/{subreddit})",
                        "content": f"{post.get('title')} - {post.get('selftext')[:200]}...",
                        "url": f"https://reddit.com{post.get('permalink')}",
                        "timestamp": post.get("created_utc")
                    })
                return posts
            elif response.status_code == 429:
                return [{"source": "Reddit", "content": "Rate limited. Try again later.", "url": "", "timestamp": ""}]
            else:
                return []
        except Exception as e:
            print(f"Reddit Tool Error: {e}")
            return []
