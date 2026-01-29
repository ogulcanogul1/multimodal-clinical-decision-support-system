import time
from src.core.config import Config
from src.vectorstores.pinecone_vectorstore import PineconeVectorStore
from src.schemas.chunk import Chunk, ChunkMetadata
from src.embeddings.huggingface_embedding import EmbeddingService
from src import logger


def main():
    
    vector_store = PineconeVectorStore()
    
    logger.info("Test dökümanları hazırlanıyor...")
    sample_texts = [
        "Aspirin ağrı kesici ve ateş düşürücü olarak kullanılır. Günde en fazla 3 tablet alınmalıdır.",
        "Potasyum eksikliği kalp ritim bozukluklarına neden olabilir. Laboratuvar değeri 3.5 altı risklidir.",
        "Finansal raporlara göre şirket bu yıl %20 büyüme hedeflemektedir."
    ]
    
    chunks = []
    for i, text in enumerate(sample_texts):
        metadata = ChunkMetadata(
            source="test_document.pdf",
            file_type="pdf",
            start_index=i * 100,
            end_index=(i + 1) * 100,
            total_doc_size=len(" ".join(sample_texts)),
            page_number=1
        )
        chunks.append(Chunk(content=text, metadata=metadata))

    embedding = EmbeddingService()

    vectors = embedding.embed_chunks(chunks=chunks)

    logger.info("Yükleme işlemi başlıyor...")
    vector_store.upsert_chunks(chunks, vectors)

    logger.info("Verilerin indekslenmesi için 3 saniye bekleniyor...")
    time.sleep(3)

    # 6. Test Sorgusu (Hybrid + Rerank)

    query = "Aspirin kaç tane içilebilir?"
    query_vector = embedding.embed_query(query) # Sorgu için de 1024-dim vektör üretiyoruz
    
    logger.info(f"Sorgu yapılıyor: {query}")
    results = vector_store.get_final_context(query, query_vector, top_k=2)

    # 7. Sonuçları Yazdır
    print("\n" + "="*50)
    print(f"SORGU: {query}")
    print("="*50)
    
    for i, doc in enumerate(results, 1):
        print(f"\nSONUÇ {i}:")
        print(f"Metin: {doc.content}")
        print(f"Kaynak: {doc.metadata.source} (Sayfa: {doc.metadata.page_number})")
        print(f"RRF Skoru: {doc.score:.4f}")
        print(f"Rerank Skoru: {doc.reranker_score:.4f}")
    print("="*50)

if __name__ == "__main__":
    main()