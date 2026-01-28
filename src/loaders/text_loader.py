import os
from glob import glob
from typing import List
from src.loaders.base import BaseLoader
from src.schemas.document import Document
from src.core.config import Config
from src import logger
from src.core.exceptions import DataLoaderError

class LocalTextLoader(BaseLoader):
    def __init__(self):
        super().__init__()
        
        self.target_dir = Config.LITERATURE_DIR / "txt"

    def load(self, file_name: str) -> Document:
        """Tek bir dosyayı ham olarak okur ve Document objesi döner."""
        file_path = self.target_dir / file_name
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            return Document(
                page_content=content,
                source=file_name,
                file_type="txt",
                document_size=len(content)
            )
        except Exception as e:
            raise DataLoaderError(f"Dosya okunurken hata oluştu {file_path}: {e}")

    def load_all(self) -> List[Document]:
        """Tüm txt dosyalarını yükler."""
        all_documents = []
        
        full_paths = glob(os.path.join(str(self.target_dir), "*.txt"))
        
        if not full_paths:
            logger.warning(f"Klasörde txt dosyası yok: {self.target_dir}")
            return []

        for path in full_paths:
            file_name = os.path.basename(path)
            try:
                doc = self.load(file_name)
                all_documents.append(doc) # load() tekil döndüğü için append
            except DataLoaderError as e:
                logger.error(f"Hata, atlanıyor: {e}")
                continue

        logger.info(f"Toplam {len(all_documents)} ham döküman yüklendi.")
        return all_documents