from fastapi import FastAPI
from app.routers import search
from app.db.database import engine
from app.db.models import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Inventory Search Engine",
    description="A semantic search engine for inventory with geolocation filtering",
    version="1.0.0"
)

app.include_router(search.router, prefix="/search", tags=["search"])

@app.get("/")
async def root():
    return {"message": "Inventory Search Engine API"} 