import json
import uuid
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.db.models import Base, Product
from app.services.faiss_service import FaissService
from app.services.embedding_service import EmbeddingService
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
import os

def init_db():
    Base.metadata.create_all(bind=engine)

def ingest_products(json_file: str):
    # Initialize services
    faiss_service = FaissService()
    embedding_service = EmbeddingService()
    
    # Read products from JSON file
    with open(json_file, 'r') as f:
        products = json.load(f)
    
    # Prepare data for batch processing
    product_ids = []
    descriptions = []
    db_products = []
    
    for product in products:
        product_id = uuid.uuid4()
        product_ids.append(product_id)
        descriptions.append(product['description'])
        
        # Create database product
        db_product = Product(
            id=product_id,
            name=product['name'],
            description=product['description'],
            price=product['price'],
            category=product['category'],
            location=from_shape(Point(product['lon'], product['lat']), srid=4326)
        )
        db_products.append(db_product)
    
    # Encode descriptions in batch
    embeddings = embedding_service.encode_batch(descriptions)
    
    # Add vectors to FAISS index
    faiss_service.add_vectors(product_ids, embeddings)
    
    # Add products to database
    db = SessionLocal()
    try:
        db.add_all(db_products)
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    # Initialize database
    init_db()
    
    # Ingest products
    json_file = os.path.join(os.path.dirname(__file__), '..', 'sample_data', 'products.json')
    ingest_products(json_file) 