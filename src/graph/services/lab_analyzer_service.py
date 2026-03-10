import os
import joblib
import pandas as pd
import numpy as np
from src.graph.state import GraphState
from src.schemas.node_schemas.gate_keeper_schemas import LabReport

# 1. TIBBİ ÇEVİRİ SÖZLÜĞÜ (Ters mantıklar ve çoklu sınıflar yönetiliyor)
DIAGNOSIS_MAPPING = {
    "Diabetes": {0: "✅ Sağlıklı", 1: "⚠️ Diyabet Hastası"},
    "Cardiovascular": {0: "✅ Sağlıklı", 1: "⚠️ Kardiyovasküler Hastalık Riski"},
    "Kidney_CKD": {0: "⚠️ Kronik Böbrek Hastalığı (CKD)", 1: "✅ Sağlıklı"}, # Ters Mantık (0: Hasta)
    "Liver": {0: "⚠️ Karaciğer Hastalığı Belirtisi", 1: "✅ Sağlıklı"}, # Ters Mantık (0: Hasta)
    "Thyroid": {0: "✅ Sağlıklı / İyi Huylu", 1: "⚠️ Tiroid Bozukluğu / Nüksetme Riski"},
    "Anemia": {
        0: "✅ Sağlıklı", 1: "⚠️ Demir Eksikliği Anemisi", 2: "⚠️ Lösemi Şüphesi",
        3: "⚠️ Trombositopenili Lösemi", 4: "⚠️ Makrositik Anemi", 
        5: "⚠️ Normositik Hipokromik Anemi", 6: "⚠️ Normositik Normokromik Anemi",
        7: "⚠️ Diğer Mikrositik Anemiler", 8: "⚠️ Trombositopeni"
    }
}

def predict_safely(model, raw_df):
    """
    Kritik Kalkan Fonksiyonu: Modelin beklediği tüm sütunları (dummy kolonlar dahil) dinamik olarak oluşturur.
    Hastanın tahlilinde eksik olan değerleri NaN bırakarak XGBoost'un çökmesini engeller.
    """
    expected_features = model.feature_names_in_
    safe_df = pd.DataFrame(columns=expected_features)
    safe_df.loc[0] = np.nan # Her yeri NaN ile doldur
    
    # Elimizde olan kan değerlerini, modelin beklediği sütunlara aktar
    for col in raw_df.columns:
        if col in expected_features:
            safe_df.at[0, col] = raw_df.at[0, col]
            
    safe_df = safe_df.astype(float) # Tür uyuşmazlığını önle
    prob = model.predict_proba(safe_df)[0]
    pred = model.predict(safe_df)[0]
    return prob, pred


def lab_analyzer_service(state: GraphState):
    """Llama'dan gelen Pydantic verisini 6 XGBoost modeline sokar ve teşhis üretir."""
    print("\n🔬 [LAB ANALYZER] Tahlil verileri 6 Uzman Modele gönderiliyor...")
    
    lab_report: LabReport = state.get("extracted_lab_data")
    
    if not lab_report or not lab_report.is_valid_report:
        return {"lab_analysis_results": {"Hata": "Geçersiz veya okunamayan laboratuvar belgesi."}}

    # 2. ALIAS ARAMA MOTORU
    extracted_dict = {param.name.lower().strip(): param.value for param in lab_report.parameters}
    age = lab_report.patient_age if lab_report.patient_age else 35.0 
    gender_code = 1 if lab_report.patient_gender == 'M' else 0 
    
    def get_val(*aliases):
        for a in aliases:
            if a in extracted_dict:
                return float(extracted_dict[a])
        return np.nan

    # ==========================================
    # 3. VERİ ÇERÇEVELERİ (6 Uzmanın Beklediği Sütunlar)
    # ==========================================
    raw_dfs = {
        "Diabetes": pd.DataFrame([{
            'Pregnancies': np.nan, 
            'Glucose': get_val('glucose', 'glu', 'şeker', 'glukoz', 'açlık şekeri'),
            'BloodPressure': get_val('bloodpressure', 'bp', 'tansiyon', 'systolic'),
            'SkinThickness': np.nan, 
            'Insulin': get_val('insulin', 'ins', 'insülin'),
            'BMI': get_val('bmi', 'vki', 'vücut kitle indeksi'),
            'DiabetesPedigreeFunction': np.nan,
            'Age': age
        }]),
        
        "Liver": pd.DataFrame([{
            'age': age,
            'gender': gender_code,
            'tot_bilirubin': get_val('total bilirubin', 'tbil', 'total bilirübin', 'tb', 'bil-t'),
            'direct_bilirubin': get_val('direct bilirubin', 'dbil', 'direkt bilirübin', 'bil-d'),
            'tot_proteins': get_val('total protein', 'tprot', 'tp', 'total protein'),
            'albumin': get_val('albumin', 'alb'),
            'ag_ratio': get_val('a/g ratio', 'ag_ratio', 'a/g'),
            'sgpt': get_val('sgpt', 'alt', 'alanin aminotransferaz'),
            'sgot': get_val('sgot', 'ast', 'aspartat aminotransferaz'),
            'alkphos': get_val('alkphos', 'alp', 'alkalen fosfataz')
        }]),
        
        "Anemia": pd.DataFrame([{
            'WBC': get_val('wbc', 'lökosit', 'white blood cell'),
            'LYMp': get_val('lymp', 'lymphocyte percentage', 'lenfosit %', 'lym%'),
            'NEUTp': get_val('neutp', 'neutrophil percentage', 'nötrofil %', 'neu%'),
            'LYMn': get_val('lymn', 'lymphocyte count', 'lym#'),
            'NEUTn': get_val('neutn', 'neutrophil count', 'neu#'),
            'RBC': get_val('rbc', 'eritrosit', 'red blood cell'),
            'HGB': get_val('hgb', 'hemoglobin', 'hb'),
            'HCT': get_val('hct', 'hematokrit', 'ht'),
            'MCV': get_val('mcv'),
            'MCH': get_val('mch'),
            'MCHC': get_val('mchc'),
            'PLT': get_val('plt', 'trombosit', 'platelet', 'plt'),
            'PDW': get_val('pdw'),
            'PCT': get_val('pct')
        }]),
        
        "Cardiovascular": pd.DataFrame([{
            'age': age * 365.25, # Dataset yaşı GÜN cinsinden bekliyor!
            'gender': 2 if gender_code == 1 else 1, # Dataset Erkek:2, Kadın:1 olarak kodlamış
            'height': get_val('height', 'boy'),
            'weight': get_val('weight', 'kilo', 'ağırlık'),
            'ap_hi': get_val('ap_hi', 'systolic', 'sistolik tansiyon', 'büyük tansiyon'),
            'ap_lo': get_val('ap_lo', 'diastolic', 'diastolik tansiyon', 'küçük tansiyon'),
            'cholesterol': get_val('cholesterol', 'kolesterol', 'chol'), 
            'gluc': get_val('gluc', 'glukoz', 'glucose', 'şeker'),
            'smoke': np.nan, 'alco': np.nan, 'active': np.nan
        }]),
        
        "Kidney_CKD": pd.DataFrame([{
            'age': age,
            'bp': get_val('bp', 'bloodpressure', 'tansiyon'),
            'bgr': get_val('bgr', 'glucose', 'glu', 'şeker'),
            'bu': get_val('bu', 'bun', 'blood urea', 'üre', 'ure'),
            'sc': get_val('sc', 'creatinine', 'kreatinin', 'crea'),
            'sod': get_val('sod', 'sodium', 'na', 'sodyum'),
            'pot': get_val('pot', 'potassium', 'k', 'potasyum'),
            'hemo': get_val('hemo', 'hemoglobin', 'hgb', 'hb'),
            'pcv': get_val('pcv', 'hct', 'hematokrit'),
            'wc': get_val('wc', 'wbc', 'lökosit'),
            'rc': get_val('rc', 'rbc', 'eritrosit')
        }])
    }

    # ==========================================
    # 4. MODELLERİ ÇALIŞTIR VE TAHMİNLERİ AL
    # ==========================================
    analysis_results = {}
    model_dir = "data/mlp/" 

    for disease_name, raw_df in raw_dfs.items():
        model_path = os.path.join(model_dir, f"{disease_name}_expert_model.joblib")
        
        try:
            if os.path.exists(model_path):
                model = joblib.load(model_path)
                prob, pred = predict_safely(model, raw_df)
                pred_class = int(pred)
                
                # --- Çıktı Mantığı ve İhtimal Hesaplamaları ---
                if disease_name in ["Kidney_CKD", "Liver"]:
                    # TERS MANTIK: 0. Index hasta demektir
                    risk_ratio = prob[0]
                elif disease_name == "Anemia":
                    # ÇOK SINIFLI: Modelin bulduğu sınıfın ihtimalini al
                    risk_ratio = prob[pred_class]
                else:
                    # NORMAL MANTIK: 1. Index hasta demektir (Diabetes, Cardio, Thyroid)
                    risk_ratio = prob[1]
                
                message = DIAGNOSIS_MAPPING[disease_name][pred_class]
                
                # Sadece hastaysa veya yüksek ihtimalli sonuçları vurgula, sağlıklılara düşük risk de
                if disease_name == "Anemia" and pred_class != 0:
                    analysis_results[f"{disease_name}_Report"] = f"{message} (Teşhis Güveni: %{risk_ratio*100:.1f})"
                else:
                    analysis_results[f"{disease_name}_Report"] = f"{message} (Risk Oranı: %{risk_ratio*100:.1f})"
                    
            else:
                analysis_results[f"{disease_name}_Report"] = f"Model Dosyası Bulunamadı ({disease_name}_expert_model.joblib)"
                
        except Exception as e:
            analysis_results[f"{disease_name}_Report"] = f"Analiz Hatası: {str(e)}"

    print("✅ 6 Uzman Model de başarıyla çalıştı ve sonuçlar sentezlendi!")
    for k, v in analysis_results.items():
        print(f"   -> {k}: {v}")

    return {"lab_analysis_results": analysis_results}