import os
from src.graph.model.llm_factory_ollama import OllamaLLMFactory
from src.graph.model.OpenAI_llm_factory import OpenAILLMFactory

# .env dosyasından okuyabilirsin veya burayı manuel True/False yapabilirsin
USE_OPENAI = os.getenv("USE_OPENAI", "True").lower() == "true"

if USE_OPENAI:
    print("🌐 [SYSTEM] LLM Engine Active: OpenAI (Cloud API)")
    # Sınıfı bir değişkene atıyoruz (Örneklemiyoruz, direkt sınıfın kendisini veriyoruz)
    ActiveLLMFactory = OpenAILLMFactory
else:
    print("🖥️ [SYSTEM] LLM Engine Active: Ollama (Local Local)")
    ActiveLLMFactory = OllamaLLMFactory