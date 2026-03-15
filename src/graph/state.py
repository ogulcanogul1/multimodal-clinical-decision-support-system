from typing import List, Optional, TypedDict, Dict, Any, Annotated
import operator
from src.schemas.node_schemas.gate_keeper_schemas import LabReport
from src.schemas.chunk import Chunk

class GraphState(TypedDict):
    # --- HAM GİRİŞLER (Java'dan Gelenler) ---
    message_content: str
    image_url: Optional[str]
    document_url: Optional[str]
    chief_complaint: Optional[str]
    
    # --- KLİNİK BAĞLAM (Yeni Eklendi) ---
    patient_age: Optional[int]
    patient_gender: Optional[str]
    blood_type: Optional[str]
    chronic_diseases: List[str]
    allergies: List[str]
    current_medications: List[str]
    chat_history: List[Dict[str, str]]
    
    # --- CONTROL & VALIDATION ---
    active_branches: List[str] 
    is_image_medical: bool      
    is_lab_consistent: bool     
    gatekeeper_notes: str       
    
    # --- RAG & RESEARCH INTELLIGENCE ---
    optimized_queries: Dict[str, Any] 
    retrieved_docs: Annotated[List[Chunk], operator.add] 
    final_retrieved_docs: List[Chunk] 
    web_results: List[Dict[str, Any]]
    retrieval_retry_count: int 
    is_search_reliable: bool 
    rag_weight: float
    
    # --- MULTIMODAL ANALİZ & XAI ---
    image_features: Optional[Any]     
    grad_cam_path: Optional[str]      
    lab_features: Optional[Any]       
    feature_importance: Dict[str, float] 

    # Image Gatekeeper
    modality: Optional[str]
    is_valid: Optional[bool]
    vlm_note: Optional[str]
    
    # Burada modelin ürettiği metin ve skoru tutacağız
    image_prediction: Optional[str]
    image_confidence: Optional[float]

    # Lab Gatekeeper
    lab_data: Optional[LabReport]
    lab_is_valid: Optional[bool]
    lab_prediction: Optional[str]
    lab_confidence: Optional[float]

    # Adaptive Fusion & Conflict
    fused_clinical_context: Optional[Dict]
    critique_status: Optional[str]
    critique_feedback: Optional[str]
    conflict_retry_count: Optional[int]
    resolution_guidance: Optional[str] 
    
    # --- ÇIKTI ---
    final_report: str                
    evidence_links: List[Dict[str, Any]]  # List of Dict yaptık (Java'daki listeye uyum için)
    status: str