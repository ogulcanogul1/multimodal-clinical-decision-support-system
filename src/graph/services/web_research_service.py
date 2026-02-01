import asyncio
from typing import List
from langchain_community.tools.tavily_search import TavilySearchResults
from src.graph.state import GraphState
from src.graph.enum.system_status import SystemStatus
from src.schemas.node_schemas.rag_schemas import Chunk, ChunkMetadata
from src.vectorstores.reranker import RerankerService # Senin servisin
from src import logger

# Servisi fonksiyon dışında bir kez ilklendirebilirsin (Singleton mantığı)
reranker_service = RerankerService(model_name="BAAI/bge-reranker-v2-m3")

async def web_research_service(state: GraphState):
    """
    Optimizer sorgularını paralel aratır, sonuçları anında Reranker ile 
    puanlar ve sadece en iyi 3 chunk'ı döner.
    """
    logger.info("--- 🌐 WEB RESEARCH & RERANK STARTING (ASYNC) ---")
    
    try:
        query = state.get("query") # Rerank için asıl soru lazım
        web_queries = state.get("web_search_queries", [])
        
        if not web_queries:
            logger.warning("No web queries found in state!")
            return {"status": SystemStatus.FAILED.value}

        search_tool = TavilySearchResults(k=2)
        MAX_CHAR_LIMIT = 5000 

        async def perform_search(q: str) -> List[Chunk]:
            try:
                search_results = await asyncio.to_thread(search_tool.invoke, {"query": q})
                chunks = []
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
                    chunks.append(Chunk(content=raw_content, metadata=meta))
                return chunks
            except Exception as e:
                logger.error(f"❌ Sub-search error for '{q}': {e}")
                return []

        # 1. Paralel olarak tüm web verilerini topla
        tasks = [perform_search(q) for q in web_queries]
        results = await asyncio.gather(*tasks)
        all_web_chunks = [chunk for sublist in results for chunk in sublist]

        if not all_web_chunks:
            logger.warning("No web chunks retrieved.")
            return {"retrieved_docs": []}

        # 2. ENTEGRE RERANKER KATMANI
        # State'e yazmadan önce senin RerankerService'i burada çalıştırıyoruz
        logger.info(f"🎯 Reranking {len(all_web_chunks)} web chunks with BGE...")
        
        # Senin rerank metodun top_k=3 döküman dönecek şekilde kurgulanmış
        final_web_chunks = reranker_service.rerank(
            query=query, 
            documents=all_web_chunks, 
            top_k=3
        )

        logger.info(f"✅ Web research & Rerank complete. Selected top {len(final_web_chunks)} chunks.")
        
        # Sadece seçilen en iyi 3 dökümanı state'e gönderiyoruz
        return {
            "retrieved_docs": final_web_chunks,
            "status": SystemStatus.PROCESSING.value
        }

    except Exception as e:
        logger.critical(f"🛑 Critical failure in integrated Web-Rerank node: {e}")
        return {"retrieved_docs": [], "status": SystemStatus.PROCESSING.value}