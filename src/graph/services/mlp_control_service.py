from langchain_core.messages import HumanMessage
from src.graph.model.llm_factory_ollama import OllamaLLMFactory
from src.schemas.node_schemas.gate_keeper_schemas import LabReport
from src.graph.state import GraphState


def mlp_control_service(state: GraphState):
    """Tahlil raporunu ayrıştırır ve yapılandırılmış formata çevirir."""
    print("\n🩸 [MLP CONTROL] Laboratuvar verileri analiz ediliyor...")
    
    # Varsayalım ki bir önceki adımdan PDF'in metni okundu ve state'e eklendi
    raw_lab_text = state.get("raw_document_text", "")

    if raw_lab_text == "":
        return {
            "lab_data": None, 
            "lab_is_valid": False
        }
    
    extractor_llm = OllamaLLMFactory.lab_extractor_llm()
    
    instruction = """You are an expert clinical data extraction assistant. 
    Analyze the provided unstructured laboratory report text and extract the data strictly into the requested JSON format.

    Map the extracted information to the following fields:

    **Top-Level Fields:**
    1. is_valid_report (boolean): Set to true ONLY IF the text is a genuine medical laboratory report (blood, urine, biochemistry, etc.). Otherwise, set to false.
    2. patient_age (integer): The age of the patient if explicitly stated.
    3. patient_gender (string): The gender of the patient. Use 'M' for male, 'F' for female.
    4. parameters (list): A list containing every lab test parameter found in the report.

    **For EACH item in the 'parameters' list, extract:**
    - name (string): The short name or code of the test (e.g., WBC, GLU, HGB, PLT).
    - value (float): The actual test result numeric value.
    - unit (string): The unit of measurement (e.g., mg/dL, 10^3/uL, g/dL).
    - ref_min (float): The LOWER bound of the hospital's reference/normal range.
    - ref_max (float): The UPPER bound of the hospital's reference/normal range.
    - flag (string): Compare the 'value' against 'ref_min' and 'ref_max'. If the report indicates the value is out of range, assign 'H' for High or 'L' for Low. If normal, leave it empty or assign 'N'.

    Your output must be ONLY a valid JSON object matching this exact schema. Do not add any conversational text."""

    message = HumanMessage(
        content=f"{instruction}\n\nRAPOR METNİ:\n{raw_lab_text}"
    )
    
    try:
        # Bütün sihir burada gerçekleşiyor!
        extracted_data: LabReport = extractor_llm.invoke([message])
        
        if not extracted_data.is_valid_report:
            print("⚠️ [UYARI] Yüklenen belge geçerli bir tahlil raporu değil!")
            return {"lab_data": None, "is_valid": False}
            
        print(f"✅ Başarıyla çıkarılan parametre sayısı: {len(extracted_data.parameters)}")
        
        # Test
        if extracted_data.parameters:
            first_param = extracted_data.parameters[0]
            print(f"🔍 Örnek: {first_param.name} = {first_param.value} {first_param.unit} (Normal: {first_param.ref_min}-{first_param.ref_max})")

        return {
            "lab_data": extracted_data, 
            "lab_is_valid": True
        }
        
    except Exception as e:
        print(f"🚨 [HATA] Veri çıkarma başarısız: {e}")
        return {"lab_data": None, "is_valid": False}