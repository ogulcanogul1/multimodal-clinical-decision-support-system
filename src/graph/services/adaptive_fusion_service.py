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

    print("image_analysis_result")
    print(image_results)
    print(type(image_results))
    
    # --- YENİ EKLENEN: HASTANIN KLİNİK BAĞLAMI ---
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
    if isinstance(lab_results, dict):
        for test_name, result in lab_results.items():
            # Hayalet anahtarları ve hataları atla
            if test_name in ["System_Note", "Error"] or "Error" in str(result):
                continue
                
            if "⚠️" in str(result):
                fusion_report["Lab_Anomalies"].append(f"{test_name.replace('_Report', '')}: {result.replace('⚠️ ', '')}")

    # ==========================================
    # 2. SADECE ANORMALLİKLERİ FİLTRELE (GÖRÜNTÜ - HAYALET TUZAĞI ÇÖZÜLDÜ)
    # ==========================================
    if isinstance(image_results, dict):
        for test_name, result in image_results.items():
            # Geçmiş testlerden kalan hayalet notları döngü içinde atlıyoruz!
            if test_name in ["System_Note", "Error", "Lung_General_Status"] or "Error" in str(result):
                continue
                
            res_str = str(result)
            res_str_lower = res_str.lower()
            
            # Risk taşıyan anahtar kelimeler (Case-insensitive için lower yapıldı)
            risk_keywords = [
                "abnormal", "detected", "positive", "retinopathy", 
                "glaucoma", "cataract", "glioma", "meningioma", "pituitary"
            ]
            
            is_abnormal = any(keyword in res_str_lower for keyword in risk_keywords)
            
            # Eğer tümör kelimesi varsa ve başında "No" yoksa al.
            if ("tumor" in res_str_lower and "no tumor" not in res_str_lower) or is_abnormal:
                fusion_report["Image_Anomalies"].append(f"{test_name}: {res_str}")

    fusion_report["Total_Anomaly_Count"] = len(fusion_report["Lab_Anomalies"]) + len(fusion_report["Image_Anomalies"])
    
    print(f"✅ Veri Sentezi Tamam! Toplam Anormallik: {fusion_report['Total_Anomaly_Count']}")
    
    # Debug için LLM'e giden gerçek veriyi ekrana basalım ki içimiz rahat etsin
    if fusion_report["Total_Anomaly_Count"] > 0:
        print(f"   🔍 LLM'e Gönderilen Anormallikler: Lab({len(fusion_report['Lab_Anomalies'])}), Image({len(fusion_report['Image_Anomalies'])})")
        for anomaly in fusion_report["Image_Anomalies"]:
            print(f"      -> {anomaly}")

    return {"fused_clinical_context": fusion_report}