import pytest
import os
from src.loaders.text_loader import LocalTextLoader
from src.schemas.document import Document
from src.loaders.pdf_loader import LocalPDFLoader
import fitz

# pytest src/tests/test_loaders.py

def test_local_text_loader_single_file(tmp_path):
    """
    tmp_path üzerinden geçici dosya sistemi kullanarak tekli dosya yüklemeyi test eder.
    """
    # 1. Arrange: Test verisi ve geçici dosya hazırla
    d = tmp_path / "test_data"
    d.mkdir()
    test_file = d / "hello.txt"
    content = "Bu bir test metnidir."
    test_file.write_text(content, encoding="utf-8")

    # Loader'ı başlat ve hedef dizini geçici klasöre set et
    loader = LocalTextLoader()
    loader.target_dir = d

    # 2. Act: Metodu çalıştır
    doc = loader.load("hello.txt")

    # 3. Assert: Yeni sadeleşmiş şemaya göre doğrula
    assert isinstance(doc, Document)
    assert doc.page_content == content
    assert doc.source == "hello.txt"
    assert doc.file_type == "txt"
    assert doc.document_size == len(content)

def test_local_text_loader_load_all(tmp_path):
    """
    Klasördeki tüm txt dosyalarının başarıyla taranıp taranmadığını test eder.
    """
    # 1. Arrange: Birden fazla txt ve bir tane farklı uzantılı dosya oluştur
    d = tmp_path / "test_all"
    d.mkdir()
    (d / "doc1.txt").write_text("Metin 1", encoding="utf-8")
    (d / "doc2.txt").write_text("Metin 2", encoding="utf-8")
    (d / "not_txt.pdf").write_text("PDF content", encoding="utf-8") # Filtrelenmesi gerekir

    loader = LocalTextLoader()
    loader.target_dir = d

    # 2. Act: Toplu yüklemeyi çalıştır
    docs = loader.load_all()

    # 3. Assert
    # Sadece .txt olan 2 dosya yüklenmiş olmalı
    assert len(docs) == 2
    
    # Dosya isimlerinin doğruluğunu kontrol et
    loaded_sources = [doc.source for doc in docs]
    assert "doc1.txt" in loaded_sources
    assert "doc2.txt" in loaded_sources
    assert "not_txt.pdf" not in loaded_sources

def test_local_pdf_loader_single_file(tmp_path):
    # 1. Arrange: Gerçek bir PDF dosyası oluştur
    d = tmp_path / "pdf_data"
    d.mkdir()
    pdf_path = d / "test.pdf"
    
    # Boş bir PDF oluşturup içine metin yazalım
    doc_gen = fitz.open()
    page = doc_gen.new_page()
    content = "Bu bir PDF test metnidir."
    page.insert_text((50, 50), content)
    doc_gen.save(str(pdf_path))
    doc_gen.close()

    loader = LocalPDFLoader()
    loader.target_dir = d

    # 2. Act
    doc = loader.load("test.pdf")

    # 3. Assert
    assert isinstance(doc, Document)
    assert content in doc.page_content # PDF'den çekilen metin içeriği içermeli
    assert doc.source == "test.pdf"
    assert doc.file_type == "pdf"

def test_local_pdf_loader_load_all(tmp_path):
    # 1. Arrange: İki tane PDF oluştur
    d = tmp_path / "pdf_all"
    d.mkdir()
    
    for name in ["doc1.pdf", "doc2.pdf","doc3.txt"]:
        p = d / name
        doc_gen = fitz.open()
        doc_gen.new_page().insert_text((50, 50), f"Content of {name}")
        doc_gen.save(str(p))
        doc_gen.close()

    loader = LocalPDFLoader()
    loader.target_dir = d

    # 2. Act
    docs = loader.load_all()

    # 3. Assert
    assert len(docs) == 2
    sources = [doc.source for doc in docs]
    assert "doc1.pdf" in sources
    assert "doc2.pdf" in sources

