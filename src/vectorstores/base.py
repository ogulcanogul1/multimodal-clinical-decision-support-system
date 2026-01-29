
from abc import ABC,abstractmethod
from typing import List,Dict,Any
from src.schemas.chunk import Chunk

class BaseVectorStore(ABC):
    @abstractmethod
    @abstractmethod
    def upsert_chunks(self, chunks: List[Chunk], vectors: List[List[float]]) -> None:
        """Vektörleri ve metadata'yı veritabanına kaydeder."""
        pass

    @abstractmethod
    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Benzerlik araması yapar."""
        pass