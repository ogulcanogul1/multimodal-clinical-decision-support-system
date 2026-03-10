from typing import List, Optional, TypedDict, Dict, Any, Annotated
import operator
from src.schemas.document import Document
from src.schemas.node_schemas.gate_keeper_schemas import LabReport

class GraphState(TypedDict):
    # --- HAM GİRİŞLER ---
    query: str
    image_path: Optional[str]
    lab_results: Optional[Dict[str, float]]
    
    active_branches: List[str] 
    
    # --- CONTROL & VALIDATION ---
    is_image_medical: bool      # Resim tıbbi bir görüntü mü?
    is_lab_consistent: bool     # Lab değerleri biyolojik olarak anlamlı mı?
    gatekeeper_notes: str       # Neden reddedildiğine dair kısa not
    
    # --- RAG & RESEARCH INTELLIGENCE ---
    optimized_queries: Dict[str, str] # Local ve Web için ayrı sorgular
    retrieved_docs: Annotated[List[Document], operator.add]
    web_results: List[Dict[str, Any]]
    retrieval_retry_count: int # Döngü sayacı
    is_search_reliable: bool 
    rag_weight: float           # Fusion'da RAG'in etki katsayısı
    
    # --- MULTIMODAL ANALİZ & XAI (AÇIKLANABİLİRLİK) ---
    image_path:Optional[str]
    image_features: Optional[Any]     # CNN öznitelik vektörü
    grad_cam_path: Optional[str]      # Gradcam dosya yolu
    lab_features: Optional[Any]       # MLP öznitelik vektörü
    feature_importance: Dict[str, float] # Karara en çok etki eden lab parametreleri

    # Image_gatekeeper_node
    modality:Optional[str]
    is_valid:Optional[bool]
    vlm_note:Optional[str]
    image_analysis_results:Optional[Any]

    # LAB
    lab_data:Optional[LabReport]
    lab_is_valid:Optional[bool]
    lab_analysis_results:Optional[Any]

    #Adaptive Fusion
    fused_clinical_context:Optional[Dict]
    
   # Self Critique
    critique_status:Optional[str]
    critique_feedback:Optional[str]
    conflict_retry_count:Optional[int]
    
    # --- ÇIKTI ---
    final_report: str                 # Atıflı, kanıtlı ve XAI destekli rapor
    evidence_links: Dict[str, Any]    # Rapor içindeki atıfların ham veri linkleri
    status: str                       # "success", "retry_triggered", "failed"