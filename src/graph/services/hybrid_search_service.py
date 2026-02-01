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
    query = state.get("query") # Query Optimizerda düzenlendi.
    index_name = Config.PINECONE_INDEX_NAME
    
    vectorstore = PineconeVectorStore(
        index_name=index_name, 
        embedding=embeddings
    )
    
    
    docs:List[Chunk] = vectorstore.get_final_context(query, k=5)
    
    
    logger.info(f"Retrieved {len(docs)} documents from Pinecone.")
    
    
    return {
        "retrieved_docs": docs 
    }