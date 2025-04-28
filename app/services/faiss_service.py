import faiss
import numpy as np
import os
from typing import List
import uuid
from dotenv import load_dotenv

load_dotenv()

class FaissService:
    def __init__(self):
        self.index_path = os.getenv('FAISS_INDEX_PATH')
        self.dimension = 384  # Dimension of all-MiniLM-L6-v2 embeddings
        self.index = None
        self.load_index()

    def load_index(self):
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            faiss.write_index(self.index, self.index_path)

    def add_vectors(self, ids: List[uuid.UUID], vectors: np.ndarray):
        if not self.index:
            self.load_index()
        
        # Convert UUIDs to integers for FAISS
        id_map = {i: str(pid) for i, pid in enumerate(ids)}
        
        # Add vectors to index
        self.index.add(vectors)
        
        # Save index
        faiss.write_index(self.index, self.index_path)
        
        return id_map

    def search(self, query_vector: np.ndarray, k: int) -> List[uuid.UUID]:
        if not self.index:
            self.load_index()
        
        # Search for similar vectors
        distances, indices = self.index.search(query_vector.reshape(1, -1), k)
        
        # Convert indices back to UUIDs
        # Note: In a real implementation, you'd need to maintain a mapping
        # between FAISS indices and your UUIDs
        return [uuid.UUID(int=idx) for idx in indices[0] if idx != -1] 