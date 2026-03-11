from enum import Enum
from langchain_openai import ChatOpenAI
from src.schemas.node_schemas.rag_schemas import OptimizedQueries, Grade
from src.schemas.node_schemas.gate_keeper_schemas import ImageAnalysis, LabReport
from src.schemas.node_schemas.self_critique import CritiqueOutput

class OpenAIModelNames(str, Enum):
    # Ucuz, hızlı ve rutin işler (Veri çıkarma, yönlendirme, basit Vision)
    GPT_4O_MINI = "gpt-4o-mini"
    
    # Yüksek zeka, sentez ve klinik muhakeme gerektiren işler
    GPT_4O = "gpt-4o"

class OpenAILLMFactory:

    @staticmethod
    def query_optimizer_llm():
        """Kullanıcı sorusunu arama kelimelerine dönüştürür (Düşük Maliyet)"""
        llm = ChatOpenAI(model=OpenAIModelNames.GPT_4O_MINI, temperature=0.1)
        # OpenAI modellerinde format="json" belirtmeye gerek yoktur, 
        # with_structured_output arka planda Native Function Calling kullanır.
        return llm.with_structured_output(OptimizedQueries)
    
    @staticmethod
    def retrieval_grader_llm():
        """Belge konuyla alakalı mı? (Evet/Hayır) (Düşük Maliyet)"""
        llm = ChatOpenAI(model=OpenAIModelNames.GPT_4O_MINI, temperature=0.1)
        return llm.with_structured_output(Grade)
    
    @staticmethod
    def image_gatekeeper_llm():
        """Görüntüleri analiz eden VLM. (gpt-4o-mini'nin native Vision desteği vardır)"""
        vlm = ChatOpenAI(
            model=OpenAIModelNames.GPT_4O_MINI, 
            temperature=0.0 
        )
        return vlm.with_structured_output(ImageAnalysis)
    
    @staticmethod
    def lab_extractor_llm():
        """OCR ve karmaşık PDF metinlerinden JSON çıkarma. (Düşük Maliyet)"""
        llm = ChatOpenAI(
            model=OpenAIModelNames.GPT_4O_MINI, 
            temperature=0.0
        )
        return llm.with_structured_output(LabReport)
    
    @staticmethod
    def diagnostic_llm():
        """
        👨‍⚕️ BAŞHEKİM (Diagnostic Agent) Modeli:
        Sistemin beynidir. Tüm verileri sentezleyip rapor yazar.
        Yüksek analitik zeka gerektiği için amiral gemisi (GPT-4o) kullanıyoruz.
        """
        return ChatOpenAI(
            model=OpenAIModelNames.GPT_4O,
            temperature=0.2, 
            max_tokens=2048
        )
    
    @staticmethod
    def critique_llm():
        """
        🕵️‍♂️ DENETÇİ (QA Auditor) Modeli:
        Başhekimin yaptığı tıbbi halüsinasyonları ve çelişkileri yakalamak için 
        en az Başhekim kadar zeki olmalıdır. Bu yüzden GPT-4o kullanıyoruz.
        """
        llm = ChatOpenAI(
            model=OpenAIModelNames.GPT_4O, 
            temperature=0.0
        )
        return llm.with_structured_output(CritiqueOutput)