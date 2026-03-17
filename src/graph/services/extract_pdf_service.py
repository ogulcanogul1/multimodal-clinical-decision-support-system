import fitz
import os
from src.graph.state import GraphState

def extract_text_with_pymupdf(pdf_path: str) -> str:
    print('*' * 50)
    text = ""
    try:
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text("text", sort=True)
            text += page_text + "\n"
        
        doc.close()
        return text.strip()
        
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        return ""

def document_loader_service(state: GraphState):
    pdf_path = state.get("document_url")
    print(f"pdf_path : {pdf_path}")
    
    if not pdf_path or not os.path.exists(pdf_path):
        print("   ⚠️ Geçerli bir PDF yolu bulunamadı.")
        return {"raw_document_text": ""}

    extracted_text = extract_text_with_pymupdf(pdf_path)
    print(f"extracted_text length: {len(extracted_text)}")

    # Dijital PDF kontrolü — metin yoksa reddet
    if not extracted_text:
        print("   ❌ Bu PDF taranmış/görsel formatta. Sadece dijital PDF kabul edilmektedir.")
        print("   💡 e-Nabız veya hastane sisteminden export edilen PDF'i yükleyiniz.")
        return {"raw_document_text": "", "pdf_rejection_reason": "scanned_pdf"}

    print("   ✅ Dijital PDF başarıyla okundu.")
    return {"raw_document_text": extracted_text}