from src.graph.state import GraphState
from src.graph.enum.node_names import NodeNames
from src.graph.enum.system_status import SystemStatus
from src import logger 

def parser_service(state:GraphState):
    """
    Sisteme giren ham veriyi analiz eder ve aktif kolları belirler.
    """
    print("--- INPUT PARSER STARTING ---")
    logger.info("--- INPUT PARSER STARTING ---")
    
    # RAG (Query Optimizer) her zaman aktiftir.
    active_branches = [NodeNames.QUERY_OPTIMIZER.value]
    
    image_path = state.get("image_path")
    if image_path:
        print(f"📍 Image detected: {image_path}. Activating CNN branch.")
        logger.info(f"📍 Image detected: {image_path}. Activating CNN branch.")
        active_branches.append(NodeNames.CNN_CONTROL.value)
    
    lab_results = state.get("lab_results")
    if lab_results:
        print(f"📍 Lab results detected. Activating MLP branch.")
        logger.info(f"📍 Lab results detected. Activating MLP branch.")
        active_branches.append(NodeNames.MLP_CONTROL.value)
    
   
    #'active_branches' Annotated[List, operator.add] olduğu için 
    # doğrudan listeyi döndürmek üzerine ekleme yapacaktır.
    return {
        "active_branches": active_branches,
        "retry_count": 0, # Sayaçları sıfırla
        "status": SystemStatus.STARTED.value
    }
