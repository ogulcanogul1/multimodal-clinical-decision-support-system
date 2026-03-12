from typing import List
from langchain_community.tools.tavily_search import TavilySearchResults
from src.graph.state import GraphState
from src.graph.enum.system_status import SystemStatus
from src.schemas.chunk import Chunk, ChunkMetadata
from src.vectorstores.reranker import RerankerService
from src import logger

reranker_service = RerankerService(model_name="BAAI/bge-reranker-v2-m3")

def web_research_service(state: GraphState):
    """
    Optimizer sorgularını sırayla aratır, sonuçları anında Reranker ile 
    puanlar ve sadece en iyi 3 chunk'ı döner.
    """
    logger.info("--- 🌐 WEB RESEARCH & RERANK STARTING ---")
    
    try:
        query = state.get("query") 
        opt_queries = state.get("optimized_queries", {})
        web_queries = opt_queries.get("web_search_queries", [])
        
        if not web_queries:
            logger.warning("No web queries found in state!")
            return {"status": SystemStatus.FAILED.value}

        search_tool = TavilySearchResults(k=2)
        MAX_CHAR_LIMIT = 5000 
        all_web_chunks = []

        # 1. Normal for döngüsü ile tüm web verilerini topla
        for q in web_queries:
            try:
                search_results = search_tool.invoke({"query": q})
                for res in search_results:
                    raw_content = res.get("content", "")
                    
                    if len(raw_content) > MAX_CHAR_LIMIT:
                        raw_content = raw_content[:MAX_CHAR_LIMIT] + "... [Truncated]"

                    meta = ChunkMetadata(
                        source=res.get("url", "unknown_url"),
                        file_type="web_page",
                        total_doc_size=len(raw_content),
                        start_index=0, 
                        end_index=len(raw_content),
                        page_number=None 
                    )
                    all_web_chunks.append(Chunk(content=raw_content, metadata=meta))
            except Exception as e:
                logger.error(f"❌ Sub-search error for '{q}': {e}")

        if not all_web_chunks:
            logger.warning("No web chunks retrieved.")
            return {"retrieved_docs": []}

        # 2. ENTEGRE RERANKER KATMANI
        logger.info(f"🎯 Reranking {len(all_web_chunks)} web chunks with BGE...")
        
        final_web_chunks = reranker_service.rerank(
            query=query, 
            documents=all_web_chunks, 
            top_k=3
        )

        logger.info(f"✅ Web research & Rerank complete. Selected top {len(final_web_chunks)} chunks.")
        
        return {"retrieved_docs": final_web_chunks, "status": SystemStatus.PROCESSING.value}
        
    except Exception as e:
        logger.critical(f"🛑 Critical failure in integrated Web-Rerank node: {e}")
        return {"retrieved_docs": [], "status": SystemStatus.PROCESSING.value}