from sentence_transformers import CrossEncoder
from typing import List, Dict, Any
from src import logger

class RerankerService:
    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3"):
        # Cross-Encoder modelleri soruyu ve dökümanı birlikte işler
        self.model = CrossEncoder(model_name)
        logger.info(f"Reranker modeli yüklendi: {model_name}")

    def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = 3):
        """
        Gelen dökümanları sorguya göre yeniden puanlar ve sıralar.
        """
        # Modelin beklediği format: [[soru, döküman1], [soru, döküman2]...]
        pairs = [[query, doc['text']] for doc in documents]
        
        # Puanları hesapla
        scores = self.model.predict(pairs)
        
        # Skorları dökümanlarla eşleştir
        for i, score in enumerate(scores):
            documents[i]['rerank_score'] = float(score)
            
        # Skorlara göre büyükten küçüğe sırala
        reranked_docs = sorted(documents, key=lambda x: x['rerank_score'], reverse=True)
        
        return reranked_docs[:top_k]