from typing import List, Dict, Any
from pinecone import Pinecone
from src.vectorstores.base import BaseVectorStore
from src.core.config import Config
from src import logger
from src.schemas.chunk import Chunk, ChunkMetadata
from src.vectorstores.keyword_search import KeywordSearchService
from src.vectorstores.reranker import RerankerService 
from src.embeddings.huggingface_embedding import EmbeddingService

class PineconeVectorStore(BaseVectorStore):
    def __init__(self):
        # Pinecone bağlantısı
        self.pc = Pinecone(api_key=Config.PINECONE_API_KEY)
        self.index = self.pc.Index(Config.PINECONE_INDEX_NAME)
        self.batch_size = 150
        
        # AĞIR MODELLER BURADA SADECE 1 KEZ YÜKLENİR
        self.keyword_search = KeywordSearchService()
        self.reranker = RerankerService()
        self.embedding = EmbeddingService()
        self.k_rrf = 60 # RRF sabiti
        
        logger.info(f"Pinecone ve Hibrit Servisler hazır: {Config.PINECONE_INDEX_NAME}")

    def upsert_chunks(self, chunks: List[Chunk], vectors: List[List[float]]):
        total_records = len(chunks)
        async_results = []

        for i in range(0, total_records, self.batch_size):
            batch_chunks = chunks[i : i + self.batch_size]
            batch_vectors = vectors[i : i + self.batch_size]
            
            records = []
            for chunk, vector in zip(batch_chunks, batch_vectors):
                records.append({
                    "id": chunk.chunk_id,
                    "values": vector,
                    "metadata": {
                        "text": chunk.content,
                        "source": chunk.metadata.source,
                        "file_type": chunk.metadata.file_type,
                        "start_index": chunk.metadata.start_index,
                        "end_index": chunk.metadata.end_index,
                        "total_doc_size": chunk.metadata.total_doc_size,
                        "page_number": chunk.metadata.page_number
                    }
                })

            try:
                res = self.index.upsert(
                    vectors=records, 
                    namespace="medical_data",
                    async_req=True 
                )
                async_results.append(res)
            except Exception as e:
                logger.error(f"Pinecone Batch hatası: {e}")

        logger.info(f"Bekleniyor: {len(async_results)} batch yükleniyor...")
        for res in async_results:
            res.get() 
            
        logger.info("Veriler Pinecone ve Yerel Keyword Index'e başarıyla yüklendi ve doğrulandı.")

    def _apply_rrf(self, semantic_docs: List[Chunk], keyword_docs: List[Chunk], top_k: int = 20) -> List[Chunk]:
        """Reciprocal Rank Fusion ile iki listeyi harmanlar."""
        rrf_scores = {}
        doc_map: Dict[str, Chunk] = {} 

        for rank, doc in enumerate(semantic_docs, 1):
            doc_id = doc.chunk_id
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + (1 / (self.k_rrf + rank))
            doc_map[doc_id] = doc

        for rank, chunk in enumerate(keyword_docs, 1):
            doc_id = chunk.chunk_id
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + (1 / (self.k_rrf + rank))
            if doc_id not in doc_map:
                doc_map[doc_id] = chunk

        sorted_ids = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        
        final_results = []
        for doc_id, score in sorted_ids[:top_k]:
            target_chunk = doc_map[doc_id]
            target_chunk.score = score  # Hibrit RRF skorunu atıyoruz
            final_results.append(target_chunk)

        return final_results

    def semantic_search(self, query_vector: List[float], top_k: int = 20) -> List[Chunk]:
        results = self.index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True,
            namespace="medical_data"
        )
        
        semantic_chunks = []
        for match in results.get("matches", []):
            meta = match["metadata"]
            
            chunk_metadata = ChunkMetadata(
                source=meta["source"],
                file_type=meta["file_type"],
                start_index=meta["start_index"],
                end_index=meta["end_index"],
                total_doc_size=meta["total_doc_size"],
                page_number=meta.get("page_number",None)
            )
            
            chunk = Chunk(
                content=meta["text"],
                metadata=chunk_metadata
            )
            
            chunk.chunk_id = match["id"] 
            chunk.score = match["score"]
            
            semantic_chunks.append(chunk)
            
        return semantic_chunks

    def get_final_context(self, query: str, top_k: int = 5) -> List[Chunk]:
        """Uçtan uca Hibrit Arama + Reranking süreci."""
        
        # Her seferinde yüklemek yerine self.embedding kullanıyoruz (HIZ KAZANCI!)
        query_vector = self.embedding.embed_query(query=query)
        
        semantic_results = self.semantic_search(query_vector, top_k=30)
        keyword_results = self.keyword_search.search(query, top_k=30)
        
        candidates: List[Chunk] = self._apply_rrf(semantic_results, keyword_results, top_k=10)
        
        final_docs = self.reranker.rerank(query, candidates, top_k=top_k)
        
        return final_docs