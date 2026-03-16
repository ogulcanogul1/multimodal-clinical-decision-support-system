import fitz
import pytesseract
from PIL import Image
import io
import os
from src.graph.state import GraphState


pytesseract.pytesseract.tesseract_cmd = r"D:/Tesseract/tesseract.exe"
def extract_text_with_pymupdf(pdf_path: str) -> str:
    print('*' * 50)
    text = ""
    try:
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text("text", sort=True)
            
            if page_text.strip():
                # Normal PDF → direkt metin al
                text += page_text + "\n"
            else:
                # Görsel PDF → OCR uygula
                print(f"   🔍 Sayfa {page_num + 1}: OCR başlatılıyor...")
                mat = fitz.Matrix(2.0, 2.0)
                pix = page.get_pixmap(matrix=mat)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                
                ocr_text = pytesseract.image_to_string(
                    img,
                    lang="tur+eng",
                    config="--psm 6"
                )
                text += ocr_text + "\n"
                print(f"   ✅ OCR tamamlandı: {len(ocr_text)} karakter")
        
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
    
    if extracted_text:
        print("   ✅ Metin başarıyla çıkarıldı.")
    else:
        print("   ⚠️ Metin çıkarılamadı.")

    return {"raw_document_text": extracted_text}