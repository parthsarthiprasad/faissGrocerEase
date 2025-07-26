from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, desc, asc
from app.db.database import get_db
from app.services.qdrant_service import QdrantService
from app.services.embedding_service import EmbeddingService
from pydantic import BaseModel, confloat
from typing import List, Optional
import uuid

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    lat: float
    lon: float
    radius_km: float
    max_results: int
    min_price: Optional[confloat(ge=0)] = None
    max_price: Optional[confloat(ge=0)] = None
    categories: Optional[List[str]] = None
    sort_by: Optional[str] = None
    show_only_available: Optional[bool] = False

class ProductResponse(BaseModel):
    id: uuid.UUID
    name: str
    price: float
    category: str
    lat: float
    lon: float
    description: str

@router.post("/", response_model=List[ProductResponse])
async def search(
    request: SearchRequest,
    db: Session = Depends(get_db),
    qdrant_service: QdrantService = Depends(QdrantService),
    embedding_service: EmbeddingService = Depends(EmbeddingService)
):
    # Get query embedding
    query_embedding = embedding_service.encode(request.query)
    
    # Get similar products from Qdrant with all filters
    similar_product_ids = qdrant_service.search(
        query_vector=query_embedding.tolist(),
        k=request.max_results * 2,
        lat=request.lat,
        lon=request.lon,
        radius_km=request.radius_km,
        min_price=request.min_price,
        max_price=request.max_price,
        categories=request.categories
    )
    
    if not similar_product_ids:
        return []
    
    # Convert UUIDs to strings for SQL query
    product_ids_str = [str(pid) for pid in similar_product_ids]
    
    # Build the base query
    base_query = """
        SELECT id, name, price, category, 
               ST_Y(location::geometry) as lat, 
               ST_X(location::geometry) as lon,
               description
        FROM products
        WHERE id::text = ANY(:product_ids)
    """
    
    # Add availability filter if specified
    # Note: is_available column doesn't exist in current schema
    # if request.show_only_available:
    #     base_query += " AND is_available = true"
    
    # Add sorting
    if request.sort_by:
        if request.sort_by == "price_asc":
            base_query += " ORDER BY price ASC"
        elif request.sort_by == "price_desc":
            base_query += " ORDER BY price DESC"
        # Note: rating and created_at columns don't exist in current schema
        # elif request.sort_by == "rating":
        #     base_query += " ORDER BY rating DESC NULLS LAST"
        # elif request.sort_by == "newest":
        #     base_query += " ORDER BY created_at DESC"
    
    # Add limit
    base_query += " LIMIT :limit"
    
    # Prepare parameters
    params = {
        "product_ids": product_ids_str,
        "limit": request.max_results
    }
    
    # Execute query
    results = db.execute(text(base_query), params).fetchall()
    
    return [
        ProductResponse(
            id=row[0],
            name=row[1],
            price=row[2],
            category=row[3],
            lat=row[4],
            lon=row[5],
            description=row[6]
        )
        for row in results
    ] 