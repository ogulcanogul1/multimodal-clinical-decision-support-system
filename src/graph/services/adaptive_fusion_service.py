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
    # Doktorun şikayeti çoğu zaman chief_complaint yerine message_content'te gelir.
    # chief_complaint null ise doktorun mesajını şikayet olarak kullan ki
    # self_critique bunu "halüsinasyon" sanıp reddetmesin.
    chief_complaint = state.get("chief_complaint") or state.get("message_content") or "Not specified"

    fusion_report = {
        "Patient_Profile": {
            "Age": state.get("patient_age"),
            "Gender": state.get("patient_gender"),
            "Chief_Complaint": chief_complaint,
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
    # 1b. HAM RAPOR FLAG'LERİ (ML modelinden BAĞIMSIZ ground truth)
    # ML modeli "sağlıklı" dese veya atlansa bile, raporun kendi referans
    # aralığına göre H/L işaretlenmiş değerleri doktora MUTLAKA göster.
    # ==========================================
    lab_data = state.get("lab_data")
    if lab_data is not None and getattr(lab_data, "parameters", None):
        for param in lab_data.parameters:
            flag = str(getattr(param, "flag", "") or "").strip().upper()
            if flag not in ("H", "L"):
                continue
            direction = "HIGH" if flag == "H" else "LOW"
            unit = getattr(param, "unit", None) or ""
            ref_min = getattr(param, "ref_min", None)
            ref_max = getattr(param, "ref_max", None)
            ref = f" (Ref: {ref_min}-{ref_max})" if ref_min is not None or ref_max is not None else ""
            name = getattr(param, "name", "?")
            fusion_report["Lab_Anomalies"].append(
                f"{name}: {getattr(param, 'value', '?')} {unit}{ref} [{direction}]".strip()
            )

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

            # CNN uzmanları Türkçe sınıf ismi döner (Katarakt, Glokom, Diyabetik Retinopati,
            # Menenjiyom, Hipofiz...). İngilizce keyword listesiyle eşleştirmek dile bağımlı ve
            # kırılgan — onun yerine "sağlıklı/normal değilse bulgudur" mantığını kullanıyoruz.
            normal_keywords = [
                "normal", "sağlıklı", "saglikli", "healthy",
                "no tumor", "tümör yok", "tumor yok", "negative"
            ]
            is_normal = any(keyword in res_str_lower for keyword in normal_keywords)

            if not is_normal:
                fusion_report["Image_Anomalies"].append(f"{test_name}: {res_str}")

    fusion_report["Total_Anomaly_Count"] = len(fusion_report["Lab_Anomalies"]) + len(fusion_report["Image_Anomalies"])
    
    print(f"✅ Veri Sentezi Tamam! Toplam Anormallik: {fusion_report['Total_Anomaly_Count']}")
    
    # Debug için LLM'e giden gerçek veriyi ekrana basalım ki içimiz rahat etsin
    if fusion_report["Total_Anomaly_Count"] > 0:
        print(f"   🔍 LLM'e Gönderilen Anormallikler: Lab({len(fusion_report['Lab_Anomalies'])}), Image({len(fusion_report['Image_Anomalies'])})")
        for anomaly in fusion_report["Image_Anomalies"]:
            print(f"      -> {anomaly}")

    return {"fused_clinical_context": fusion_report}