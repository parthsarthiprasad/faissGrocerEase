from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://34.42.51.177:3000", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/search", tags=["search"])

@app.get("/")
async def root():
    return {"message": "Inventory Search Engine API"} 