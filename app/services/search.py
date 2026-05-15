from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import time

class SearchEngine:
    @staticmethod
    async def search_articles(session: AsyncSession, query: str, decay_rate: float = 0.1, limit: int = 10):
        # We need to construct a tsquery from the query string.
        # Postgres websearch_to_tsquery provides a good way to parse user input into a tsquery
        
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
                 EXP(-:decay_rate * extract(epoch from (now() - published_at))/86400)) AS final_score
            FROM articles
            WHERE search_vector @@ websearch_to_tsquery('english', :query)
            ORDER BY final_score DESC
            LIMIT :limit;
        """)
        
        start_time = time.time()
        result = await session.execute(sql, {"query": query, "decay_rate": decay_rate, "limit": limit})
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
