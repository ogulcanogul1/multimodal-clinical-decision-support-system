from sentence_transformers import CrossEncoder
from typing import List, Dict, Any
from src.schemas.chunk import Chunk
from src import logger

class RerankerService:
    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3"):
        # Cross-Encoder modelleri soruyu ve dökümanı birlikte işler
        self.model = CrossEncoder(model_name)
        logger.info(f"Reranker modeli yüklendi: {model_name}")

    def rerank(self, query: str, documents: List[Chunk], top_k: int = 3) -> List[Chunk]:
        """
        Gelen dökümanları sorguya göre yeniden puanlar ve sıralar.
        """
        # Modelin beklediği format: [[soru, döküman1], [soru, döküman2]...]
        pairs = [[query, doc.content] for doc in documents]
        
        # Puanları hesapla
        scores = self.model.predict(pairs)
        
        # Skorları dökümanlarla eşleştir
        for i, score in enumerate(scores):
            documents[i].reranker_score = float(score)
            
        # Skorlara göre büyükten küçüğe sırala
        reranked_docs = sorted(documents, key=lambda x: x.reranker_score, reverse=True)
        
        return reranked_docs[:top_k]