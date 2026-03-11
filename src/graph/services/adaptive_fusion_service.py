from src.graph.state import GraphState

def adaptive_fusion_service(state: GraphState):
    """
    Sadece verileri toplar, temizler ve Final LLM için yapılandırılmış bir bağlam (Context) oluşturur.
    Tıbbi yorumlamayı ve çapraz bağlantıları (Cross-Modality) tamamen Final LLM'e bırakır.
    """
    print("\n🧬 [ADAPTIVE FUSION] Veriler toplanıyor ve LLM için sentezleniyor...")

    lab_results = state.get("lab_analysis_results", {})
    image_results = state.get("image_analysis_results", {})
    # DÜZELTME: RAG'den gelen TEMİZLENMİŞ dokümanları alıyoruz!
    retrieved_docs = state.get("final_retrieved_docs", [])

    fusion_report = {
        "Lab_Anomalies": [],
        "Image_Anomalies": [],
        "Literature_Support": "",
        "Total_Anomaly_Count": 0
    }

    # ==========================================
    # 1. SADECE ANORMALLİKLERİ FİLTRELE (LLM Çöple Uğraşmasın)
    # ==========================================
    if isinstance(lab_results, dict) and "Error" not in lab_results and "System_Note" not in lab_results:
        for test_name, result in lab_results.items():
            if "⚠️" in str(result):
                fusion_report["Lab_Anomalies"].append(f"{test_name.replace('_Report', '')}: {result.replace('⚠️ ', '')}")

    if isinstance(image_results, dict) and "System_Note" not in image_results:
        for test_name, result in image_results.items():
            if any(keyword in str(result) for keyword in ["Abnormal", "Tumor", "Detected", "Positive", "Retinopathy", "Glaucoma", "Cataract"]):
                fusion_report["Image_Anomalies"].append(f"{test_name}: {result}")

    fusion_report["Total_Anomaly_Count"] = len(fusion_report["Lab_Anomalies"]) + len(fusion_report["Image_Anomalies"])

    # ==========================================
    # 2. TIBBİ LİTERATÜRÜ (RAG) EKLE
    # ==========================================
    if retrieved_docs:
        doc_texts = [f"[Source {i+1}]: {getattr(doc, 'content', str(doc))}" for i, doc in enumerate(retrieved_docs)]
        fusion_report["Literature_Support"] = "\n\n".join(doc_texts)
    else:
        fusion_report["Literature_Support"] = "No specific medical literature found for this case."

    print(f"✅ Veri Sentezi Tamam! Toplam Anormallik: {fusion_report['Total_Anomaly_Count']}")
    return {"fused_clinical_context": fusion_report}