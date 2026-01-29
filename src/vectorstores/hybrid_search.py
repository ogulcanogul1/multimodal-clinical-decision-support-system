from typing import List, Dict, Any
from src.vectorstores.pinecone_vectorstore import PineconeVectorStore
from src.vectorstores.keyword_search import KeywordSearchService
from src import logger

class HybridSearchManager:
    def __init__(self):
        self.semantic_store = PineconeVectorStore() 
        self.keyword_service = KeywordSearchService()
        self.k = 60 

    def search(self, query_text: str, query_vector: List[float], top_k: int = 5):
        
        semantic_results = self.semantic_store.search(query_vector, top_k=top_k * 2)
        keyword_results = self.keyword_service.search(query_text, top_k=top_k * 2)

        rrf_scores = {}

        # Semantic search results
        for rank, match in enumerate(semantic_results.get('matches', []), 1):
            doc_id = match['id']
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + (1 / (self.k + rank))

        # Keyword search results
        for rank, chunk in enumerate(keyword_results, 1):
            doc_id = chunk.chunk_id
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + (1 / (self.k + rank))

        
        sorted_ids = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        
        return sorted_ids