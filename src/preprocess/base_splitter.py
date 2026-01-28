from abc import ABC, abstractmethod
from src.schemas.chunk import Chunk
from src.schemas.document import Document
from typing import List

class BaseSplitter(ABC):

    @abstractmethod
    def split_documents(self, docs: List[Document]) -> List[Chunk]:
        pass