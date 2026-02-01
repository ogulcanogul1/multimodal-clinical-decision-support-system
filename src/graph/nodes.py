from src.graph.state import GraphState
from src.graph.services.parser_service import parser_service 
from src.graph.services.query_optimizer_service import query_optimizer_service
from src.graph.services.hybrid_search_service import hybrid_search_service
from src.graph.services.web_research_service import web_research_service

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
    pass

def retrieval_grader_node(state: GraphState):
    """Arama kalitesini puanlar (Retry mi yoksa Fusion mı?)."""
    pass

# --- VISION & ANALYTICS (GATEKEEPER CONTROLLED) ---
def image_gatekeeper_node(state: GraphState):
    """Görüntü kalitesini kontrol eder."""
    pass

def image_analyzer_node(state: GraphState):
    """CNN analizi ve Grad-CAM üretimini yapar."""
    pass

def image_skip_node(state: GraphState):
    """Görüntü yoksa veya kötüyse pas geçer."""
    pass

def lab_gatekeeper_node(state: GraphState):
    """Lab verisi tutarlılığını kontrol eder."""
    pass

def lab_analyzer_node(state: GraphState):
    """MLP analizi ve Feature Importance çıkarır."""
    pass

def lab_skip_node(state: GraphState):
    """Lab verisi yoksa veya kötüyse pas geçer."""
    pass

# --- FUSION & REASONING ---
def adaptive_fusion_node(state: GraphState):
    """Modaliteleri ağırlıklandırarak birleştirir."""
    pass

def diagnostic_agent_node(state: GraphState):
    """LLM ile klinik teşhis üretir."""
    pass

def attribution_node(state: GraphState):
    """Tanıyı kanıtlarla (XAI) eşleştirir."""
    pass

# --- SELF-CORRECTION ---
def self_critique_node(state: GraphState):
    """Halüsinasyon ve çelişki kontrolü yapar."""
    pass

def conflict_resolver_node(state: GraphState):
    """Çelişkileri çözmek için akışı DiagnosticAgent'a geri gönderir."""
    pass