import taskiq_fastapi
from taskiq_redis import ListQueueBroker
from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
import os

from app.services.ingestion import fetch_and_ingest_feed

# Define the Redis broker
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
broker = ListQueueBroker(url=REDIS_URL)

# Define the scheduler
scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)

# Example feeds to poll
FEEDS = [
    {"url": "http://feeds.bbci.co.uk/news/world/rss.xml", "category": "world"},
    {"url": "https://feeds.npr.org/1001/rss.xml", "category": "general"},
]

@broker.task(schedule=[{"cron": "*/15 * * * *"}])
async def poll_rss_feeds():
    for feed in FEEDS:
        await fetch_and_ingest_feed(feed["url"], feed["category"])

# We'll initialize taskiq_fastapi in main.py to avoid circular imports.
