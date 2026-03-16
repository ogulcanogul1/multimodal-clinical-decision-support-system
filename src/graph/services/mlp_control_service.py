from langchain_core.messages import HumanMessage
from src.graph.model.model_abstraction import ActiveLLMFactory
from src.schemas.node_schemas.gate_keeper_schemas import LabReport
from src.graph.state import GraphState



def mlp_control_service(state: GraphState):
    """Tahlil raporunu ayrıştırır ve veritabanından gelen klinik bağlamla birleştirir."""
    print('*' * 50)
    
    print("\n🩸 [MLP CONTROL] Laboratuvar verileri analiz ediliyor...")
    
    raw_lab_text = state.get("raw_document_text", "")

    if raw_lab_text == "":
        return {"lab_data": None, "lab_is_valid": False}
    
    # 1. ELİMİZDEKİ KESİN VERİLERİ (JAVA'DAN GELEN) ALIYORUZ
    patient_age = state.get("patient_age")
    patient_gender = state.get("patient_gender")
    blood_type = state.get("blood_type")
    
    extractor_llm = ActiveLLMFactory.lab_extractor_llm()
    
    # 2. PROMPT'U HAFİFLETTİK: LLM'den artık yaş ve cinsiyet bulmasını İSTEMİYORUZ.
    # (Eğer LabReport Pydantic modelinde patient_age ve patient_gender varsa, 
    # LLM onları boş (None) bırakacak, biz aşağıda dolduracağız)
    instruction = """You are an expert clinical data extraction assistant. 
    Analyze the provided unstructured laboratory report text and extract the data strictly into the requested JSON format.

    Map the extracted information to the following fields:

    **Top-Level Fields:**
    1. is_valid_report (boolean): Set to true ONLY IF the text is a genuine medical laboratory report (blood, urine, biochemistry, etc.). Otherwise, set to false.
    2. parameters (list): A list containing every lab test parameter found in the report.

    **For EACH item in the 'parameters' list, extract:**
    - name (string): The short name or code of the test (e.g., WBC, GLU, HGB, PLT).
    - value (float): The actual test result numeric value.
    - unit (string): The unit of measurement (e.g., mg/dL, 10^3/uL, g/dL).
    - ref_min (float): The LOWER bound of the hospital's reference/normal range.
    - ref_max (float): The UPPER bound of the hospital's reference/normal range.
    - flag (string): Compare the 'value' against 'ref_min' and 'ref_max'. Assign 'H' (High), 'L' (Low), or 'N' (Normal).

    Your output must be ONLY a valid JSON object matching this exact schema. Do not add any conversational text."""

    # İPUCU: LLM'e referans aralıklarını doğru bulması için hastanın yaş ve cinsiyetini BİLGİ olarak veriyoruz, 
    # ama ondan bunu geri ayıklamasını istemiyoruz.
    context_hint = f"Note: The patient is a {patient_age} year old {patient_gender}. Use this for context if reference ranges depend on demographics."

    message = HumanMessage(
        content=f"{instruction}\n\n{context_hint}\n\nRAPOR METNİ:\n{raw_lab_text}"
    )
    
    try:
        # LLM sadece tahlil değerlerini ve raporun geçerli olup olmadığını bulur
        extracted_data: LabReport = extractor_llm.invoke([message])
        
        # if not getattr(extracted_data, 'is_valid_report', False):
        #     print("⚠️ [UYARI] Yüklenen belge geçerli bir tahlil raporu değil!")
        #     return {"lab_data": None, "is_valid": False}
            
        # 3. KESİN VERİLERİ ENJEKTE EDİYORUZ (Ground Truth Injection)
        # LLM'in çıkardığı parametrelere, kendi veritabanımızdaki %100 doğru yaş ve cinsiyeti ekliyoruz.
        # (Not: Eğer LabReport Pydantic modelinde bu alanlar varsa atama yapıyoruz)
        if hasattr(extracted_data, 'patient_age'):
            extracted_data.patient_age = patient_age
        if hasattr(extracted_data, 'patient_gender'):
            extracted_data.patient_gender = patient_gender
        if hasattr(extracted_data,'blood_type'):
            extracted_data.patient_blood_type = blood_type

        print(f"✅ Başarıyla çıkarılan parametre sayısı: {len(extracted_data.parameters)}")
        
        # Test
        if extracted_data.parameters:
            first_param = extracted_data.parameters[0]
            print(f"🔍 Örnek: {first_param.name} = {first_param.value} {first_param.unit} (Normal: {first_param.ref_min}-{first_param.ref_max})")
        

        print(f""" lab_data : {extracted_data}""")

        print("\n🩸 [MLP CONTROL] SON")


        return {
            "lab_data": extracted_data, 
            "lab_is_valid": True
        }
        
    except Exception as e:
        print(f"🚨 [HATA] Veri çıkarma başarısız: {e}")
        return {"lab_data": None, "is_valid": False}