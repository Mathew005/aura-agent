from src.tools.reddit_tool import RedditTool

def test_reddit():
    tool = RedditTool()
    print("Fetching posts from r/news...")
    posts = tool.fetch_subreddit_posts("news", limit=3)
    
    if posts:
        print(f"Successfully fetched {len(posts)} posts.")
        for post in posts:
            print(f"- {post['content'][:50]}...")
    else:
        print("Failed to fetch posts.")

if __name__ == "__main__":
    test_reddit()
