from src.graph.state import GraphState

def adaptive_fusion_service(state: GraphState):
    """
    Sadece verileri toplar, temizler ve Final LLM için yapılandırılmış bir bağlam (Context) oluşturur.
    Tıbbi yorumlamayı ve çapraz bağlantıları (Cross-Modality) tamamen Final LLM'e bırakır.
    """
    print('*' * 50)

    print("\n🧬 [ADAPTIVE FUSION] Veriler toplanıyor ve LLM için sentezleniyor...")

    lab_results = state.get("lab_analysis_results", {})
    image_results = state.get("image_analysis_results", {})
    

    # --- YENİ EKLENEN: HASTANIN KLİNİK BAĞLAMI ---
    # Final LLM bu rapora bakarak kiminle konuştuğunu bilecek
    fusion_report = {
        "Patient_Profile": {
            "Age": state.get("patient_age"),
            "Gender": state.get("patient_gender"),
            "Chief_Complaint": state.get("chief_complaint", "Not specified"),
            "Chronic_Diseases": state.get("chronic_diseases", []),
            "Allergies": state.get("allergies", []),
            "Medications": state.get("current_medications", [])
        },
        "Lab_Anomalies": [],
        "Image_Anomalies": [],
        "Total_Anomaly_Count": 0
    }

    # ==========================================
    # 1. SADECE ANORMALLİKLERİ FİLTRELE (LAB)
    # ==========================================
    if isinstance(lab_results, dict) and "Error" not in lab_results and "System_Note" not in lab_results:
        for test_name, result in lab_results.items():
            if "⚠️" in str(result):
                fusion_report["Lab_Anomalies"].append(f"{test_name.replace('_Report', '')}: {result.replace('⚠️ ', '')}")

    # ==========================================
    # 2. SADECE ANORMALLİKLERİ FİLTRELE (GÖRÜNTÜ - TUZAK ÇÖZÜLDÜ)
    # ==========================================
    if isinstance(image_results, dict) and "System_Note" not in image_results:
        for test_name, result in image_results.items():
            res_str = str(result)
            
            # DÜZELTME: İçinde "Normal" GECMEYEN ve risk taşıyan kelimeleri alıyoruz.
            # Böylece "Normal (No Tumor)" tuzağa düşmüyor!
            is_abnormal = any(keyword in res_str for keyword in [
                "Abnormal", "Detected", "Positive", "Retinopathy", 
                "Glaucoma", "Cataract", "Glioma", "Meningioma", "Pituitary"
            ])
            
            # Eğer tümör kelimesi varsa ve başında "No" yoksa al.
            if ("Tumor" in res_str and "No Tumor" not in res_str) or is_abnormal:
                fusion_report["Image_Anomalies"].append(f"{test_name}: {res_str}")

    fusion_report["Total_Anomaly_Count"] = len(fusion_report["Lab_Anomalies"]) + len(fusion_report["Image_Anomalies"])

    
    print(f"✅ Veri Sentezi Tamam! Toplam Anormallik: {fusion_report['Total_Anomaly_Count']}")
    return {"fused_clinical_context": fusion_report}