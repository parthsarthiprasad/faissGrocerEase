from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def encode(self, text: str) -> np.ndarray:
        return self.model.encode(text)
    
    def encode_batch(self, texts: list) -> np.ndarray:
        return self.model.encode(texts) 