import os
from glob import glob
from typing import List
from langchain_community.document_loaders import PyMuPDFLoader # Hızlı ve stabil

from src.loaders.base import BaseLoader
from src.schemas.document import Document
from src.core.config import Config
from src import logger
from src.core.exceptions import DataLoaderError

class LocalPDFLoader(BaseLoader):
    def __init__(self):
        super().__init__()
        self.target_dir = Config.LITERATURE_DIR / "pdf"

    def load(self, file_name: str) -> List[Document]:
        """LangChain kullanarak PDF'i okur ve bir liste içinde tek bir Document döner."""
        file_path = self.target_dir / file_name
        
        try:
            loader = PyMuPDFLoader(str(file_path))
            pages = loader.load() # LangChain döküman listesi döner
            
            # Sayfaları tek bir metinde birleştiriyoruz
            full_text = "\n".join([p.page_content for p in pages])

            # Standartımıza uygun olarak listeye sarıp döndürüyoruz
            return [Document(
                page_content=full_text,
                source=file_name,
                file_type="pdf",
                document_size=len(full_text)
            )]
        except Exception as e:
            raise DataLoaderError(f"LangChain PDF okuma hatası {file_name}: {str(e)}")

    def load_all(self) -> List[Document]:
        """Dizindeki tüm PDF'leri tarar ve extend ederek birleştirir."""
        all_documents = []
        pdf_files = glob(os.path.join(str(self.target_dir), "*.pdf"))
        
        for path in pdf_files:
            file_name = os.path.basename(path)
            try:
                # Artik liste döndüğü için extend kullanıyoruz
                docs = self.load(file_name)
                all_documents.extend(docs)
            except DataLoaderError as e:
                logger.error(e)
                continue
                
        logger.info(f"Toplam {len(all_documents)} PDF dökümanı yüklendi.")
        return all_documents