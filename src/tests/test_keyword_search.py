import pytest
from pathlib import Path
from src.vectorstores.keyword_search import KeywordSearchService
from src.schemas.chunk import Chunk, ChunkMetadata

@pytest.fixture
def service(tmp_path):
    """
    Her test için geçici bir klasörde çalışan servis döner.
    Bu sayede gerçek verilerle (Config.DATA_DIR) çakışma yaşanmaz.
    """
    # 1. Geçici bir klasör oluşturuyoruz
    test_dir = tmp_path / "data" / "keyword_search"
    test_dir.mkdir(parents=True)
    
    # 2. Servisi oluşturup yolunu bu geçici klasöre yönlendiriyoruz
    svc = KeywordSearchService()
    svc.index_path = test_dir / "bm25_index.pkl"
    
    # Her test başında BM25 ve chunks'ın boş olduğundan emin olalım
    svc.bm25 = None
    svc.chunks = []
    
    return svc

@pytest.fixture
def sample_chunks():
    """Test için kullanılacak örnek veriler."""
    return [
        Chunk(
            content="Aspirin ağrı kesici ve ateş düşürücü olarak kullanılır.",
            metadata=ChunkMetadata(source="doc1.pdf", file_type="pdf", start_index=0, end_index=50, total_doc_size=100)
        ),
        Chunk(
            content="Potasyum eksikliği kalp ritim bozukluklarına neden olabilir.",
            metadata=ChunkMetadata(source="doc2.pdf", file_type="pdf", start_index=0, end_index=60, total_doc_size=120)
        )
    ]



def test_empty_fit_logic(service):
    """Boş fit sonrası aramanın boş dönmesi gerektiğini doğrular."""
    # Hiçbir veri yüklemiyoruz ve diskte de dosya yok
    results = service.search("test")
    
    assert results == []
    assert service.bm25 is None

def test_persistence_clean(service, sample_chunks):
    """Verinin kaydedilip yeni bir nesne tarafından yüklenebildiğini doğrular."""
    # Önce veriyi kaydedelim
    service.fit(sample_chunks)
    assert service.index_path.exists()
    
    # Yeni bir servis nesnesi oluşturup aynı geçici yola bağlayalım
    from src.vectorstores.keyword_search import KeywordSearchService as KSS
    new_service = KSS()
    new_service.index_path = service.index_path # Aynı geçici dosyaya bakmalı
    
    # Yükleme başarılı olmalı ve veriler gelmeli
    assert new_service.load_index() is True
    assert len(new_service.chunks) == 2
    assert "Aspirin" in new_service.chunks[0].content

def test_tokenization_replace(service):
    """İç metot olan _replace'in noktalama işaretlerini temizlediğini doğrular."""
    dirty_content = "Aspirin, ağrı kesici: etkili midir?"
    tokens = service._replace(dirty_content)
    
    # Beklenen: ['aspirin', 'ağrı', 'kesici', 'etkili', 'midir']
    assert "," not in tokens
    assert ":" not in tokens
    assert "?" not in tokens
    assert "aspirin" in tokens