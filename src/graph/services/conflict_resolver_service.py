from src.graph.state import GraphState

def conflict_resolver_service(state: GraphState):
    """
    Self-Critique düğümünden gelen çelişkiyi/hatayı (conflict) ele alır.
    Diagnostic Agent'ın (Başhekim) raporu düzeltebilmesi için yönlendirici
    bir bağlam (resolution_guidance) oluşturur ve akışı geri gönderir.
    """
    print("\n🔄 [CONFLICT RESOLVER] Çelişki tespit edildi! Başhekim (Diagnostic Agent) için düzeltme talimatı hazırlanıyor...")
    
    # 1. State'ten Denetçi Geri Bildirimini ve Deneme Sayısını Al
    feedback = state.get("critique_feedback", "Bilinmeyen bir tıbbi tutarsızlık veya halüsinasyon tespit edildi.")
    retry_count = state.get("conflict_retry_count", 0)
    
    # ==========================================
    # 2. SONSUZ DÖNGÜ KORUMASI (Fail-Safe)
    # ==========================================
    # Eğer Başhekim 3 denemede hala halüsinasyon görüyorsa, döngüyü zorla kır!
    if retry_count >= 2:
        print("   🚨 [DİKKAT] Maksimum düzeltme denemesine ulaşıldı! Sonsuz döngü engelleniyor.")
        
        # Hastayı riske atmamak için raporun sonuna yasal bir uyarı ekliyoruz
        emergency_warning = "\n\n*(Sistem Notu: Yapay zeka tabanlı bu rapor, bazı tıbbi çapraz kontrolleri tam olarak geçememiştir. Lütfen teşhis için doğrudan uzman bir hekime başvurunuz.)*"
        forced_report = state.get("final_report", "") + emergency_warning
        
        return {
            "final_report": forced_report,
            "critique_status": "verified", # Router'ı kandırıp akışı "__end__" düğümüne bitirmeye zorluyoruz
            "retry_count": retry_count + 1
        }

    # ==========================================
    # 3. BAŞHEKİM İÇİN DÜZELTME TALİMATI HAZIRLAMA
    # ==========================================
    # Başhekimin (diagnostic_agent) prompt'una eklenecek olan o sert uyarı metni
    resolution_guidance = (
        f"\n\n⚠️ DİKKAT: YAZDIĞINIZ ÖNCEKİ RAPOR TIBBİ DENETÇİ TARAFINDAN REDDEDİLDİ ⚠️\n"
        f"Reddedilme Sebebi / Bulunan Hatalar:\n"
        f"[{feedback}]\n\n"
        f"GÖREVİN: Lütfen yukarıdaki geri bildirimi DİKKATLİCE okuyarak raporu BAŞTAN AŞAĞI YENİDEN YAZ.\n"
        f"Reddedilme sebebindeki çelişkileri veya halüsinasyonları kesinlikle tekrar etme. "
        f"Sadece sana verilen Raw Clinical Facts (Ham Klinik Gerçekler) doğrultusunda hareket et."
    )

    print(f"   -> Düzeltme talimatı hazırlandı. (Deneme: {retry_count + 1})")
    print("   -> Akış yeniden 'diagnostic_agent' düğümüne yönlendiriliyor...")

    # State'i güncelliyoruz. Bu sayede Diagnostic Agent tekrar çalıştığında bu yönergeyi okuyacak.
    return {
        "resolution_guidance": resolution_guidance,
        "conflict_retry_count": retry_count + 1
    }