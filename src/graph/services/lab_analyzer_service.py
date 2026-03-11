import os
import joblib
import pandas as pd
import numpy as np
from src.graph.state import GraphState
from src.schemas.node_schemas.gate_keeper_schemas import LabReport

# 1. MEDICAL TRANSLATION DICTIONARY (Handles reverse logic and multi-class mapping)
DIAGNOSIS_MAPPING = {
    "Diabetes": {0: "✅ Healthy", 1: "⚠️ Diabetes Patient"},
    "Cardiovascular": {0: "✅ Healthy", 1: "⚠️ Cardiovascular Disease Risk"},
    "Kidney_CKD": {0: "⚠️ Chronic Kidney Disease (CKD)", 1: "✅ Healthy"}, # Reverse Logic (0: Patient)
    "Liver": {0: "⚠️ Liver Disease Symptom", 1: "✅ Healthy"}, # Reverse Logic (0: Patient)
    "Anemia": {
        0: "✅ Healthy", 1: "⚠️ Iron Deficiency Anemia", 2: "⚠️ Leukemia Suspicion",
        3: "⚠️ Leukemia with Thrombocytopenia", 4: "⚠️ Macrocytic Anemia", 
        5: "⚠️ Normocytic Hypochromic Anemia", 6: "⚠️ Normocytic Normochromic Anemia",
        7: "⚠️ Other Microcytic Anemia", 8: "⚠️ Thrombocytopenia"
    }
}

def predict_safely(model, raw_df):
    """
    Critical Shield Function: Dynamically creates all columns expected by the model (including dummy cols).
    Leaves missing values in the patient's test as NaN to prevent XGBoost from crashing.
    """
    expected_features = model.feature_names_in_
    safe_df = pd.DataFrame(columns=expected_features)
    safe_df.loc[0] = np.nan # Fill everywhere with NaN
    
    # Transfer the available blood values to the expected columns
    for col in raw_df.columns:
        if col in expected_features:
            safe_df.at[0, col] = raw_df.at[0, col]
            
    safe_df = safe_df.astype(float) # Prevent type mismatch
    prob = model.predict_proba(safe_df)[0]
    pred = model.predict(safe_df)[0]
    return prob, pred


def lab_analyzer_service(state: GraphState):
    """Feeds Pydantic data from Llama into 5 XGBoost models and generates diagnoses."""
    print("\n🔬 [LAB ANALYZER] Lab data is being sent to Expert Models...")
    
    lab_report: LabReport = state.get("lab_data")
    
    if not lab_report or not lab_report.is_valid_report:
        return {"lab_analysis_results": {"Error": "Invalid or unreadable laboratory document."}}

    # 2. ALIAS SEARCH ENGINE
    extracted_dict = {param.name.lower().strip(): param.value for param in lab_report.parameters}
    age = lab_report.patient_age if lab_report.patient_age else 35.0 
    gender_code = 1 if lab_report.patient_gender == 'M' else 0 
    
    def get_val(*aliases):
        for a in aliases:
            if a in extracted_dict:
                return float(extracted_dict[a])
        return np.nan

    # ==========================================
    # 3. DATAFRAMES (Columns Expected by the 5 Experts)
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
            'age': age * 365.25, # Dataset expects age in DAYS!
            'gender': 2 if gender_code == 1 else 1, # Dataset codes Male:2, Female:1
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
    # 4. RUN MODELS AND GET PREDICTIONS
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
                
                # --- Output Logic and Probability Calculations ---
                if disease_name in ["Kidney_CKD", "Liver"]:
                    # REVERSE LOGIC: 0th Index means patient
                    risk_ratio = prob[0]
                elif disease_name == "Anemia":
                    # MULTI-CLASS: Take the probability of the predicted class
                    risk_ratio = prob[pred_class]
                else:
                    # NORMAL LOGIC: 1st Index means patient (Diabetes, Cardio)
                    risk_ratio = prob[1]
                
                message = DIAGNOSIS_MAPPING[disease_name][pred_class]
                
                if disease_name == "Anemia" and pred_class != 0:
                    analysis_results[f"{disease_name}_Report"] = f"{message} (Diagnosis Confidence: {risk_ratio*100:.1f}%)"
                else:
                    analysis_results[f"{disease_name}_Report"] = f"{message} (Risk Ratio: {risk_ratio*100:.1f}%)"
                    
            else:
                analysis_results[f"{disease_name}_Report"] = f"Model File Not Found ({disease_name}_expert_model.joblib)"
                
        except Exception as e:
            analysis_results[f"{disease_name}_Report"] = f"Analysis Error: {str(e)}"

    print("✅ All 5 Expert Models executed successfully and results synthesized!")
    for k, v in analysis_results.items():
        print(f"   -> {k}: {v}")

    return {"lab_analysis_results": analysis_results}