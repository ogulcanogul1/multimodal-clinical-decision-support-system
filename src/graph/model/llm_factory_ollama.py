from enum import Enum
from langchain_ollama import ChatOllama
from src.schemas.node_schemas.rag_schemas import OptimizedQueries

class OllamaModelNames(str,Enum):
    LLAMA_8B= "llama3.1:8b"

class OllamaLLMFactory:

    @staticmethod
    def query_optimizer_llm():

        llm = ChatOllama(model=OllamaModelNames.LLAMA_8B,temperature=0.1,format="json")
        
        return llm.with_structured_output(OptimizedQueries)