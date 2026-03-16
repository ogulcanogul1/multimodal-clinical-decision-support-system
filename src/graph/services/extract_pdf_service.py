import fitz
from src.graph.state import GraphState
import os

def extract_text_with_pymupdf(pdf_path: str) -> str:
    """
    Belirtilen PDF dosyasını okur ve metinleri çıkarır.
    'sort=True' parametresi tahlil tablolarının hizasını korumak için hayatidir.
    """
    print('*' * 50)
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
    
def document_loader_service(state: GraphState):
    # State'ten dosya yolunu al (main.py'den artık absolute/tam yol geliyor)
    pdf_path = state.get("document_url")
    
    # 1. DÜZELTME: None gelse bile sistemin çökmemesi için f-string kullandık
    print(f"pdf_path : {pdf_path}")
    
    if not pdf_path or not os.path.exists(pdf_path):
        print("   ⚠️ Geçerli bir PDF yolu bulunamadı veya dosya yok.")
        return {"raw_document_text": ""}

    # PyMuPDF ile metni çıkar
    extracted_text = extract_text_with_pymupdf(pdf_path)

    # 2. DÜZELTME: int olan uzunluğu (len), f-string sayesinde güvenle yazdırıyoruz
    print(f"extracted_text length test: {len(extracted_text)}")
    
    if extracted_text:
        print("   ✅ PDF başarıyla okundu ve metin çıkarıldı.")
    else:
        print("   ⚠️ PDF okundu ancak içinden metin çıkarılamadı (Taranmış/Görsel formatta olabilir).")

    # Çıkarılan metni bir sonraki düğüm (mlp_control_service) için State'e yaz
    return {"raw_document_text": extracted_text}