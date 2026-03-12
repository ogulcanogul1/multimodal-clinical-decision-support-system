import fitz  # PyMuPDF
import re
from typing import List, Dict
from src import logger
import os

class MedicalPDFLoader:
    def __init__(self, file_path: str, start_page: int = 1, end_page: int = None):
        self.file_path = file_path
        self.start_page = max(1, start_page)
        self.end_page = end_page
        self.page_blacklist = ["table of contents", "index", "references", "bibliography"]

    def _is_garbage_page(self, page_text: str) -> bool:
        header_text = page_text[:200].lower()
        for keyword in self.page_blacklist:
            if keyword in header_text:
                return True
        return False

    def load(self) -> List[Dict]:
        logger.info(f"📄 PDF Yüklenecek: {self.file_path} (Sayfa: {self.start_page} - {self.end_page if self.end_page else 'Son'})")
        
        try:
            doc = fitz.open(self.file_path)
        except Exception as e:
            logger.error(f"PDF açılamadı: {e}")
            return []

        documents = []
        last_page_idx = self.end_page if self.end_page and self.end_page <= len(doc) else len(doc)

        for page_num in range(self.start_page - 1, last_page_idx):
            page = doc[page_num]
            
            rect = page.rect
            page_height = rect.height
            page_width = rect.width
            
            top_margin = page_height * 0.06
            bottom_margin = page_height * 0.92
            left_margin = page_width * 0.05
            right_margin = page_width * 0.95

            blocks = page.get_text("blocks")
            page_text = ""

            for b in blocks:
                x0, y0, x1, y1, text, block_no, block_type = b

                if block_type != 0: 
                    continue
                if y1 < top_margin or y0 > bottom_margin: 
                    continue
                if x1 < left_margin or x0 > right_margin: 
                    continue

                clean_text = text.replace('\n', ' ').strip()
                clean_text = re.sub(r'-\s+', '', clean_text)
                clean_text = re.sub(r'\s+', ' ', clean_text)

                if len(clean_text) > 15: 
                    page_text += clean_text + "\n\n"

            if self._is_garbage_page(page_text):
                logger.debug(f"Sayfa {page_num + 1} kara listeye takıldı (İçindekiler/Kaynakça). Atlanıyor.")
                continue

            if page_text.strip():
                documents.append({
                    "page_content": page_text.strip(),
                    "metadata": {
                        "source": self.file_path.split("/")[-1],
                        "page_number": page_num + 1
                    }
                })

        logger.info(f"✅ {self.file_path.split('/')[-1]} dosyasından {len(documents)} sayfa saf klinik metin çıkarıldı.")
        return documents
    
pdf_library = [
    {
        "file": "standards-of-care-2026.pdf", 
        "start": 11, "end": 300, "label": "ADA (Diyabet)"
        # Orijinalini koruduk, makul görünüyor
    },
    {
        "file": "KDIGO-2024-CKD-Guideline.pdf", 
        "start": 20, "end": 180, "label": "KDIGO (Böbrek)"
        # Orijinalini koruduk
    },
    {
        "file": "Guia-ESC-2024_.pdf", 
        "start": 15, "end": 250, "label": "ESC (Kalp/Tansiyon)"
        # Orijinalini koruduk
    },
    {
        "file": "GINA-Summary-Guide-2024-WEB-WMS.pdf", 
        "start": 3,   # Sayfa 1-2: kapak + telif, içerik sayfa 3'te başlıyor (TOC)
        "end": 49,    # Toplam 49 sayfa, tamamı klinik içerik
        "label": "GINA (Astım)"
    },
    {
        "file": "amckd_nice_guideline_v8.1.pdf", 
        "start": 4,   # Sayfa 1-3: kapak + telif + içindekiler
        "end": 36,    # Toplam 36 sayfa, appendix dahil kalsın
        "label": "NICE (Anemi)"
    },
    {
        "file": "8205Oxford Handbook of Clinical Medicine 10th 2017 Edition_SamanSarKo - Copy.pdf", 
        "start": 30, "end": 850, "label": "Oxford (Genel Klinik)"
        # Orijinalini koruduk
    },
    {
        "file": "harrisons-manual-of-medicine-16th-edition.pdf", 
        "start": 15, "end": 900, "label": "Harrison (Dahiliye)"
        # Orijinalini koruduk
    }
]

if __name__ == "__main__":
    

    print("\n" + "="*60)
    print("🩺 TIBBİ KÜTÜPHANE ÖN İZLEME MODU")
    print("="*60)

    # KRİTİK AYAR: Her kitaptan sadece ilk kaç sayfayı görmek istiyorsun?
    TEST_PAGE_LIMIT = 2 

    for item in pdf_library:
        file_path = f"data/pdf/{item['file']}"
        
        if not os.path.exists(file_path):
            print(f"\n⚠️  HATA: {item['file']} bulunamadı!")
            continue

        # Sadece test amaçlı, end_page'i sınırlıyoruz ki RAM dolmasın
        # Eğer gerçek end_page, start_page + limit'ten küçükse onu korur
        actual_end = min(item['start'] + TEST_PAGE_LIMIT - 1, item['end'] if item['end'] else 9999)

        loader = MedicalPDFLoader(
            file_path=file_path,
            start_page=item['start'],
            end_page=actual_end # İşte gereksiz yüklemeyi engelleyen kısım!
        )
        
        docs = loader.load()

        print(f"\n📚 KAYNAK: {item['label']}")
        print(f"📊 Test için okunan sayfa: {len(docs)} (Toplam aralığı: {item['start']}-{item['end']})")
        
        for i, doc in enumerate(docs):
            print(f"\n🔍 SAYFA {doc['metadata']['page_number']} İÇERİĞİ:")
            print("-" * 30)
            # Sayfanın sadece başını ve sonunu göstererek temizliği kontrol et
            content = doc['page_content']
            print(f"{content[:300]} ... [ARA KISIM] ... {content[-200:]}")
            print("-" * 30)

    print("\n✅ Ön izleme bitti. Eğer çıktılar temizse 'actual_end' kısmını kaldırıp full yükleme yapabilirsin.")