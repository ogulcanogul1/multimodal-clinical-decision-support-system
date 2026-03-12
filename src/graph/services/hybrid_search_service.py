import os
from src.vectorstores.pinecone_vectorstore import PineconeVectorStore
from src.embeddings.huggingface_embedding import EmbeddingService
from src.graph.state import GraphState
from src.graph.enum.system_status import SystemStatus
from src.core.config import Config
from src import logger
from typing import List
from src.schemas.chunk import Chunk

def hybrid_search_service(state: GraphState):
    """
    Optimizer'dan gelen 'vector_store_query'yi kullanarak 
    Pinecone üzerinde Hybrid (Vector + Keyword) arama yapar.
    """
    logger.info("--- HYBRID SEARCH STARTING ---")
    
    embeddings = EmbeddingService()
    
    # DÜZELTME: Sorguyu optimizer'ın ürettiği yerden alıyoruz
    opt_queries = state.get("optimized_queries", {})
    vector_query = opt_queries.get("vector_store_query", state.get("query"))
    
    index_name = Config.PINECONE_INDEX_NAME
    vectorstore = PineconeVectorStore()
    
    
    docs:List[Chunk] = vectorstore.get_final_context(vector_query, top_k=5)
    logger.info(f"Retrieved {len(docs)} documents from Pinecone.")
    
    
    return {"retrieved_docs": docs}