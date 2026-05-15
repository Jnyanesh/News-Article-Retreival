from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import time
from typing import Dict, Any

class RecommendationEngine:
    @staticmethod
    async def get_recommendations(session: AsyncSession, article_id: int, limit: int = 5) -> Dict[str, Any]:
        
        # First, ensure article exists and get category
        sql_article = text("SELECT category FROM articles WHERE id = :id")
        result = await session.execute(sql_article, {"id": article_id})
        article = result.fetchone()
        
        if not article:
            return {"error": "Article not found"}
            
        category = article.category
        
        # Extract top 5 frequent words from the article's tsvector
        sql_keywords = text(f"""
            SELECT word 
            FROM ts_stat('SELECT search_vector FROM articles WHERE id = {int(article_id)}')
            ORDER BY nentry DESC
            LIMIT 5;
        """)
        
        kw_result = await session.execute(sql_keywords)
        keywords = [row.word for row in kw_result.fetchall()]
        
        if not keywords:
            return {"article_id": article_id, "keywords_used": [], "recommendations": []}
            
        # Join words with OR operator
        # Make sure words don't contain special tsquery characters or handle them
        clean_keywords = [w.replace("'", "") for w in keywords]
        query_str = " | ".join(clean_keywords)
        
        # Search for similar articles using these keywords
        sql_search = text("""
            SELECT 
                id, 
                title, 
                source, 
                url, 
                published_at,
                category,
                ts_rank_cd(search_vector, to_tsquery('english', :query)) AS rank
            FROM articles
            WHERE category = :category 
              AND id != :id
              AND search_vector @@ to_tsquery('english', :query)
            ORDER BY rank DESC
            LIMIT :limit;
        """)
        
        start_time = time.time()
        rec_result = await session.execute(sql_search, {
            "query": query_str, 
            "category": category, 
            "id": article_id, 
            "limit": limit
        })
        
        rows = rec_result.fetchall()
        latency_ms = (time.time() - start_time) * 1000
        
        recommendations = [
            {
                "id": row.id,
                "title": row.title,
                "source": row.source,
                "url": row.url,
                "published_at": row.published_at.isoformat() if row.published_at else None,
                "category": row.category,
                "rank": float(row.rank)
            }
            for row in rows
        ]
        
        return {
            "article_id": article_id,
            "keywords_used": keywords,
            "latency_ms": round(latency_ms, 2),
            "recommendations": recommendations
        }
