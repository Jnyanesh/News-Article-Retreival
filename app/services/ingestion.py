import feedparser
import hashlib
from datetime import datetime
from email.utils import parsedate_to_datetime
import logging
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError

from app.database import async_session
from app.models import Article
from app.utils.text_processing import clean_html

logger = logging.getLogger(__name__)

async def fetch_and_ingest_feed(feed_url: str, category: str):
    logger.info(f"Fetching feed: {feed_url}")
    # Using feedparser asynchronously is not natively supported, but it's IO-bound, 
    # we can run it in a thread if needed, or just use it directly for this example.
    feed = feedparser.parse(feed_url)
    
    articles_to_insert = []
    
    for entry in feed.entries:
        title = entry.get('title', '')
        link = entry.get('link', '')
        # SHA-256 for strict deduplication
        url_hash = hashlib.sha256(link.encode('utf-8')).hexdigest()
        
        # summary or content
        body_raw = ''
        if 'content' in entry:
            body_raw = entry.content[0].value
        elif 'summary' in entry:
            body_raw = entry.summary
            
        body = clean_html(body_raw)
        
        # Handle pubDate
        # Ensure it is timezone-aware
        published_at = None
        if 'published' in entry:
            try:
                published_at = parsedate_to_datetime(entry.published)
            except Exception:
                pass
        
        if not published_at:
            published_at = datetime.utcnow()
            
        source = feed.feed.get('title', feed_url)
        
        articles_to_insert.append({
            'title': title,
            'body': body,
            'source': source,
            'url': link,
            'url_hash': url_hash,
            'published_at': published_at,
            'category': category
        })
        
    if not articles_to_insert:
        return
        
    async with async_session() as session:
        try:
            # Use PostgreSQL INSERT ... ON CONFLICT DO NOTHING for deduplication
            stmt = insert(Article).values(articles_to_insert)
            stmt = stmt.on_conflict_do_nothing(index_elements=['url_hash'])
            
            await session.execute(stmt)
            await session.commit()
            logger.info(f"Ingested {len(articles_to_insert)} articles from {feed_url}")
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Error ingesting feed {feed_url}: {e}")
