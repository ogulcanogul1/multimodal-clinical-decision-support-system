import fitz

def extract_text_with_pymupdf(pdf_path: str) -> str:
    """
    Belirtilen PDF dosyasını okur ve metinleri çıkarır.
    'sort=True' parametresi tahlil tablolarının hizasını korumak için hayatidir.
    """
    text = ""
    try:
        # PDF dosyasını aç (Hızlı C++ motoru devreye girer)
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # sort=True: Metin bloklarını okuma sırasına göre dizer (Tablolar için şart)
            page_text = page.get_text("text", sort=True)
            text += page_text + "\n"
            
        doc.close()
        return text.strip()
        
    except Exception as e:
        print(f"❌ [PDF PARSER] Dosya okuma hatası: {str(e)}")
        return ""