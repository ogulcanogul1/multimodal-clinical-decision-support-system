import os
from src import logger

# Listeyi doğrudan ana kaynağından çekiyoruz! (Kod tekrarına son)
from src.loaders.pdf_loader import MedicalPDFLoader, pdf_library 

from src.preprocess.base_splitter import FixedSizeSplitter 
from src.embeddings.huggingface_embedding import EmbeddingService
from src.vectorstores.pinecone_vectorstore import PineconeVectorStore
from src.schemas.document import Document
from typing import List
from src.schemas.chunk import Chunk

def run_pipeline():
    logger.info("🎬 Tıbbi Veri Pipeline'ı başlatılıyor...")
    
    splitter = FixedSizeSplitter()
    embedding_service = EmbeddingService()
    vectorstore = PineconeVectorStore()
    
    pdf_dir = "data/pdf"

    for item in pdf_library:
        file_path = os.path.join(pdf_dir, item["file"])
        
        if not os.path.exists(file_path):
            logger.warning(f"⚠️ Dosya eksik, atlanıyor: {item['file']}")
            continue

        logger.info(f"\n🔄 İŞLENİYOR: {item['label']} {'='*20}")
        
        # 1. YÜKLEME
        loader = MedicalPDFLoader(file_path=file_path, start_page=item['start'], end_page=item['end'])
        raw_pages = loader.load()
        
        if not raw_pages:
            continue

        all_chunks_for_pdf = []

        # 2. Pydantic DOC OLUŞTURMA & PARÇALAMA
        for page_dict in raw_pages:
            page_content = page_dict["page_content"]
            page_meta = page_dict["metadata"]
            
            # Senin yazdığın Pydantic Document modeli (Tam uyumlu)
            doc = Document(
                page_content=page_content,
                source=page_meta["source"],
                file_type="pdf",
                document_size=len(page_content)
            )
            
            # Kendi Splitter'ından geçir
            page_chunks:List[Chunk] = splitter.split_documents([doc])
            
            # Metadata zenginleştirme (ID üretimi zaten __post_init__ ile otomatik yapıldı!)
            for chunk in page_chunks:
                # Pinecone'un beklediği page_number'ı enjekte ediyoruz
                chunk.metadata.page_number = page_meta["page_number"]
                
                all_chunks_for_pdf.append(chunk)

        if not all_chunks_for_pdf:
            continue

        # 3. VEKTÖRLEŞTİRME (Senin Qwen/MiniLM Embedding Servisin)
        logger.info(f"🧬 {len(all_chunks_for_pdf)} chunk vektörleştiriliyor...")
        vectors = embedding_service.embed_chunks(all_chunks_for_pdf)

        # 4. PINECONE'A YAZMA (Asenkron Batching ile)
        logger.info(f"📤 {item['label']} Pinecone'a yükleniyor...")
        vectorstore.upsert_chunks(all_chunks_for_pdf, vectors)
        
        logger.info(f"✅ {item['label']} tamamlandı!")

    logger.info("\n🏁 TÜM PIPELINE BAŞARIYLA TAMAMLANDI. Pinecone artık bir Başhekim!")

if __name__ == "__main__":
    run_pipeline()