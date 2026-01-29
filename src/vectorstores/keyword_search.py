from rank_bm25 import BM25Okapi
from typing import List, Dict, Any
from src.schemas.chunk import Chunk
from src import logger
import pickle
from src.core.config import Config

class KeywordSearchService:
    def __init__(self):
        self.bm25 = None
        self.chunks = []
        
        self.index_path = Config.DATA_DIR / "keyword_search" / "bm25_index.pkl"
        logger.info("Keyword Search Servisi (BM25) hazır.")

    def fit(self, chunks: List[Chunk]):
        if not chunks:
            logger.warning("Fit edilecek veri yok!")
            return
            
        self.chunks = chunks
        
        # Daha temiz bir tokenization (Noktalama işaretlerinden kaynaklı hataları azaltır) # Aspirin | Asprin,  farklı kelime sanmasın

        #chunk.content.lower().replace('.', ' ').replace(',', ' ').split() for chunk in chunks
        tokenized_corpus = [self._replace(chunk.content) for chunk in chunks]
        
        self.bm25 = BM25Okapi(tokenized_corpus)
        logger.info(f"{len(chunks)} chunk ile BM25 dizini oluşturuldu.")
        self.save_index()

    def _replace(self,content:str):
        punctuations = ".,:;?!()[]{}-"
        content = content.lower()

        for char in punctuations:
            content = content.replace(char, ' ')

        return content.split()

    def save_index(self):
        try:
            # Klasörün var olduğundan emin oluyoruz
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.index_path, "wb") as f:
                pickle.dump({"bm25": self.bm25, "chunks": self.chunks}, f)
            logger.info(f"Keyword index şu adrese kaydedildi: {self.index_path}")
        except Exception as e:
            logger.error(f"Index kaydedilirken hata: {e}")

    def load_index(self):
        if self.index_path.exists():
            try:
                with open(self.index_path, "rb") as f:
                    data = pickle.load(f)
                    self.bm25 = data["bm25"]
                    self.chunks = data["chunks"]
                logger.info("Keyword index diskten başarıyla yüklendi.")
                return True
            except Exception as e:
                logger.error(f"Index yüklenirken hata oluştu: {e}")
        return False