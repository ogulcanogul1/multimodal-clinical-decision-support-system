import concurrent.futures
import json
from typing import List

from langchain_tavily import TavilySearch
from src.graph.state import GraphState
from src.graph.enum.system_status import SystemStatus
from src.schemas.chunk import Chunk, ChunkMetadata
from src.vectorstores.reranker import RerankerService
from src import logger

# AĞIR MODEL GLOBALDE (Sunucu başlarken 1 kez yüklenir)
try:
    reranker_service = RerankerService(model_name="BAAI/bge-reranker-v2-m3")
except Exception as e:
    logger.error(f"Reranker başlatılamadı: {e}")
    reranker_service = None

# ==========================================
# ⚡ HIZ VE KALİTE OPTİMİZASYONU (TAVILY)
# ==========================================
# max_results: Her sorgu için 2 sayfa getirir.
# search_depth="basic": Alt sayfalara dalıp saniyelerce beklemez, anında metni çeker.
# include_domains: Sadece dünyanın en güvenilir tıp otoritelerinde arama yapar.
search_tool = TavilySearch(
    max_results=2,
    search_depth="basic",
    include_domains=[
        "ncbi.nlm.nih.gov",       # PubMed / NIH
        "mayoclinic.org",         # Mayo Clinic
        "clevelandclinic.org",    # Cleveland Clinic
        "hopkinsmedicine.org",    # Johns Hopkins
        "medscape.com",           # Medscape
        "nature.com",             # Nature Medicine
        "thelancet.com"           # The Lancet
    ]
)

def web_research_service(state: GraphState):
    """
    Optimizer sorgularını PARALEL olarak aratır, sonuçları anında Reranker ile 
    puanlar ve sadece en iyi 3 chunk'ı döner.
    """
    print('*' * 50)
    logger.info("--- 🌐 WEB RESEARCH & RERANK STARTING ---")
    
    try:
        original_query = state.get("message_content") or state.get("query") or ""
        opt_queries = state.get("optimized_queries", {})
        web_queries = opt_queries.get("web_search_queries", [])
        
        rerank_context = opt_queries.get("vector_store_query") or original_query
        
        if not web_queries:
            logger.warning("No web queries found in state!")
            return {"status": SystemStatus.FAILED.value}

        MAX_CHAR_LIMIT = 5000 
        all_web_chunks = []

        # ==========================================
        # 🚀 PARALEL ARAMA (THREAD POOL)
        # ==========================================
        def fetch_tavily(query: str):
            """Tekil arama fonksiyonu (Thread'ler bunu çalıştıracak)"""
            logger.info(f"🌐 Searching Web: {query}")
            try:
                result = search_tool.invoke({"query": query})
                
                # ZIRH 1: Eğer Tavily listesi yerine JSON String dönerse, onu Python listesine çevir
                if isinstance(result, str):
                    try:
                        result = json.loads(result)
                    except json.JSONDecodeError:
                        return []
                        
                # 🛡️ ZIRH 2: Eğer Dictionary dönerse içindeki "results" listesini çek!
                if isinstance(result, dict) and "results" in result:
                    result = result["results"]
                        
                # Sadece geçerli bir liste ise döndür
                return result if isinstance(result, list) else []
                
            except Exception as e:
                logger.error(f"❌ Sub-search error for '{query}': {e}")
                return []

        # Tüm web sorgularını aynı anda (milisaniyeler içinde) fırlatır!
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(web_queries)) as executor:
            parallel_results = list(executor.map(fetch_tavily, web_queries))

        # Gelen verileri Chunk objesine çevirme
        for search_results in parallel_results:
            for res in search_results:
                # API yapısına göre metin genelde "content" anahtarında olur
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

        if not all_web_chunks:
            logger.warning("No web chunks retrieved.")
            return {"retrieved_docs": []}

        # ==========================================
        # 🎯 ENTEGRE RERANKER KATMANI
        # ==========================================
        if not reranker_service:
            logger.error("Reranker modeli yüklü değil!")
            return {"retrieved_docs": []}

        logger.info(f"🎯 Reranking {len(all_web_chunks)} web chunks with BGE...")
        
        final_web_chunks = reranker_service.rerank(
            query=rerank_context,
            documents=all_web_chunks, 
            top_k=3
        )

        logger.info(f"✅ Web research & Rerank complete. Selected top {len(final_web_chunks)} chunks.")
        
        return {"retrieved_docs": final_web_chunks, "status": SystemStatus.PROCESSING.value}
        
    except Exception as e:
        logger.critical(f"🛑 Critical failure in integrated Web-Rerank node: {e}")
        return {"retrieved_docs": [], "status": SystemStatus.PROCESSING.value}