from src.graph.state import GraphState
from src.graph.enum.node_names import NodeNames
from src.graph.enum.system_status import SystemStatus
from src import logger 

def parser_service(state:GraphState):
    print("--- INPUT PARSER STARTING ---")
    logger.info("--- INPUT PARSER STARTING ---")
    active_branches = [NodeNames.QUERY_OPTIMIZER.value]
    
    image_path = state.get("image_path")
    if image_path:
        print("Image Bulundu")
        logger.info("Image Bulundu")
        active_branches.append(NodeNames.CNN_CONTROL.value)
    
    # DÜZELTME: Artık lab_results değil, pdf_path veya raw text arıyoruz
    pdf_path = state.get("pdf_path")
    raw_text = state.get("raw_document_text")
    
    if pdf_path or raw_text:
        print(f"📍 Lab document detected. Activating PDF Extract / MLP branch.")
        logger.info("📍 Lab document detected. Activating PDF Extract / MLP branch.")
        # Şemana göre pdf_extract'i tetiklemen gerekiyorsa buraya onun adını yazmalısın.
        # Eğer Edge'lerini direkt mlp_control'e bağladıysan böyle kalabilir.
        active_branches.append(NodeNames.PDF_EXTRACT.value) # veya MLP_CONTROL.value
        
    return {
        "active_branches": active_branches,
        "rag_retry_count": 0,
        "status": SystemStatus.STARTED.value
    }
