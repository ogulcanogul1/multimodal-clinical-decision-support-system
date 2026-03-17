import os
import re
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

# ==========================================
# 🛡️ ZORUNLU HAYATİ TAHLİLLER (KEY FEATURES)
# XGBoost Feature Importance grafiklerinden alınmıştır.
# ==========================================
MANDATORY_FEATURES = {
    "Liver": ["direct_bilirubin", "age", "tot_proteins", "albumin"],
    "Kidney_CKD": ["hemo", "sg", "al"],
    "Diabetes": ["Glucose", "BMI", "Age", "Insulin"],
    "Cardiovascular": ["ap_hi", "cholesterol", "age"],
    "Anemia": ["HGB", "MCHC", "MCH"]
}

# --- 1. LLM Çıktısını Normalize Etme (Key Eşleşme Güvenliği) ---
def normalize_key(key: str) -> str:
    """ 'H G B', 'Hgb.', 'hgb' gibi tüm varyasyonları 'hgb' yapar. """
    return re.sub(r'[^a-z0-9]', '', str(key).lower().strip())

# --- 2. Virgüllü Float Güvenliği (Pydantic Bypass) ---
def parse_safe_float(val):
    """ '3,5' veya '~3.5' gibi LLM'den gelebilecek bozuk stringleri güvenle float yapar. """
    try:
        if isinstance(val, str):
            val = val.replace(',', '.')
            val = re.sub(r'[^\d.]', '', val) # Sadece rakam ve noktayı bırak
        return float(val)
    except (ValueError, TypeError):
        return np.nan

# --- 3. Yeterli Veri Kontrolü ---
def has_enough_data(df: pd.DataFrame, disease_name: str, threshold: float = 0.3) -> tuple[bool, str]:
    """Hayati kolonların varlığını ve minimum veri doluluğunu kontrol eder."""
    mandatory_cols = MANDATORY_FEATURES.get(disease_name, [])
    
    # Zorunlu tahliller kontrolü
    for m_col in mandatory_cols:
        if m_col not in df.columns or pd.isna(df.at[0, m_col]):
            return False, f"Hayati tahlil eksik: {m_col}"
            
    # Genel doluluk oranı kontrolü (%30 altı ise riskli)
    valid_ratio = df.notna().sum(axis=1).iloc[0] / len(df.columns)
    if valid_ratio < threshold:
        return False, f"Yetersiz veri doluluğu (%{valid_ratio*100:.1f})"
        
    return True, "OK"

def predict_safely(model, raw_df):
    expected_features = model.feature_names_in_
    safe_df = pd.DataFrame(columns=expected_features)
    safe_df.loc[0] = np.nan 
    
    for col in raw_df.columns:
        if col in expected_features and pd.notna(raw_df.at[0, col]):
            safe_df.at[0, col] = raw_df.at[0, col]
            
    safe_df = safe_df.astype(float) 
    prob = model.predict_proba(safe_df)[0]
    pred = model.predict(safe_df)[0]
    return prob, pred


def lab_analyzer_service(state: GraphState):
    print('*' * 50)
    print("\n🔬 [LAB ANALYZER] Lab data is being sent to Expert Models...")
    
    lab_report: LabReport = state.get("lab_data")
    
    if not lab_report or not getattr(lab_report, 'is_valid_report', False):
        return {"lab_analysis_results": {"Error": "Invalid or unreadable laboratory document."}}

    # Normalize edilmiş Key ile sözlük oluştur
    extracted_dict = {normalize_key(param.name): param.value for param in lab_report.parameters}
    
    try:
        raw_age = state.get("patient_age") or getattr(lab_report, 'patient_age', 35.0) or 35.0
        age = float(raw_age)
    except (ValueError, TypeError):
        age = 35.0 
    
    raw_gender = str(state.get("patient_gender") or getattr(lab_report, 'patient_gender', "MALE")).strip().upper()
    is_male = raw_gender in ["MALE", "M", "ERKEK", "1"]
    
    liver_gender = 1 if is_male else 0
    cardio_gender = 2 if is_male else 1 
    
    # --- GÜVENLİ VERİ ÇEKİMİ (Sessiz NaN Loglaması eklendi) ---
    def get_val(*aliases):
        for a in aliases:
            norm_alias = normalize_key(a)
            if norm_alias in extracted_dict:
                return parse_safe_float(extracted_dict[norm_alias])
        
        # Sadece eksik verileri görmek için geliştirici ekranına bas (Console'u çok kirletmemek için kısa yazdırıyoruz)
        print(f"   ⚠️ Eksik Tahlil: {aliases[0]}")
        return np.nan

    print("\n🔍 Hastadan Çekilen Veriler Taranıyor...")
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
            'albumin': get_val('albumin', 'alb', 'albümin'),
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
            'PLT': get_val('plt', 'trombosit', 'platelet'),
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
            'bp': get_val('bp', 'bloodpressure', 'tansiyon', 'systolic'),
            'sg': get_val('sg', 'specific gravity', 'dansite', 'özgül ağırlık'), # Yeni eklendi
            'al': get_val('al', 'albumin', 'alb', 'albümin'), # Yeni eklendi
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

    max_risk_score = 0.0
    primary_prediction = "Healthy"
    feature_importance_dict = {}

    print("\n🧠 Modeller Değerlendiriliyor...")
    for disease_name, raw_df in raw_dfs.items():
        model_path = os.path.join(model_dir, f"{disease_name}_expert_model.joblib")
        
        try:
            if not os.path.exists(model_path):
                analysis_results[f"{disease_name}_Report"] = f"Model File Not Found ({disease_name}_expert_model.joblib)"
                continue
                
            model = joblib.load(model_path)
            
            # --- ZIRH: VERİ YETERLİLİK KONTROLÜ ---
            is_valid, error_msg = has_enough_data(raw_df, disease_name)
            if not is_valid:
                print(f"   ⏭️ {disease_name} Modeli Atlandı -> {error_msg}")
                analysis_results[f"{disease_name}_Report"] = f"Analysis Skipped: {error_msg}"
                continue
                
            prob, pred = predict_safely(model, raw_df)
            pred_class = int(pred)
            
            if disease_name in ["Kidney_CKD", "Liver"]:
                risk_ratio = float(prob[0]) 
            elif disease_name == "Anemia":
                risk_ratio = float(prob[pred_class])
            else:
                risk_ratio = float(prob[1])
            
            message = DIAGNOSIS_MAPPING[disease_name][pred_class]
            analysis_results[f"{disease_name}_Report"] = f"{message} (Risk: {risk_ratio*100:.1f}%)"
            print(f"   ✅ {disease_name} Modeli Çalıştı -> {message}")

            if risk_ratio > max_risk_score and "✅ Healthy" not in message:
                max_risk_score = risk_ratio
                primary_prediction = message.replace("⚠️ ", "")
                
                if hasattr(model, "feature_importances_"):
                    importances = model.feature_importances_
                    features = model.feature_names_in_
                    fi_pairs = sorted(zip(features, importances), key=lambda x: x[1], reverse=True)
                    feature_importance_dict = {f: float(imp) for f, imp in fi_pairs[:4] if imp > 0}
                    
        except Exception as e:
            analysis_results[f"{disease_name}_Report"] = f"Analysis Error: {str(e)}"

    print("\n✅ All Expert Models executed and results synthesized!")
    
    return {
        "lab_analysis_results": analysis_results,
        "lab_prediction": primary_prediction,
        "lab_confidence": float(max_risk_score),
        "feature_importance": feature_importance_dict
    }


if __name__ == "__main__":
    import fitz
    import pytesseract
    from PIL import Image
    import io

    pytesseract.pytesseract.tesseract_cmd = r"D:/Tesseract/tesseract.exe"

    pdf_path = r"D:/Python/projects/medical_system/data/resource_db/documents/444a01fc-291f-41af-abd9-75084a988c6f.pdf"

    doc = fitz.open(pdf_path)
    page = doc.load_page(0)
    mat = fitz.Matrix(2.0, 2.0)
    pix = page.get_pixmap(matrix=mat)
    img = Image.open(io.BytesIO(pix.tobytes("png")))

    result = pytesseract.image_to_string(img, lang="tur+eng", config="--psm 6")
    print(result)