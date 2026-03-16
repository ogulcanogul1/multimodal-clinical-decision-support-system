from src.graph.state import GraphState

def conflict_resolver_service(state: GraphState):
    """
    Self-Critique düğümünden gelen çelişkiyi/hatayı (conflict) ele alır.
    Diagnostic Agent'ın (Başhekim) raporu düzeltebilmesi için yönlendirici
    bir bağlam (resolution_guidance) oluşturur ve akışı geri gönderir.
    """
    print('*' * 50)

    print("\n🔄 [CONFLICT RESOLVER] Çelişki tespit edildi! Başhekim (Diagnostic Agent) için düzeltme talimatı hazırlanıyor...")
    
    # 1. State'ten Denetçi Geri Bildirimini ve Deneme Sayısını Al
    feedback = state.get("critique_feedback", "An unknown medical inconsistency or hallucination was detected.")
    retry_count = state.get("conflict_retry_count", 0)
    
    # ==========================================
    # 2. SONSUZ DÖNGÜ KORUMASI (Fail-Safe)
    # ==========================================
    if retry_count >= 2:
        print("   🚨 [DİKKAT] Maksimum düzeltme denemesine ulaşıldı! Sonsuz döngü engelleniyor.")
        
        emergency_warning = "\n\n*(System Note: This AI-generated report failed some internal medical cross-checks. Please consult a human specialist for a definitive diagnosis.)*"
        forced_report = state.get("final_report", "") + emergency_warning
        
        return {
            "final_report": forced_report,
            "critique_status": "verified", # Router'ı kandırıp akışı "__end__" düğümüne bitirmeye zorluyoruz
            "conflict_retry_count": retry_count + 1 
        }

    # ==========================================
    # 3. BAŞHEKİM İÇİN DÜZELTME TALİMATI (İNGİLİZCEYE ÇEVRİLDİ VE RAG EKLENDİ)
    # ==========================================
    resolution_guidance = (
        f"\n\n⚠️ CRITICAL WARNING: YOUR PREVIOUS REPORT WAS REJECTED BY THE MEDICAL QA AUDITOR ⚠️\n"
        f"Reason for Rejection / Errors Found:\n"
        f"[{feedback}]\n\n"
        f"YOUR TASK: Carefully read the feedback above and REWRITE the entire report.\n"
        f"Do NOT repeat the hallucinations or contradictions mentioned in the rejection reason. "
        # MİMARİ DÜZELTME: "and 'Medical Literature'" eklendi!
        f"Strictly adhere ONLY to the provided 'Raw Clinical Facts' and 'Medical Literature'."
    )

    print(f"   -> Düzeltme talimatı hazırlandı. (Deneme: {retry_count + 1})")
    print("   -> Akış yeniden 'diagnostic_agent' düğümüne yönlendiriliyor...")

    print(f"""
resolution_guidance : {resolution_guidance}
          
conflict_retry_count : {retry_count + 1}
""")
    return {
        "resolution_guidance": resolution_guidance,
        "conflict_retry_count": retry_count + 1
    }