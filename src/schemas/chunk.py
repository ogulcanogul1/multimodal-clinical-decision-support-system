import hashlib
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class ChunkMetadata:
    source: str
    file_type: str
    start_index: int
    end_index: int
    total_doc_size: int
    page_number: Optional[int] = None
    citation_id: Optional[str] = None  # <-- HATA BURADAYDI, "= None" EKLENDİ

@dataclass
class Chunk:
    content: str
    metadata: ChunkMetadata
    chunk_id: str = field(init=False)
    score: Optional[float] = None # bm25 + semantic search score
    reranker_score: Optional[float] = None # reranker score

    def __post_init__(self):
        """Nesne yaratıldığı an bu metod çalışır ve ID'yi generate eder."""
        hash_base = f"{self.metadata.source}_{self.metadata.start_index}_{self.content[:50]}_{len(self.content)}"
        self.chunk_id = hashlib.sha256(hash_base.encode()).hexdigest()