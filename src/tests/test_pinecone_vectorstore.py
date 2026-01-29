import pytest
from unittest.mock import MagicMock, patch
from src.vectorstores.pinecone_vectorstore import PineconeVectorStore
from src.schemas.chunk import Chunk, ChunkMetadata

@pytest.fixture
def mock_store():
    """
    Pinecone bağlantısını ve alt servisleri taklit eden 
    temiz bir PineconeVectorStore nesnesi döner.
    """
    with patch('src.vectorstores.pinecone_vectorstore.Pinecone'), \
         patch('src.vectorstores.pinecone_vectorstore.KeywordSearchService'), \
         patch('src.vectorstores.pinecone_vectorstore.RerankerService'):
        
        store = PineconeVectorStore()
        # Pinecone Index nesnesini mock'luyoruz
        store.index = MagicMock()
        return store

@pytest.fixture
def sample_chunks():
    """Test için örnek veri seti."""
    return [
        Chunk(content="Aspirin testi", metadata=ChunkMetadata(source="a.pdf", file_type="pdf", start_index=0, end_index=10, total_doc_size=100)),
        Chunk(content="Potasyum testi", metadata=ChunkMetadata(source="b.pdf", file_type="pdf", start_index=0, end_index=10, total_doc_size=100))
    ]

def test_upsert_logic(mock_store, sample_chunks):
    """Upsert işleminin batch mantığını ve asenkron çağrıları test eder."""
    vectors = [[0.1] * 1536, [0.2] * 1536] # 1536-dim uyumlu
    
    # Her batch için sahte bir 'async result' objesi döner
    mock_async_res = MagicMock()
    mock_store.index.upsert.return_value = mock_async_res
    
    mock_store.upsert_chunks(sample_chunks, vectors)
    
    # Doğrulamalar
    assert mock_store.keyword_search.fit.called # BM25 fit edilmeli
    assert mock_store.index.upsert.called # Pinecone upsert çağrılmalı
    assert mock_async_res.get.called # Asenkron bekleme (get) yapılmalı

def test_semantic_search_mapping(mock_store):
    """Pinecone'dan gelen ham verinin Chunk nesnesine doğru dönüştüğünü test eder."""
    # Pinecone'un döneceği sahte JSON yanıtı
    mock_store.index.query.return_value = {
        'matches': [{
            'id': 'chunk_123',
            'score': 0.95,
            'metadata': {
                'text': 'Tıbbi içerik',
                'source': 'test.pdf',
                'file_type': 'pdf',
                'start_index': 0,
                'end_index': 10,
                'total_doc_size': 100,
                'page_number': 5
            }
        }]
    }
    
    results = mock_store.semantic_search([0.1]*1536)
    
    assert len(results) == 1
    assert results[0].chunk_id == 'chunk_123'
    assert results[0].metadata.page_number == 5
    assert results[0].score == 0.95

def test_get_final_context_flow(mock_store):
    """Hibrit arama ve Reranker akışını test eder."""
    # 1. Mock verileri hazırla
    query = "Hangi ilaç?"
    query_vec = [0.1] * 1536
    
    # Sahte Semantic ve Keyword sonuçları
    c1 = Chunk(content="C1", metadata=ChunkMetadata(source="s", file_type="p", start_index=0, end_index=1, total_doc_size=1))
    c1.chunk_id = "id1"
    
    mock_store.semantic_search = MagicMock(return_value=[c1])
    mock_store.keyword_search.search = MagicMock(return_value=[c1])
    
    # Reranker'ın döneceği döküman
    mock_store.reranker.rerank = MagicMock(return_value=[c1])
    
    # 2. Metodu çalıştır
    final_results = mock_store.get_final_context(query, query_vec, top_k=1)
    
    # 3. Akışın doğruluğunu kontrol et
    assert len(final_results) == 1
    assert mock_store.semantic_search.called
    assert mock_store.keyword_search.search.called
    assert mock_store.reranker.rerank.called

def test_rrf_scoring_logic(mock_store):
    """RRF skorlamasının matematiksel mantığını test eder."""
    c1 = Chunk(content="A", metadata=ChunkMetadata(source="s", file_type="p", start_index=0, end_index=1, total_doc_size=1))
    c1.chunk_id = "doc_1"
    
    # doc_1 her iki listede de 1. sırada olsun
    results = mock_store._apply_rrf(semantic_docs=[c1], keyword_docs=[c1], top_k=1)
    
    # Beklenen RRF skoru: (1/(60+1)) + (1/(60+1)) = 2/61
    expected_score = (1 / (60 + 1)) + (1 / (60 + 1))
    assert results[0].score == pytest.approx(expected_score)