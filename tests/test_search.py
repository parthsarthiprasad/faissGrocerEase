import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.embedding_service import EmbeddingService
from app.services.faiss_service import FaissService
import numpy as np

client = TestClient(app)

def test_search_endpoint():
    # Test data
    test_query = {
        "query": "lightweight waterproof hoodie",
        "lat": 12.9716,
        "lon": 77.5946,
        "radius_km": 10,
        "max_results": 10
    }
    
    # Make request
    response = client.post("/search", json=test_query)
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:  # If there are results
        assert all(isinstance(item, dict) for item in data)
        assert all("id" in item for item in data)
        assert all("name" in item for item in data)
        assert all("price" in item for item in data)
        assert all("category" in item for item in data)
        assert all("lat" in item for item in data)
        assert all("lon" in item for item in data)

def test_embedding_service():
    embedding_service = EmbeddingService()
    text = "test query"
    embedding = embedding_service.encode(text)
    
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (384,)  # all-MiniLM-L6-v2 dimension

def test_faiss_service():
    faiss_service = FaissService()
    test_vector = np.random.rand(384).astype('float32')
    results = faiss_service.search(test_vector, k=5)
    
    assert isinstance(results, list)
    assert len(results) <= 5 