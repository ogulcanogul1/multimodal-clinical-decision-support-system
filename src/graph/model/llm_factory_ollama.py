from enum import Enum
from langchain_ollama import ChatOllama
from src.schemas.node_schemas.rag_schemas import OptimizedQueries,Grade
from src.schemas.node_schemas.gate_keeper_schemas import ImageAnalysis


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