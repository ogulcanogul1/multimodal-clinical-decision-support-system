from enum import Enum
from typing import List, Optional, Literal
import os

from langgraph.graph import StateGraph, START, END
from src.graph.nodes import *
from src.graph.state import GraphState
from src.graph.enum.node_names import NodeNames 


# --- YÖNLENDİRME MANTIKLARI (ROUTERS) ---

def parser_dynamic_router(state: GraphState) -> List[str]:
    active_outputs = [NodeNames.QUERY_OPTIMIZER.value] 
    if state.get("image_path"):
        active_outputs.append(NodeNames.CNN_CONTROL.value)
    if state.get("lab_results"):
        active_outputs.append(NodeNames.MLP_CONTROL.value)
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
    # 1. Yeni State'e göre doğru değişkenleri çekiyoruz
    final_docs = state.get("final_retrieved_docs") 
    retry_count = state.get("retrieval_retry_count", 0)
    MAX_RETRY = 2 # Grader servisimizde limiti 2 (toplam 3 tur) yapmıştık

    logger.info(f"--- EVALUATING RETRIEVAL QUALITY (Retry Count: {retry_count}/{MAX_RETRY}) ---")

    # 2. EĞER FINAL_DOCS ATANDIYSA (Devam Et)
    # Grader başarılı olduysa veya limit dolduğu için zorla pes ettiyse
    # final_docs None olmaktan çıkar (liste olur).
    if final_docs is not None:
        logger.info(f"Yeterli döküman bulundu ({len(final_docs)} adet) veya limit doldu. Adaptive Fusion'a geçiliyor.")
        return "continue"
    
    # 3. EĞER FINAL_DOCS HALA NONE İSE (Başa Dön)
    # Grader hiç geçerli döküman bulamamış ve sadece sayacı artırmış demektir.
    logger.warning("Geçerli döküman bulunamadı. Retry yoluna (Query Optimizer) giriliyor...")
    return "retry"

def critique_logic(state: GraphState) -> Literal["conflict", "verified"]:
    """
    Denetçi (Self-Critique) düğümünden çıkan karara göre akışı yönlendirir.
    Eğer limit aşılmışsa, çelişki olsa bile sistemi sonsuz döngüden kurtarmak için bitirir.
    """
    status = state.get("critique_status", "conflict") # Güvenlik için varsayılanı conflict yapıyoruz
    retry_count = state.get("conflict_retry_count", 0)
    MAX_RETRY = 2 # Toplam 3 deneme hakkı (0, 1, 2)
    
    logger.info(f"--- ⚖️ EVALUATING CRITIQUE STATUS (Retry Count: {retry_count}/{MAX_RETRY}) ---")

    # 1. DURUM: Denetçi raporu onayladıysa, her şey yolunda.
    if status == "verified":
        logger.info("✅ Rapor denetimden geçti. Akış sonlandırılıyor (__end__).")
        return "verified"
        
    # 2. DURUM: Denetçi hata buldu AMA deneme hakkımız (limit) doldu (Fail-Safe)
    if retry_count >= MAX_RETRY:
        logger.error(f"🚨 Maksimum düzeltme denemesine ({MAX_RETRY}) ulaşıldı! Başhekim hatalı döngüden çıkamadı.")
        logger.warning("Sonsuz döngüyü önlemek için akış zorla onaylanmış sayılarak sonlandırılıyor (__end__).")
        # Burada sistemi kandırıp "verified" dönüyoruz ki LangGraph akışı bitirsin, başa sarmasın.
        return "verified" 

    # 3. DURUM: Denetçi hata buldu ve HALA deneme hakkımız var
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

workflow.add_conditional_edges(
    NodeNames.PARSER.value,
    parser_dynamic_router,
    {
        NodeNames.QUERY_OPTIMIZER.value: NodeNames.QUERY_OPTIMIZER.value,
        NodeNames.CNN_CONTROL.value: NodeNames.CNN_CONTROL.value,
        #NodeNames.MLP_CONTROL.value: NodeNames.MLP_CONTROL.value
        NodeNames.PDF_EXTRACT.value: NodeNames.PDF_EXTRACT.value
    }
)

workflow.add_conditional_edges(
    NodeNames.CNN_CONTROL.value,
    image_gate_logic,
    {"valid": NodeNames.IMAGE_ANALYZER.value, "invalid": NodeNames.IMAGE_SKIP.value}
)

workflow.add_conditional_edges(
    NodeNames.MLP_CONTROL.value,
    lab_gate_logic,
    {"valid": NodeNames.LAB_ANALYZER.value, "invalid": NodeNames.LAB_SKIP.value}
)

workflow.add_edge(NodeNames.PDF_EXTRACT.value,NodeNames.MLP_CONTROL.value)
workflow.add_edge(NodeNames.QUERY_OPTIMIZER.value, NodeNames.HYBRID_SEARCH.value)
workflow.add_edge(NodeNames.QUERY_OPTIMIZER.value, NodeNames.WEB_RESEARCH.value)
workflow.add_edge(NodeNames.HYBRID_SEARCH.value, NodeNames.KNOWLEDGE_SYNTHESIS.value)
workflow.add_edge(NodeNames.WEB_RESEARCH.value, NodeNames.KNOWLEDGE_SYNTHESIS.value)
workflow.add_edge(NodeNames.KNOWLEDGE_SYNTHESIS.value, NodeNames.RETRIEVAL_GRADER.value)

workflow.add_conditional_edges(
    NodeNames.RETRIEVAL_GRADER.value,
    retrieval_quality_logic,
    {"retry": NodeNames.QUERY_OPTIMIZER.value, "continue": NodeNames.ADAPTIVE_FUSION.value}
)

workflow.add_edge(NodeNames.IMAGE_ANALYZER.value, NodeNames.ADAPTIVE_FUSION.value)
workflow.add_edge(NodeNames.IMAGE_SKIP.value, NodeNames.ADAPTIVE_FUSION.value)
workflow.add_edge(NodeNames.LAB_ANALYZER.value, NodeNames.ADAPTIVE_FUSION.value)
workflow.add_edge(NodeNames.LAB_SKIP.value, NodeNames.ADAPTIVE_FUSION.value)

workflow.add_edge(NodeNames.ADAPTIVE_FUSION.value, NodeNames.DIAGNOSTIC_AGENT.value)
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