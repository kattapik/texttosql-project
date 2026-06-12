from typing import List
from sentence_transformers import SentenceTransformer
from app.domain.interfaces import IEmbeddingService

class EmbeddingService(IEmbeddingService):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> List[float]:
        return self.model.encode(text, normalize_embeddings=True).tolist()
