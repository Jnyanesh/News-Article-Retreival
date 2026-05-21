import asyncio
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ingestion import fetch_and_ingest_feed

UNIVERSAL_FEEDS = [
    {"url": "http://feeds.bbci.co.uk/news/world/rss.xml", "category": "world"},
    {"url": "http://feeds.bbci.co.uk/news/technology/rss.xml", "category": "tech"},
    {"url": "http://feeds.bbci.co.uk/news/business/rss.xml", "category": "business"},
    {"url": "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml", "category": "science"},
    {"url": "http://feeds.bbci.co.uk/news/health/rss.xml", "category": "health"},
    {"url": "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml", "category": "entertainment"},
    {"url": "https://feeds.npr.org/1001/rss.xml", "category": "general"},
    {"url": "https://feeds.npr.org/1019/rss.xml", "category": "tech"},
    {"url": "https://feeds.npr.org/1006/rss.xml", "category": "business"},
    {"url": "https://feeds.npr.org/1004/rss.xml", "category": "world"},
]

async def seed_real_data():
    print("Fetching REAL news articles to expand the vocabulary...")
    for feed in UNIVERSAL_FEEDS:
        try:
            await fetch_and_ingest_feed(feed["url"], feed["category"])
        except Exception as e:
            print(f"Failed to fetch {feed['url']}: {e}")
    print("Done fetching real news!")

if __name__ == "__main__":
    asyncio.run(seed_real_data())
