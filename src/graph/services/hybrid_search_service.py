import os
from src.vectorstores.pinecone_vectorstore import PineconeVectorStore
from src.graph.state import GraphState
from src.graph.enum.system_status import SystemStatus
from src import logger
from typing import List
from src.schemas.chunk import Chunk

def hybrid_search_service(state: GraphState):
    """
    Optimizer'dan gelen 'vector_store_query'yi kullanarak 
    Pinecone üzerinde Hybrid (Vector + Keyword) arama yapar.
    """
    logger.info("--- 📚 HYBRID SEARCH STARTING ---")
        
    opt_queries = state.get("optimized_queries", {})
    
    # 1. Aramayı yapacak olan sorguyu alıyoruz.
    # Optimizer bir şeyler ürettiyse onu kullan, yoksa doktorun yazdığı orjinal mesaja düş.
    vector_query = opt_queries.get("vector_store_query") or state.get("message_content") or state.get("query")
    
    if not vector_query:
        logger.warning("No valid query found for vector search.")
        return {"retrieved_docs": []}
        
    logger.info(f"🔎 Pinecone Query: {vector_query}")
    vectorstore = PineconeVectorStore()
    
    try:
        docs: List[Chunk] = vectorstore.get_final_context(vector_query, top_k=5)
        logger.info(f"✅ Retrieved {len(docs)} documents from Pinecone.")
        return {"retrieved_docs": docs}
    except Exception as e:
        logger.error(f"❌ Pinecone Search Error: {e}")
        return {"retrieved_docs": []}