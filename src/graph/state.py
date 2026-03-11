from typing import List, Optional, TypedDict, Dict, Any, Annotated
import operator
from src.schemas.node_schemas.gate_keeper_schemas import LabReport
from src.schemas.chunk import Chunk

class GraphState(TypedDict):
    # --- HAM GİRİŞLER ---
    query: str
    image_path: Optional[str]
    pdf_path: Optional[str]          
    raw_document_text: Optional[str] 
    lab_results: Optional[Dict[str, float]]
    active_branches: List[str] 
    
    # --- CONTROL & VALIDATION ---
    is_image_medical: bool      
    is_lab_consistent: bool     
    gatekeeper_notes: str       
    
    # --- RAG & RESEARCH INTELLIGENCE ---
    optimized_queries: Dict[str, Any] # DÜZELTME: str yerine Any (Liste de alacak)
    retrieved_docs: Annotated[List[Chunk], operator.add] # DÜZELTME: Document yerine Chunk
    final_retrieved_docs: List[Chunk] # EKLENDİ: Temizlenmiş nihai belgeler
    web_results: List[Dict[str, Any]]
    retrieval_retry_count: int 
    is_search_reliable: bool 
    rag_weight: float
    
    # --- MULTIMODAL ANALİZ & XAI (AÇIKLANABİLİRLİK) ---
    image_features: Optional[Any]     # CNN öznitelik vektörü
    grad_cam_path: Optional[str]      # Gradcam dosya yolu
    lab_features: Optional[Any]       # MLP öznitelik vektörü
    feature_importance: Dict[str, float] # Karara en çok etki eden lab parametreleri

    # Image_gatekeeper_node
    modality: Optional[str]
    is_valid: Optional[bool]
    vlm_note: Optional[str]
    image_analysis_results: Optional[Any]

    # LAB
    lab_data: Optional[LabReport]
    lab_is_valid: Optional[bool]
    lab_analysis_results: Optional[Any]

    # Adaptive Fusion
    fused_clinical_context: Optional[Dict]
    
    # Self Critique & Conflict Resolution
    critique_status: Optional[str]
    critique_feedback: Optional[str]
    conflict_retry_count: Optional[int]
    resolution_guidance: Optional[str] # EKLENDİ (Başhekim için düzeltme yönergesi)
    
    # --- ÇIKTI ---
    final_report: str                 # Atıflı, kanıtlı ve XAI destekli rapor
    evidence_links: Dict[str, Any]    # Rapor içindeki atıfların ham veri linkleri
    status: str                       # "success", "retry_triggered", "failed"