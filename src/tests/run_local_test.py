from src.graph.workflow import app
from src.graph.enum.system_status import SystemStatus

def run_local_test():
    print("🚀 CDSS LangGraph Motoru Test İçin Ateşleniyor...\n")
    
    # Sisteme sanki API'den gelmiş gibi bir başlangıç State'i veriyoruz
    initial_state = {
        "query": "Son günlerde aşırı halsizlik ve baş dönmesi yaşıyorum, ekteki tahlilimi yorumlar mısınız?",
        
        # TEST İÇİN ÖNEMLİ: Bilgisayarında var olan gerçek bir PDF'in yolunu buraya yazmalısın!
        # Örneğin: "data/uploads/ornek_kan_tahlili.pdf"
        "pdf_path": "data/uploads/test_tahlil.pdf", 
        
        "image_path": None, # Şimdilik sadece PDF test edelim
        "raw_document_text": "",
        "active_branches": [],
        "retrieval_retry_count": 0,
        "conflict_retry_count": 0,
        "status": SystemStatus.STARTED.value
    }

    try:
        # Bütün sistemi tek bir satırla başlatıyoruz!
        final_state = app.invoke(initial_state)

        print("\n" + "="*60)
        print("🎯 BAŞHEKİM FİNAL RAPORU (DIAGNOSTIC AGENT)")
        print("="*60)
        print(final_state.get("final_report", "Rapor üretilemedi."))
        print("="*60)

    except Exception as e:
        print(f"\n❌ SİSTEM ÇÖKTÜ: {str(e)}")

if __name__ == "__main__":
    run_local_test()