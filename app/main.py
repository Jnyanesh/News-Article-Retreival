from fastapi import FastAPI
import taskiq_fastapi

from app.database import init_db
from app.routers import search, recommendation
from app.worker import broker

app = FastAPI(title="Deterministic News IR System")

# Include routers
app.include_router(search.router)
app.include_router(recommendation.router)

# Initialize TaskIQ inside FastAPI app
taskiq_fastapi.init(broker, "app.main:app")

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/")
async def root():
    return {"message": "News Article Retrieval System API is running."}
