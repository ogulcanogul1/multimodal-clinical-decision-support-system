from rank_bm25 import BM25Okapi
from typing import List
from src.schemas.chunk import Chunk
from src import logger
import pickle
import re
from src.core.config import Config

class KeywordSearchService:
    def __init__(self):
        self.bm25 = None
        self.chunks = []
        
        self.index_path = Config.DATA_DIR / "keyword_search" / "bm25_index.pkl"
        
        # 1. DÜZELTME: API AYAĞA KALKARKEN DİSKTEN OKUYUP RAM'E AL!
        # Böylece ilk gelen istekte bekleme süresi sıfır olur.
        if self.index_path.exists():
            self.load_index()
        else:
            logger.info("BM25 dizini henüz oluşturulmamış, boş başlatılıyor.")

    def fit(self, chunks: List[Chunk]):
        if not chunks:
            logger.warning("Fit edilecek veri yok!")
            return
            
        self.chunks = chunks
        
        logger.info("BM25 için tokenization yapılıyor...")
        tokenized_corpus = [self._replace(chunk.content) for chunk in chunks]
        
        self.bm25 = BM25Okapi(tokenized_corpus)
        logger.info(f"{len(chunks)} chunk ile BM25 dizini oluşturuldu.")
        self.save_index()

    def _replace(self, content: str):
        # 2. DÜZELTME: CPU YORMAYAN TEK HAMLELİ TEMİZLİK (REGEX)
        # Döngüye girmeden belirtilen tüm noktalama işaretlerini tek seferde boşluğa çevirir.
        content = str(content).lower()
        content = re.sub(r'[.,:;?!()\[\]{}-]', ' ', content)
        return content.split()
    
    def search(self, query: str, top_k: int = 5) -> List[Chunk]:
        """Kelime bazlı (BM25) arama yapar ve en alakalı chunk'ları döner."""
        if not self.bm25:
            logger.warning("BM25 dizini RAM'de yok, arama yapılamıyor!")
            return []

        tokenized_query = self._replace(query)
        
        # BM25 kendi içinde hızlıdır, direkt sonucu döner
        top_n_chunks = self.bm25.get_top_n(tokenized_query, self.chunks, n=top_k)
        
        return top_n_chunks

    def save_index(self):
        try:
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.index_path, "wb") as f:
                # Sadece bm25 nesnesi ve chunklar pickle'lanır
                pickle.dump({"bm25": self.bm25, "chunks": self.chunks}, f)
            logger.info(f"Keyword index şu adrese kaydedildi: {self.index_path}")
        except Exception as e:
            logger.error(f"Index kaydedilirken hata: {e}")

    def load_index(self):
        try:
            with open(self.index_path, "rb") as f:
                data = pickle.load(f)
                self.bm25 = data["bm25"]
                self.chunks = data["chunks"]
            logger.info("Keyword index (BM25) diskten başarıyla RAM'e yüklendi.")
            return True
        except Exception as e:
            logger.error(f"BM25 Index yüklenirken hata oluştu: {e}")
            return False