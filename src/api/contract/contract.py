from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ChatHistoryItem(BaseModel):
    role: str
    content: str

class AgentRequest(BaseModel):
    # Java'dan gelen isimlendirmelere BİREBİR uymak zorundayız (camelCase)
    messageContent: str
    imageUrl: Optional[str] = None
    documentUrl: Optional[str] = None
    chiefComplaint: Optional[str] = None
    
    # Klinik Bağlam
    patientAge: Optional[int] = None
    patientGender: Optional[str] = None
    bloodType: Optional[str] = None
    chronicDiseases: List[str] = []
    allergies: List[str] = []
    currentMedications: List[str] = []
    
    # Sohbet Geçmişi
    chatHistory: List[ChatHistoryItem] = []

class AgentResponse(BaseModel):
    aiMessage: str
    sources: List[Dict[str, Any]] = [] 
    
    # Görüntü Analizi Çıktıları
    imagePrediction: Optional[str] = None
    imageConfidenceScore: Optional[float] = None
    heatmapUrl: Optional[str] = None
    
    # Belge/Tahlil Analizi Çıktıları
    documentPrediction: Optional[str] = None
    documentConfidenceScore: Optional[float] = None
    featureImportance: Optional[Dict[str, Any]] = None