from enum import Enum
from langchain_ollama import ChatOllama
from src.schemas.node_schemas.rag_schemas import OptimizedQueries,Grade
from src.schemas.node_schemas.gate_keeper_schemas import ImageAnalysis, LabReport
from src.schemas.node_schemas.self_critique import CritiqueOutput



class OllamaModelNames(str,Enum):
    LLAMA_8B= "llama3.1:8b"
    LLAMA_VISION = "llama3.2-vision" 
class OllamaLLMFactory:

    @staticmethod
    def query_optimizer_llm():

        llm = ChatOllama(model=OllamaModelNames.LLAMA_8B,temperature=0.1,format="json")
        
        return llm.with_structured_output(OptimizedQueries)
    
    @staticmethod
    def retrieval_grader_llm():
        llm = ChatOllama(model=OllamaModelNames.LLAMA_8B,temperature=0.1,format="json")
        return llm.with_structured_output(Grade)
    
    @staticmethod
    def image_gatekeeper_llm():
        """Görüntüleri analiz eden ve yapılandırılmış veri dönen VLM."""
        # Ollama'da Llama 3.2 Vision gibi bir multimodal model seçmelisin
        vlm = ChatOllama(
            model=OllamaModelNames.LLAMA_VISION, # VLM model ismin
            temperature=0.0,         # Karar verici mekanizmalarda sıfır yaratıcılık
            format="json"
        )
        return vlm.with_structured_output(ImageAnalysis)
    
    @staticmethod
    def lab_extractor_llm():
        """Laboratuvar raporlarından (PDF metni veya OCR) kesin veri çıkaran LLM."""
        llm = ChatOllama(
            model=OllamaModelNames.LLAMA_8B, # veya llama3.2, sisteminde hangisi varsa
            temperature=0.0,     # Veri çıkarma işleminde YARATICILIK İSTEMİYORUZ!
            format="json"        # Kesinlikle JSON dönecek
        )
        # LLM'i hazırladığımız LabReport şemasına mühürlüyoruz
        return llm.with_structured_output(LabReport)
    
    @staticmethod
    def diagnostic_llm():
        """
        Başhekim (Diagnostic Agent) Modeli:
        Sistemin en zeki modeli olmalıdır. Tüm verileri sentezleyip rapor yazar.
        Öneri: llama3.1 (8b) veya llama3.2
        """
        return ChatOllama(
            model=OllamaModelNames.LLAMA_8B, # Kendi bilgisayarındaki modele göre burayı değiştirebilirsin
            temperature=0.2,  # Biraz empatik yazabilmesi için 0.2 verdik, ama çok uydurmaması lazım
            max_tokens=2048
        )
    
    @staticmethod
    def critique_llm():
        """
        Sıfır yaratıcılıkla çalışan ve DOĞRUDAN CritiqueOutput 
        sınıfına kilitlenmiş (structured) denetçi modeli döner.
        """
        llm = ChatOllama(
            model=OllamaModelNames.LLAMA_8B, 
            temperature=0.0
        )
        # Sınıf zaten belli, doğrudan gömülü şekilde veriyoruz! Parametreye gerek yok.
        return llm.with_structured_output(CritiqueOutput)