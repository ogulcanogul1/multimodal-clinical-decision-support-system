from enum import Enum
from typing import List, Optional, Literal
import os
import logging # Logger tanımlı değilse hata vermesin diye eklendi

from langgraph.graph import StateGraph, START, END
from src.graph.nodes import *
from src.graph.state import GraphState
from src.graph.enum.node_names import NodeNames 

logger = logging.getLogger(__name__)

# --- YÖNLENDİRME MANTIKLARI (ROUTERS) ---

def parser_dynamic_router(state: GraphState) -> List[str]:
    """
    BAŞLANGIÇ YÖNLENDİRİCİSİ:
    Artık RAG (Query Optimizer) burada KÖRKÜTÜK BAŞLAMAYACAK.
    Sadece analiz edilmesi gereken bir modalite (Resim/PDF) varsa o dalları başlatır.
    """
    active_outputs = [] 
    
    if state.get("image_path"):
        active_outputs.append(NodeNames.CNN_CONTROL.value)
    
    # PDF veya Raw Text varsa Lab dalını başlat
    if state.get("lab_results") or state.get("pdf_path") or state.get("raw_document_text"):
        active_outputs.append(NodeNames.PDF_EXTRACT.value)
        
    # EĞER SADECE METİN (SOHBET) GELDİYSE:
    # Resim veya PDF yoksa doğrudan Adaptive Fusion'a gitsin ki oradan RAG'e geçebilsin.
    if not active_outputs:
        active_outputs.append(NodeNames.ADAPTIVE_FUSION.value)
        
    return active_outputs

def image_gate_logic(state: GraphState) -> Literal["valid", "invalid"]:
    if state.get("is_image_medical"): 
        return "valid"
    return "invalid"

def lab_gate_logic(state: GraphState) -> Literal["valid", "invalid"]:
    if state.get("lab_results"):
        return "valid"
    return "invalid"

def retrieval_quality_logic(state: GraphState) -> Literal["retry", "continue"]:
    """
    Grader'dan gelen sonuçlara göre akışa karar verir.
    """
    final_docs = state.get("final_retrieved_docs") 
    retry_count = state.get("retrieval_retry_count", 0)
    MAX_RETRY = 2 

    logger.info(f"--- EVALUATING RETRIEVAL QUALITY (Retry Count: {retry_count}/{MAX_RETRY}) ---")

    # 2. EĞER FINAL_DOCS ATANDIYSA (Devam Et)
    if final_docs is not None:
        # DÜZELTME: Artık RAG bittiğinde Fusion'a değil, direkt Başhekime gidiyoruz!
        logger.info(f"Yeterli döküman bulundu ({len(final_docs)} adet) veya limit doldu. Diagnostic Agent'a geçiliyor.")
        return "continue"
    
    # 3. EĞER FINAL_DOCS HALA NONE İSE (Başa Dön)
    logger.warning("Geçerli döküman bulunamadı. Retry yoluna (Query Optimizer) giriliyor...")
    return "retry"

def critique_logic(state: GraphState) -> Literal["conflict", "verified"]:
    """
    Denetçi (Self-Critique) düğümünden çıkan karara göre akışı yönlendirir.
    """
    status = state.get("critique_status", "conflict") 
    retry_count = state.get("conflict_retry_count", 0)
    MAX_RETRY = 2 
    
    logger.info(f"--- ⚖️ EVALUATING CRITIQUE STATUS (Retry Count: {retry_count}/{MAX_RETRY}) ---")

    if status == "verified":
        logger.info("✅ Rapor denetimden geçti. Akış sonlandırılıyor (__end__).")
        return "verified"
        
    if retry_count >= MAX_RETRY:
        logger.error(f"🚨 Maksimum düzeltme denemesine ({MAX_RETRY}) ulaşıldı! Başhekim hatalı döngüden çıkamadı.")
        logger.warning("Sonsuz döngüyü önlemek için akış zorla onaylanmış sayılarak sonlandırılıyor (__end__).")
        return "verified" 

    logger.warning(f"🔄 Raporda tıbbi çelişki tespit edildi! Düzeltme talimatı için Conflict Resolver'a gidiliyor...")
    return "conflict"


# --- GRAPH KURULUMU ---

workflow = StateGraph(GraphState)

# Nodes
workflow.add_node(NodeNames.PARSER.value, input_parser_node)
workflow.add_node(NodeNames.QUERY_OPTIMIZER.value, query_optimizer_node)
workflow.add_node(NodeNames.HYBRID_SEARCH.value, hybrid_search_node)
workflow.add_node(NodeNames.WEB_RESEARCH.value, web_research_node)
workflow.add_node(NodeNames.KNOWLEDGE_SYNTHESIS.value, knowledge_synthesis_node)
workflow.add_node(NodeNames.RETRIEVAL_GRADER.value, retrieval_grader_node)

workflow.add_node(NodeNames.CNN_CONTROL.value, image_gatekeeper_node)
workflow.add_node(NodeNames.IMAGE_ANALYZER.value, image_analyzer_node)
workflow.add_node(NodeNames.IMAGE_SKIP.value, image_skip_node)

workflow.add_node(NodeNames.PDF_EXTRACT.value, document_loader_node)
workflow.add_node(NodeNames.MLP_CONTROL.value, lab_gatekeeper_node)
workflow.add_node(NodeNames.LAB_ANALYZER.value, lab_analyzer_node)
workflow.add_node(NodeNames.LAB_SKIP.value, lab_skip_node)

workflow.add_node(NodeNames.ADAPTIVE_FUSION.value, adaptive_fusion_node)
workflow.add_node(NodeNames.DIAGNOSTIC_AGENT.value, diagnostic_agent_node)
workflow.add_node(NodeNames.ATTRIBUTION.value, attribution_node)
workflow.add_node(NodeNames.SELF_CRITIQUE.value, self_critique_node)
workflow.add_node(NodeNames.CONFLICT_RESOLVER.value, conflict_resolver_node)

# --- BAĞLANTILAR (EDGES) ---

workflow.add_edge(START, NodeNames.PARSER.value)

# 1. PARSER ÇIKIŞI: Sadece Modaliteleri (veya doğrudan Fusion'ı) başlatır
workflow.add_conditional_edges(
    NodeNames.PARSER.value,
    parser_dynamic_router,
    {
        NodeNames.CNN_CONTROL.value: NodeNames.CNN_CONTROL.value,
        NodeNames.PDF_EXTRACT.value: NodeNames.PDF_EXTRACT.value,
        NodeNames.ADAPTIVE_FUSION.value: NodeNames.ADAPTIVE_FUSION.value # Sadece metin geldiyse RAG öncesi buraya uğrar
    }
)

# 2. GÖRÜNTÜ (CNN) DALI
workflow.add_conditional_edges(
    NodeNames.CNN_CONTROL.value,
    image_gate_logic,
    {"valid": NodeNames.IMAGE_ANALYZER.value, "invalid": NodeNames.IMAGE_SKIP.value}
)
workflow.add_edge(NodeNames.IMAGE_ANALYZER.value, NodeNames.ADAPTIVE_FUSION.value)
workflow.add_edge(NodeNames.IMAGE_SKIP.value, NodeNames.ADAPTIVE_FUSION.value)

# 3. LABORATUVAR (MLP) DALI
workflow.add_edge(NodeNames.PDF_EXTRACT.value, NodeNames.MLP_CONTROL.value)
workflow.add_conditional_edges(
    NodeNames.MLP_CONTROL.value,
    lab_gate_logic,
    {"valid": NodeNames.LAB_ANALYZER.value, "invalid": NodeNames.LAB_SKIP.value}
)
workflow.add_edge(NodeNames.LAB_ANALYZER.value, NodeNames.ADAPTIVE_FUSION.value)
workflow.add_edge(NodeNames.LAB_SKIP.value, NodeNames.ADAPTIVE_FUSION.value)

# =========================================================================
# 🥇 MİMARİ DEĞİŞİKLİĞİN KALBİ BURASI (SEQUENTIAL REASONING)
# =========================================================================

# 4. ADAPTIVE FUSION ÇIKIŞI -> RAG (QUERY OPTIMIZER)
# Modellerin bulduğu anormallikleri (Diyabet, Zatürre vb.) sentezledik. 
# Şimdi bu zengin sentezi literatürde araştırmak üzere Query Optimizer'a gönderiyoruz!
workflow.add_edge(NodeNames.ADAPTIVE_FUSION.value, NodeNames.QUERY_OPTIMIZER.value)

# 5. RAG (ARAŞTIRMA) DALI
workflow.add_edge(NodeNames.QUERY_OPTIMIZER.value, NodeNames.HYBRID_SEARCH.value)
workflow.add_edge(NodeNames.QUERY_OPTIMIZER.value, NodeNames.WEB_RESEARCH.value)
workflow.add_edge(NodeNames.HYBRID_SEARCH.value, NodeNames.KNOWLEDGE_SYNTHESIS.value)
workflow.add_edge(NodeNames.WEB_RESEARCH.value, NodeNames.KNOWLEDGE_SYNTHESIS.value)
workflow.add_edge(NodeNames.KNOWLEDGE_SYNTHESIS.value, NodeNames.RETRIEVAL_GRADER.value)

# 6. RAG ÇIKIŞI -> DİAGNOSTİK AGENT (BAŞHEKİM)
# Arama bitti, elde edilen bilimsel makaleler ve tüm anormallikler Başhekime sunuluyor!
workflow.add_conditional_edges(
    NodeNames.RETRIEVAL_GRADER.value,
    retrieval_quality_logic,
    {
        "retry": NodeNames.QUERY_OPTIMIZER.value, 
        "continue": NodeNames.DIAGNOSTIC_AGENT.value # Eskiden Fusion'a gidiyordu, şimdi Başhekime!
    }
)

# =========================================================================

# 7. RAPORLAMA VE DENETİM (SELF-CRITIQUE) DALI
workflow.add_edge(NodeNames.DIAGNOSTIC_AGENT.value, NodeNames.ATTRIBUTION.value)
workflow.add_edge(NodeNames.ATTRIBUTION.value, NodeNames.SELF_CRITIQUE.value)

workflow.add_conditional_edges(
    NodeNames.SELF_CRITIQUE.value,
    critique_logic,
    {"conflict": NodeNames.CONFLICT_RESOLVER.value, "verified": END}
)
workflow.add_edge(NodeNames.CONFLICT_RESOLVER.value, NodeNames.DIAGNOSTIC_AGENT.value)

app = workflow.compile()

def save_graph(app=app, filename="src/graph/graph.png"):
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "wb") as f:
            f.write(app.get_graph().draw_mermaid_png(max_retries=5, retry_delay=2.0))
        print(f"✅ Mimari şuraya kaydedildi: {filename}")
    except Exception as e:
        print(f"❌ Görselleştirme hatası: {e}")

save_graph()