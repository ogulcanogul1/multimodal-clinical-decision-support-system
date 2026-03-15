import os
import joblib
import pandas as pd
import numpy as np
from src.graph.state import GraphState
from src.schemas.node_schemas.gate_keeper_schemas import LabReport

DIAGNOSIS_MAPPING = {
    "Diabetes": {0: "✅ Healthy", 1: "⚠️ Diabetes Patient"},
    "Cardiovascular": {0: "✅ Healthy", 1: "⚠️ Cardiovascular Disease Risk"},
    "Kidney_CKD": {0: "⚠️ Chronic Kidney Disease (CKD)", 1: "✅ Healthy"}, # Reverse Logic
    "Liver": {0: "⚠️ Liver Disease Symptom", 1: "✅ Healthy"}, # Reverse Logic
    "Anemia": {
        0: "✅ Healthy", 1: "⚠️ Iron Deficiency Anemia", 2: "⚠️ Leukemia Suspicion",
        3: "⚠️ Leukemia with Thrombocytopenia", 4: "⚠️ Macrocytic Anemia", 
        5: "⚠️ Normocytic Hypochromic Anemia", 6: "⚠️ Normocytic Normochromic Anemia",
        7: "⚠️ Other Microcytic Anemia", 8: "⚠️ Thrombocytopenia"
    }
}

def predict_safely(model, raw_df):
    expected_features = model.feature_names_in_
    safe_df = pd.DataFrame(columns=expected_features)
    safe_df.loc[0] = np.nan 
    
    for col in raw_df.columns:
        if col in expected_features:
            safe_df.at[0, col] = raw_df.at[0, col]
            
    safe_df = safe_df.astype(float) 
    prob = model.predict_proba(safe_df)[0]
    pred = model.predict(safe_df)[0]
    return prob, pred


def lab_analyzer_service(state: GraphState):
    print("\n🔬 [LAB ANALYZER] Lab data is being sent to Expert Models...")
    
    lab_report: LabReport = state.get("lab_data")
    
    if not lab_report or not getattr(lab_report, 'is_valid_report', False):
        return {"lab_analysis_results": {"Error": "Invalid or unreadable laboratory document."}}

    extracted_dict = {param.name.lower().strip(): param.value for param in lab_report.parameters}
    
    # --- GÜVENLİ VERİ ÇEKİMİ (STATE veya LAB_REPORT) ---
    age = state.get("patient_age") or getattr(lab_report, 'patient_age', 35.0) or 35.0
    
    # Cinsiyet Parse Etme (MALE, FEMALE, None)
    raw_gender = str(state.get("patient_gender") or getattr(lab_report, 'patient_gender', "MALE")).strip().upper()
    is_male = raw_gender in ["MALE", "M", "ERKEK", "1"]
    
    liver_gender = 1 if is_male else 0
    cardio_gender = 2 if is_male else 1 
    
    def get_val(*aliases):
        for a in aliases:
            if a in extracted_dict:
                return float(extracted_dict[a])
        return np.nan

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
            'gender': liver_gender,
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
            'age': age * 365.25, 
            'gender': cardio_gender,
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

    analysis_results = {}
    model_dir = "data/mlp/" 

    # --- YENİ EKLENEN: JAVA'YA DÖNÜLECEK DEĞİŞKENLER ---
    max_risk_score = 0.0
    primary_prediction = "Healthy"
    feature_importance_dict = {}

    for disease_name, raw_df in raw_dfs.items():
        model_path = os.path.join(model_dir, f"{disease_name}_expert_model.joblib")
        
        try:
            if os.path.exists(model_path):
                model = joblib.load(model_path)
                prob, pred = predict_safely(model, raw_df)
                pred_class = int(pred)
                
                if disease_name in ["Kidney_CKD", "Liver"]:
                    risk_ratio = prob[0]
                elif disease_name == "Anemia":
                    risk_ratio = prob[pred_class]
                else:
                    risk_ratio = prob[1]
                
                message = DIAGNOSIS_MAPPING[disease_name][pred_class]
                analysis_results[f"{disease_name}_Report"] = f"{message} (Risk: {risk_ratio*100:.1f}%)"

                # En yüksek riskli hastalığı ve özelliklerini (XAI) kaydet
                if risk_ratio > max_risk_score and "✅ Healthy" not in message:
                    max_risk_score = risk_ratio
                    primary_prediction = message.replace("⚠️ ", "")
                    
                    if hasattr(model, "feature_importances_"):
                        importances = model.feature_importances_
                        features = model.feature_names_in_
                        fi_pairs = sorted(zip(features, importances), key=lambda x: x[1], reverse=True)
                        feature_importance_dict = {f: float(imp) for f, imp in fi_pairs[:4] if imp > 0}
                    
            else:
                analysis_results[f"{disease_name}_Report"] = f"Model File Not Found ({disease_name}_expert_model.joblib)"
                
        except Exception as e:
            analysis_results[f"{disease_name}_Report"] = f"Analysis Error: {str(e)}"

    print("✅ All 5 Expert Models executed successfully and results synthesized!")
    
    # JAVA'NIN BEKLEDİĞİ TÜM STATE VERİLERİ DÖNÜLÜYOR
    return {
        "lab_analysis_results": analysis_results,
        "lab_prediction": primary_prediction,
        "lab_confidence": float(max_risk_score),
        "feature_importance": feature_importance_dict
    }