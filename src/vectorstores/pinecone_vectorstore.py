from pinecone import Pinecone
from src.vectorstores.base import BaseVectorStore
from src.core.config import Config
from src import logger
from typing import List
from src.schemas.chunk import Chunk
from src.core.config import Config

class PineconeVectorStore(BaseVectorStore):
    def __init__(self):
        self.pc = Pinecone(api_key=Config.PINECONE_API_KEY)
        self.index = self.pc.Index(Config.PINECONE_INDEX_NAME)
        self.batch_size = 150
        logger.info(f"Pinecone bağlandı: {Config.PINECONE_INDEX_NAME}")


    def upsert_chunks(self, chunks: List[Chunk], vectors: List[List[float]]):
        """
        Vektörleri batch'lere bölerek ve asenkron olarak Pinecone'a yükler.
        """
        total_records = len(chunks)
        logger.info(f"Toplam {total_records} kayıt batch'ler halinde gönderiliyor...")

        # Veriyi batch_size kadar parçalara bölüyoruz
        for i in range(0, total_records, self.batch_size):
            batch_chunks = chunks[i : i + self.batch_size]
            batch_vectors = vectors[i : i + self.batch_size]
            
            records = []
            for chunk, vector in zip(batch_chunks, batch_vectors):
                records.append({
                    "id": chunk.chunk_id,
                    "values": vector,
                    "metadata": {
                        "text": chunk.content,
                        "source": chunk.metadata.source,
                        "file_type": chunk.metadata.file_type,
                        "start_index":chunk.metadata.start_index,
                        "end_index":chunk.metadata.end_index,
                        "total_doc_size":chunk.metadata.total_doc_size
                    }
                })

            # async_req=True ile isteği arka plana atıyoruz
            # Bu, işlemin bitmesini beklemeden bir sonraki döngüye geçmeyi sağlar
            try:
                self.index.upsert(
                    vectors=records, 
                    namespace="medical_data",
                    async_req=True 
                )
                logger.debug(f"Batch gönderildi: {i} - {i + len(records)}")
            except Exception as e:
                logger.error(f"Batch yüklenirken hata: {e}")

        logger.info(f"Tüm batch'ler kuyruğa eklendi ve gönderiliyor.")

    def search(self, query_vector, top_k=5):
        results = self.index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True,
            namespace="medical_data"
        )
        return results.to_dict()
    
