from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import taskiq_fastapi

from app.database import init_db
from app.routers import search, recommendation
from app.worker import broker
import os

app = FastAPI(title="Deterministic News IR System")

# Ensure static directory exists
os.makedirs("app/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

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
    return FileResponse("app/static/index.html")
