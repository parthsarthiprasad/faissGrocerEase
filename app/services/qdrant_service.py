from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
from typing import List, Optional
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

class QdrantService:
    def __init__(self):
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL", "http://localhost:6333")
        )
        self.collection_name = "products"
        self.vector_size = 384  # Dimension of all-MiniLM-L6-v2 embeddings
        self._ensure_collection()

    def _ensure_collection(self):
        collections = self.client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )

    def add_vectors(
        self,
        ids: List[uuid.UUID],
        vectors: List[List[float]],
        payloads: List[dict]
    ):
        points = []
        for idx, (vector, payload) in enumerate(zip(vectors, payloads)):
            points.append(
                models.PointStruct(
                    id=idx,
                    vector=vector,
                    payload={
                        "product_id": str(ids[idx]),
                        **payload
                    }
                )
            )
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search(
        self,
        query_vector: List[float],
        k: int,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius_km: Optional[float] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        categories: Optional[List[str]] = None
    ) -> List[uuid.UUID]:
        # Build filter conditions
        filter_conditions = []
        
        if lat is not None and lon is not None and radius_km is not None:
            filter_conditions.append(
                models.FieldCondition(
                    key="location",
                    geo_radius=models.GeoRadius(
                        center=models.GeoPoint(
                            lat=lat,
                            lon=lon
                        ),
                        radius=radius_km * 1000  # Convert km to meters
                    )
                )
            )
        
        if min_price is not None:
            filter_conditions.append(
                models.FieldCondition(
                    key="price",
                    range=models.Range(
                        gte=min_price
                    )
                )
            )
        
        if max_price is not None:
            filter_conditions.append(
                models.FieldCondition(
                    key="price",
                    range=models.Range(
                        lte=max_price
                    )
                )
            )
        
        if categories:
            filter_conditions.append(
                models.FieldCondition(
                    key="category",
                    match=models.MatchAny(any=categories)
                )
            )
        
        # Combine all conditions
        filter_ = models.Filter(
            must=filter_conditions
        ) if filter_conditions else None
        
        # Perform search
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=k,
            query_filter=filter_
        )
        
        # Extract product IDs from results
        return [uuid.UUID(point.payload["product_id"]) for point in search_result] 