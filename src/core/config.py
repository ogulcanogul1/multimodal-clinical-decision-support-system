import os
from pathlib import Path

class Config:
    
    
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    
    SRC_DIR = BASE_DIR / "src"
    
    
    DATA_DIR = BASE_DIR / "data"
    LOG_DIR = BASE_DIR / "logs"
    WEIGHTS_DIR = BASE_DIR / "weights" 
    
    
    
    LOADERS_DIR = SRC_DIR / "loaders"
    EMBEDDINGS_DIR = SRC_DIR / "embeddings"
    VECTORSTORES_DIR = SRC_DIR / "vectorstores"
    MODULES_DIR = SRC_DIR / "modules"
    GRAPH_DIR = SRC_DIR / "graph"
    FUSION_DIR = SRC_DIR / "fusion"
    RAG_DIR = SRC_DIR / "rag"
    XAI_DIR = SRC_DIR / "xai"
    CORE_DIR = SRC_DIR / "core"

    
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"
    LITERATURE_DIR = RAW_DATA_DIR / "literature" 
    VECTOR_DB_PATH = str(DATA_DIR / "vector_db") 

    
    EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2" 
    CHUNK_SIZE = 500 
    CHUNK_OVERLAP = 50
    LLM_MODEL_NAME = "llama3.2" 

    @classmethod
    def setup_directories(cls):
        """
        Projenin tüm fiziksel ve mantıksal klasör yapısını otomatik oluşturur.
        Hem veri dizinlerini hem de src altındaki modül dizinlerini kurar.
        """
        
        all_directories = [
            
            cls.DATA_DIR, cls.LOG_DIR, cls.WEIGHTS_DIR,
            cls.RAW_DATA_DIR, cls.PROCESSED_DATA_DIR,
            cls.LITERATURE_DIR,
            
            
            cls.LOADERS_DIR, cls.EMBEDDINGS_DIR, cls.VECTORSTORES_DIR,
            cls.MODULES_DIR, cls.GRAPH_DIR, cls.FUSION_DIR,
            cls.RAG_DIR, cls.XAI_DIR, cls.CORE_DIR
        ]

        for directory in all_directories:
            os.makedirs(directory, exist_ok=True)
            # Eğer src altındaki bir modül klasörü ise __init__.py ekle 
            if str(cls.SRC_DIR) in str(directory):
                init_file = directory / "__init__.py"
                if not init_file.exists():
                    with open(init_file, "w", encoding="utf-8") as f:
                        f.write(f"# {directory.name.capitalize()} module\n")


Config.setup_directories()