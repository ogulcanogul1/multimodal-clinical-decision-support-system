import torch
from typing import List
from sentence_transformers import SentenceTransformer
from src.schemas.chunk import Chunk
from src import logger

class EmbeddingService:
    def __init__(self, model_name: str = "Alibaba-NLP/gte-Qwen2-1.5B-instruct"):
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        logger.info(f"Embedding modeli yükleniyor: {model_name} (Cihaz: {self.device})")
        
        try:
            # trust_remote_code=True, Qwen mimarisi için zorunludur.
            self.model = SentenceTransformer(
                model_name, 
                trust_remote_code=True, 
                device=self.device
            )
            self.dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"Model hazır. Boyut: {self.dimension}")
        except Exception as e:
            logger.error(f"Model yükleme hatası: {e}")
            raise

    def embed_chunks(self, chunks: List[Chunk]) -> List[List[float]]:
        """Chunk listesini alır ve 1024 boyutlu vektörlerini döner."""
        if not chunks:
            return []
            
        texts = [chunk.content for chunk in chunks]
        embeddings = self.model.encode(
            texts, 
            batch_size=16, 
            show_progress_bar=True,
            normalize_embeddings=True 
        )
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """Kullanıcının sorusunu arama için vektöre çevirir."""
        # Not: Instruction-based modellerde sorgu başına küçük bir 'prompt' eklemek kaliteyi artırır.
        full_query = f"Sorgu: {query}"
        embedding = self.model.encode(full_query, normalize_embeddings=True)
        return embedding.tolist()