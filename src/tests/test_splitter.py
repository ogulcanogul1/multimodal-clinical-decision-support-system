import pytest
from src.preprocess.fixed_size_splitter import FixedSizeSplitter
from src.schemas.document import Document
from src.core.config import Config

# pytest src/tests/test_splitter.py
@pytest.fixture # nesne test için dependency olarak verilecek
def splitter():
    
    return FixedSizeSplitter()

def test_split_documents_word_boundaries(splitter):
   
    content = "Bu bir test cumlesidir."
    
    
    doc = Document(
        page_content=content,
        source="test.txt",
        file_type="txt",
        document_size=len(content)
    )
    
    chunks = splitter.split_documents([doc])
    
    assert len(chunks) > 0
    for chunk in chunks:
        
        assert chunk.content.strip() == chunk.content

def test_split_documents_overlap(splitter):
    
    content = "Bir iki uc dort bes alti yedi sekiz"
    doc = Document(
        page_content=content,
        source="overlap_test.txt",
        file_type="txt",
        document_size=len(content)
    )
    
    
    splitter.chunk_size = 12 
    splitter.overlap = 6    
    
    chunks = splitter.split_documents([doc])
    
    
    assert len(chunks) >= 2
    
    first_content = chunks[0].content
    second_content = chunks[1].content
    
    # İki chunk arasında en az bir ortak kelime olduğunu doğrula
    common_words = set(first_content.split()) & set(second_content.split())
    assert len(common_words) > 0, f"Ortak kelime bulunamadı! C1: {first_content}, C2: {second_content}"

def test_chunk_id_consistency(splitter):
    # 3. Senaryo: Dataclass __post_init__ çalışıyor mu? (Hash tutarlılığı)
    content = "Hash test içeriği."
    doc = Document(
        page_content=content,
        source="hash.txt",
        file_type="txt",
        document_size=len(content)
    )
    
    chunks = splitter.split_documents([doc])
    
    assert chunks[0].chunk_id is not None
    assert len(chunks[0].chunk_id) == 64 # SHA-256 uzunluğu