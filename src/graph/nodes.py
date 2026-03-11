from src.graph.state import GraphState
from src.graph.services.parser_service import parser_service 
from src.graph.services.query_optimizer_service import query_optimizer_service
from src.graph.services.hybrid_search_service import hybrid_search_service
from src.graph.services.web_research_service import web_research_service
from src.graph.services.retrieval_grader import retrieval_grader_service
from src.graph.services.image_gatekeeper_service import image_gatekeeper_service
from src.graph.services.mlp_control_service import mlp_control_service
from src.graph.services.lab_analyzer_service import lab_analyzer_service
from src.graph.services.image_analyzer_service import image_analyzer_service
from src.graph.services.adaptive_fusion_service import adaptive_fusion_service
from src.graph.services.diagnostic_agent_service import diagnostic_agent_service
from src.graph.services.self_critique_service import self_critique_service
from src.graph.services.conflict_resolver_service import conflict_resolver_service
from src.graph.services.extract_pdf_service import document_loader_service 


from src import logger
from src.schemas.chunk import Chunk
from typing import List

# --- ENTRY & ROUTING ---
def input_parser_node(state: GraphState):
    """Girişi ayrıştırır ve başlangıç state'ini kurar."""
    return parser_service(state=state)
    

# --- RESEARCH INTELLIGENCE (RAG LOOP) ---
def query_optimizer_node(state: GraphState):
    """Sorguyu yerel ve web araması için optimize eder."""
    return query_optimizer_service(state=state)
    

def hybrid_search_node(state: GraphState):
    """Pinecone 1536d + BM25 + Reranker işlemini yapar."""
    return hybrid_search_service(state=state)

def web_research_node(state: GraphState):
    """Tavily üzerinden akademik tıbbi tarama yapar."""
    return web_research_service(state=state)

def knowledge_synthesis_node(state: GraphState):
    """Arama sonuçlarını sentezler ve kaynakları etiketler."""
    logger.info("--- KNOWLEDGE SYNTHESIS: ASSIGNING CITATION IDS ---")
    
    all_docs:List[Chunk] = state.get("retrieved_docs", [])
    
    if not all_docs:
        return {"retrieved_docs": []}

    for i, doc in enumerate(all_docs):
        doc.metadata.citation_id = f"Ref-{i+1}"
        
        prefix = f"[[SOURCE ID: {doc.metadata.citation_id}]] | SOURCE: {doc.metadata.source}\n"
        if not doc.content.startswith("[[SOURCE ID:"):
            doc.content = prefix + doc.content

    logger.info(f"Assigned Citation IDs to {len(all_docs)} documents.")

    return {"retrieved_docs": all_docs}

def retrieval_grader_node(state: GraphState):
    """Arama kalitesini puanlar (Retry mi yoksa Fusion mı?)."""
    return retrieval_grader_service(state=state)

# --- VISION & ANALYTICS (GATEKEEPER CONTROLLED) ---
def image_gatekeeper_node(state: GraphState):
    """Görüntü kalitesini kontrol eder."""
    return image_gatekeeper_service(state=state)

def image_analyzer_node(state: GraphState):
    """CNN analizi ve Grad-CAM üretimini yapar."""
    return image_analyzer_service(state=state)

def image_skip_node(state: GraphState):
    """Görüntü (Röntgen, MR vb.) yoksa veya geçersizse CNN analizini güvenlice pas geçer."""
    print("\n⏭️ [IMAGE SKIP] Geçerli bir medikal görüntü (Röntgen/MR/OCT) bulunamadı, Görüntü Uzmanları (CNN) atlanıyor...")
    
    # En sondaki Uzman Doktor (Final LLM) ajanının halüsinasyon görmesini engellemek için
    # State'teki görüntü analizi alanını net bir "Sistem Notu" ile dolduruyoruz.
    skip_message = {
    "System_Note": "Image-based (CNN) disease risk analysis was not performed because no valid radiological or medical image (X-ray, MRI, Fundus, etc.) belonging to the patient was detected."
}
    
    return {"image_analysis_results": skip_message}

def document_loader_node(state: GraphState):
    """
    LangGraph akışının en başında çalışır. 
    State'te bir PDF yolu varsa onu okur ve metni State'e yazar.
    Böylece MLP Control Service doğrudan bu temiz metni kullanabilir.
    """
    print("\n📄 [DOCUMENT LOADER] Tahlil PDF'i sisteme yükleniyor ve metne çevriliyor...")
        
    return document_loader_service(state=state)

def lab_gatekeeper_node(state: GraphState):
    """Lab verisi tutarlılığını kontrol eder."""
    return mlp_control_service(state=state)

def lab_analyzer_node(state: GraphState):
    """MLP analizi ve Feature Importance çıkarır."""
    return lab_analyzer_service(state=state)

def lab_skip_node(state: GraphState):
    """Lab verisi yoksa veya kötüyse MLP analizini güvenlice pas geçer."""
    print("\n⏭️ [LAB SKIP] Geçerli bir tahlil bulunamadı, Laboratuvar Uzmanları (MLP) atlanıyor...")
    
    # En sondaki Uzman Doktor (Final LLM) ajanının kafası karışmasın diye,
    # State'teki ilgili alanı "Bilgi" notuyla dolduruyoruz.
    skip_message = {
    "System_Note": "MLP-based disease risk analysis was not performed because no valid laboratory (blood/urine) test document belonging to the patient was detected."
}
    
    return {"lab_analysis_results": skip_message}

# --- FUSION & REASONING ---
def adaptive_fusion_node(state: GraphState):
    """Modaliteleri ağırlıklandırarak birleştirir."""
    return adaptive_fusion_service(state=state)

def diagnostic_agent_node(state: GraphState):
    """LLM ile klinik teşhis üretir."""
    return diagnostic_agent_service(state=state)

def attribution_node(state: GraphState):
    """Tanıyı kanıtlarla (XAI) eşleştirir."""
    pass

# --- SELF-CORRECTION ---
def self_critique_node(state: GraphState):
    """Halüsinasyon ve çelişki kontrolü yapar."""
    return self_critique_service(state=state)

def conflict_resolver_node(state: GraphState):
    """Çelişkileri çözmek için akışı DiagnosticAgent'a geri gönderir."""
    return conflict_resolver_service(state=state)