from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import Product
from app.services.faiss_service import FaissService
from app.services.embedding_service import EmbeddingService
import numpy as np

def build_faiss_index():
    # Initialize services
    faiss_service = FaissService()
    embedding_service = EmbeddingService()
    
    # Get all products from database
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        
        if not products:
            print("No products found in database.")
            return
        
        # Prepare data for batch processing
        product_ids = []
        descriptions = []
        
        for product in products:
            product_ids.append(product.id)
            descriptions.append(product.description)
        
        # Encode descriptions in batch
        embeddings = embedding_service.encode_batch(descriptions)
        
        # Add vectors to FAISS index
        faiss_service.add_vectors(product_ids, embeddings)
        
        print(f"Successfully built FAISS index with {len(products)} products.")
    
    finally:
        db.close()

if __name__ == "__main__":
    build_faiss_index() 