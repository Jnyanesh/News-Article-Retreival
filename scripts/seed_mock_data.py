import asyncio
import sys
import os
import hashlib
from datetime import datetime, timedelta
import random

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.dialects.postgresql import insert
from app.models import Article, Base
from app.database import init_db

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://news_user:news_password@localhost:5432/news_db")
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

WORDS = ["election", "economy", "market", "technology", "ai", "sports", "championship", 
         "health", "vaccine", "global", "warming", "climate", "policy", "government"]
CATEGORIES = ["world", "politics", "business", "tech", "health", "sports"]
SOURCES = ["CNN", "BBC", "Reuters", "AP", "Bloomberg"]

async def seed_data(count=10000):
    await init_db()
    
    print(f"Seeding {count} articles...")
    batch_size = 1000
    
    async with async_session() as session:
        for i in range(0, count, batch_size):
            articles = []
            for j in range(batch_size):
                title_words = random.sample(WORDS, 3)
                body_words = random.sample(WORDS, 7) * 5
                
                title = " ".join(title_words).title() + f" {i+j}"
                body = " ".join(body_words) + f" details about {title}"
                category = random.choice(CATEGORIES)
                source = random.choice(SOURCES)
                url = f"https://mocknews.com/{category}/{i+j}"
                url_hash = hashlib.sha256(url.encode('utf-8')).hexdigest()
                
                # Random time within the last 30 days
                days_ago = random.randint(0, 30)
                published_at = datetime.utcnow() - timedelta(days=days_ago)
                
                articles.append({
                    "title": title,
                    "body": body,
                    "source": source,
                    "url": url,
                    "url_hash": url_hash,
                    "published_at": published_at,
                    "category": category
                })
            
            stmt = insert(Article).values(articles)
            stmt = stmt.on_conflict_do_nothing(index_elements=['url_hash'])
            await session.execute(stmt)
            await session.commit()
            print(f"Inserted {i + batch_size} articles.")

if __name__ == "__main__":
    asyncio.run(seed_data())
