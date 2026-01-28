import pytest
import os
from pathlib import Path
from src.loaders.text_loader import LocalTextLoader
from src.schemas.document import Document

def test_local_text_loader_single_file(tmp_path):
    """
    tmp_path: pytest'in sunduğu geçici bir klasör özelliğidir.
    Gerçek diskte dosya yaratmadan test yapmamızı sağlar.
    """
    # 1. Arrange: Test verisi hazırla
    d = tmp_path / "test_data"
    d.mkdir()
    test_file = d / "hello.txt"
    content = "Bu bir test metnidir."
    test_file.write_text(content, encoding="utf-8")

    # Loader'ı başlat
    loader = LocalTextLoader()
    # Test için target_dir'i geçici klasöre yönlendiriyoruz (Mocking benzeri)
    loader.target_dir = d

    # 2. Act: Metodu çalıştır
    doc = loader.load("hello.txt")

    # 3. Assert: Sonuçları kontrol et
    assert isinstance(doc, Document)
    assert doc.page_content == content
    assert doc.metadata.source == "hello.txt"
    assert doc.metadata.file_type == "txt"
    assert doc.metadata.start_index == 0
    assert doc.metadata.end_index == len(content)

def test_local_text_loader_load_all(tmp_path):
    # 1. Arrange: Birden fazla dosya oluştur
    d = tmp_path / "test_all"
    d.mkdir()
    (d / "doc1.txt").write_text("Metin 1", encoding="utf-8")
    (d / "doc2.txt").write_text("Metin 2", encoding="utf-8")
    (d / "not_txt.pdf").write_text("PDF content", encoding="utf-8") # Atlanmalı

    loader = LocalTextLoader()
    loader.target_dir = d

    # 2. Act
    docs = loader.load_all()

    # 3. Assert
    assert len(docs) == 2
    assert any(doc.metadata.source == "doc1.txt" for doc in docs)
    assert any(doc.metadata.source == "doc2.txt" for doc in docs)