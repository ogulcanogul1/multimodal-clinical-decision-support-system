from langchain_core.prompts import ChatPromptTemplate
from src.graph.state import GraphState
# Kendi LLM factory yolunu buraya eklemelisin
from src.graph.model.llm_factory_ollama import OllamaLLMFactory 

def diagnostic_agent_service(state: GraphState):
    """
    Generates a clinical diagnosis and final report using the LLM.
    Evaluates available modalities, detects cross-modality correlations, 
    and points out diagnostic limitations if a modality is missing.
    """
    print("\n👨‍⚕️ [DIAGNOSTIC AGENT] The Chief Medical Officer (LLM) is writing the final report...")
    
    # 1. Extract Synthesized Data and User Query from State
    context = state.get("fused_clinical_context", {})
    query = state.get("query", "Please analyze my overall health status based on the provided documents.")
    
    lab_anomalies = context.get("Lab_Anomalies", [])
    image_anomalies = context.get("Image_Anomalies", [])
    literature = context.get("Literature_Support", "")
    
    # 2. Build a Clean Clinical Table for the LLM
    if not lab_anomalies and not image_anomalies:
        clinical_summary = "All provided laboratory and radiological findings are within normal limits. No anomalies detected."
    else:
        clinical_summary = f"🩸 Laboratory Anomalies:\n- " + "\n- ".join(lab_anomalies) if lab_anomalies else "🩸 Laboratory: No data provided or no anomalies detected."
        clinical_summary += f"\n\n📸 Radiological Anomalies:\n- " + "\n- ".join(image_anomalies) if image_anomalies else "\n\n📸 Radiology: No data provided or no anomalies detected."

    # ==========================================
    # 3. CHIEF MEDICAL OFFICER PROMPT (The Brain of the Architecture)
    # ==========================================
    system_instruction = """You are the Chief Medical Officer and the final analytical engine of an advanced Clinical Decision Support System (CDSS).
You will be provided with the patient's laboratory anomalies, radiological anomalies, and relevant medical literature (RAG) regarding the case.

Your Tasks and Constraints:
1. Holistic Synthesis: Evaluate the provided clinical and radiological findings comprehensively. 
2. Missing Modalities & Limitations: Patients may not provide all types of data (e.g., they might only upload a blood test, or only an X-ray). Evaluate ONLY what is provided. Do NOT hallucinate missing tests. If the absence of a specific modality prevents a definitive assessment (e.g., high WBC is present but no chest X-ray was provided to rule out pneumonia), explicitly state this limitation and recommend the missing test.
3. Cross-Modality Intelligence: If both laboratory and radiological data are present, act like a medical detective. Identify and explain any clinical correlations between the two sources (e.g., high blood glucose correlated with diabetic retinopathy). If only one source is present, skip this cross-validation.
4. Evidence-Based Medicine: Ground your recommendations in the provided "Medical Literature (RAG)". If the literature is missing or irrelevant, rely on standard medical protocols but mention the lack of specific literature support.
5. Ethical Boundaries: Do not provide a definitive, legally binding diagnosis. Provide risk assessments, differential possibilities, and triage recommendations. Tell the patient exactly which medical specialist (e.g., Internal Medicine, Pulmonology, Ophthalmology) they should visit next.
6. Tone & Style: Use a professional, highly scientific, yet empathetic language. Ensure the output is strictly in English.

CLINICAL PICTURE:
{clinical_summary}

MEDICAL LITERATURE (RAG):
{literature}

Please format your final report strictly using the following structure:
- 📌 Clinical Status Summary
- 🔗 Cross-Modality Findings & Diagnostic Limitations (Highlight what is correlated, or what is missing to make a full diagnosis)
- 📚 Evidence-Based Evaluation
- 🩺 Recommended Next Steps & Specialist Referrals
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_instruction),
        ("human", "Patient's Query/Complaint: {query}\n\nPlease generate your detailed and professional medical report.")
    ])
    
    # ==========================================
    # 4. LLM CALL (INFERENCE)
    # ==========================================
    try:
        # Kendi yapına göre LLM'i çağır
        llm = OllamaLLMFactory.diagnostic_llm() 
        chain = prompt | llm
        
        response = chain.invoke({
            "clinical_summary": clinical_summary,
            "literature": literature,
            "query": query
        })
        
        # LangChain objesinden metni çıkar
        final_report = response.content if hasattr(response, 'content') else str(response)
        
    except Exception as e:
        print(f"❌ [DIAGNOSTIC AGENT] LLM Error: {str(e)}")
        final_report = "Due to system overload, the medical report could not be generated. Please consult a healthcare facility directly with your findings."

    print("✅ [DIAGNOSTIC AGENT] Final medical report successfully generated!")
    
    return {"final_report": final_report}