from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.database import get_db
from app.services.recommendation import RecommendationEngine

router = APIRouter()

@router.get("/recommend/{article_id}", response_model=Dict[str, Any])
async def recommend(article_id: int, limit: int = 5, db: AsyncSession = Depends(get_db)):
    result = await RecommendationEngine.get_recommendations(db, article_id=article_id, limit=limit)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
