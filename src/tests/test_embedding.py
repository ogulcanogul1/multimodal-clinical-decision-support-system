import pytest
import torch
from src.embeddings.huggingface_embedding import EmbeddingService
from src.schemas.chunk import Chunk, ChunkMetadata

@pytest.fixture(scope="session")
def embedding_service():
    """
    Modeli tüm test süreci için sadece bir kez yükler.
    Bu, testlerin hızını ciddi şekilde artırır.
    """
    return EmbeddingService()

def test_model_initialization(embedding_service):
    """Modelin başarıyla yüklendiğini ve cihaz seçimini kontrol eder."""
    assert embedding_service.model is not None
    # Cihaz seçimi mantıklı mı? (cuda veya cpu)
    assert embedding_service.device in ["cuda", "cpu"]
    # Boyut senin Pinecone index'inle uyumlu mu? (1536 veya 1024)
    assert embedding_service.dimension > 0

def test_embed_chunks_output(embedding_service):
    """Chunk'ların vektöre dönüştürülmesini ve çıktı boyutunu test eder."""
    chunks = [
        Chunk(content="Aspirin yan etkileri nelerdir?", 
              metadata=ChunkMetadata(source="a.pdf", file_type="pdf", start_index=0, end_index=10, total_doc_size=100)),
        Chunk(content="Kalp sağlığı için egzersiz önemlidir.", 
              metadata=ChunkMetadata(source="b.pdf", file_type="pdf", start_index=0, end_index=10, total_doc_size=100))
    ]
    
    embeddings = embedding_service.embed_chunks(chunks)
    
    # İki chunk için iki vektör gelmeli
    assert len(embeddings) == 2
    # Her vektör beklenen boyutta olmalı
    assert len(embeddings[0]) == embedding_service.dimension
    

def test_semantic_similarity(embedding_service):
    """Anlamsal olarak benzer metinlerin daha yakın vektörler ürettiğini doğrular."""
    query_1 = "Baş ağrısı için hangi ilaç kullanılır?"
    query_2 = "Migren tedavisinde kullanılan ağrı kesiciler."
    query_3 = "Uzay madenciliği gelecekte nasıl yapılacak?"
    
    vec_1 = embedding_service.embed_query(query_1)
    vec_2 = embedding_service.embed_query(query_2)
    vec_3 = embedding_service.embed_query(query_3)
    
    # Cosine Similarity hesaplama (vektörler normalize edildiği için dot product yeterli)
    def cosine_sim(v1, v2):
        return sum(a*b for a, b in zip(v1, v2))
    
    sim_1_2 = cosine_sim(vec_1, vec_2) # Benzer konular
    sim_1_3 = cosine_sim(vec_1, vec_3) # Alakasız konular
    
    # Benzer metinlerin skoru, alakasızlardan daha yüksek olmalı
    assert sim_1_2 > sim_1_3

def test_empty_input(embedding_service):
    """Boş giriş verildiğinde servisin nasıl davrandığını test eder."""
    assert embedding_service.embed_chunks([]) == []