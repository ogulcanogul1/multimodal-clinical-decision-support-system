from src import logger

class MedicalAppError(Exception):
    """Tüm uygulama hatalarının temel sınıfı."""
    def __init__(self, message="Bir uygulama hatası oluştu.", metadata=None):
        super().__init__(message)
        self.metadata = metadata # Hangi hasta ID, hangi dosya yolu vb.

# 1. Veri Giriş Hataları 
class DataValidationError(MedicalAppError): 
    """Eksik veya hatalı formatta veri geldiğinde fırlatılır"""
    pass

# 2. Model Çalıştırma Hataları 
class ModelInferenceError(MedicalAppError): 
    """CNN, MLP veya BERT tahmin üretirken oluşan donanım/yazılım hataları"""
    pass

# 3. LLM ve RAG Hataları 
class RAGServiceError(MedicalAppError): 
    """Literatür tarama veya LLM API bağlantı sorunları."""
    pass

class DataLoaderError(RAGServiceError):
    "Veri yüklenirken gerçekleşen hata"
    pass