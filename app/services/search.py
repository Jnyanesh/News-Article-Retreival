from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import time
import urllib.parse
from app.services.ingestion import fetch_and_ingest_feed

class SearchEngine:
    @staticmethod
    async def search_articles(session: AsyncSession, query: str, decay_rate: float = 0.1, limit: int = 10):
        if query.strip():
            # Dynamically fetch from Google News RSS before searching the DB
            encoded_query = urllib.parse.quote(query.strip())
            rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
            try:
                await fetch_and_ingest_feed(rss_url, "universal")
            except Exception as e:
                print(f"Failed to fetch external news for {query}: {e}")

        # We need to construct a tsquery from the query string.
        # Postgres websearch_to_tsquery provides a good way to parse user input into a tsquery
        # Process the query to default to OR matching rather than strict AND
        # This solves the issue where "world news" requires both words in the same article.
        processed_query = " OR ".join([term for term in query.split() if term.strip()])
        if not processed_query:
            processed_query = query
        
        sql = text("""
            SELECT 
                id, 
                title, 
                source, 
                url, 
                published_at,
                category,
                ts_rank_cd(search_vector, websearch_to_tsquery('english', :query)) AS rank,
                (ts_rank_cd(search_vector, websearch_to_tsquery('english', :query)) * 
                 EXP(CAST(:decay_rate AS FLOAT) * -1 * extract(epoch from (now() - published_at))/86400)) AS final_score
            FROM articles
            WHERE search_vector @@ websearch_to_tsquery('english', :query)
            ORDER BY final_score DESC
            LIMIT :limit;
        """)
        
        start_time = time.time()
        result = await session.execute(sql, {"query": processed_query, "decay_rate": decay_rate, "limit": limit})
        rows = result.fetchall()
        latency_ms = (time.time() - start_time) * 1000
        
        articles = [
            {
                "id": row.id,
                "title": row.title,
                "source": row.source,
                "url": row.url,
                "published_at": row.published_at.isoformat() if row.published_at else None,
                "category": row.category,
                "rank": float(row.rank),
                "final_score": float(row.final_score)
            }
            for row in rows
        ]
        
        return {
            "query": query,
            "latency_ms": round(latency_ms, 2),
            "results": articles
        }
