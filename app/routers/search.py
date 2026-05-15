from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.database import get_db
from app.services.search import SearchEngine

router = APIRouter()

@router.get("/search", response_model=Dict[str, Any])
async def search(q: str, limit: int = 10, decay_rate: float = 0.1, db: AsyncSession = Depends(get_db)):
    return await SearchEngine.search_articles(db, query=q, decay_rate=decay_rate, limit=limit)
