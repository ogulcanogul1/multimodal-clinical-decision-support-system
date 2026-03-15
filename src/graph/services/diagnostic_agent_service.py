from langchain_core.prompts import ChatPromptTemplate
from src.graph.state import GraphState
from src.graph.model.model_abstraction import ActiveLLMFactory

def diagnostic_agent_service(state: GraphState):
    """
    Generates a clinical diagnosis and final report using the LLM.
    Evaluates available modalities, detects cross-modality correlations, 
    and points out diagnostic limitations if a modality is missing.
    """
    print("\n👨‍⚕️ [DIAGNOSTIC AGENT] The Chief Medical Officer (LLM) is writing the final report...")

    retry_count = state.get("conflict_retry_count", 0)

    if retry_count >= 3:
        return {}
    
    # 1. Extract Synthesized Data and State Variables
    context = state.get("fused_clinical_context", {})
    # DÜZELTME: FastAPI'de ismini message_content yapmıştık, geriye dönük uyum için ikisine de bakıyoruz
    query = state.get("message_content") or state.get("query") or "Please analyze my overall health status."
    guidance = state.get("resolution_guidance", "")
    chat_history = state.get("chat_history", [])

    # --- YENİ EKLENEN: HASTA PROFİLİ VE GEÇMİŞİ ---
    patient_profile = context.get("Patient_Profile", {})
    lab_anomalies = context.get("Lab_Anomalies", [])
    image_anomalies = context.get("Image_Anomalies", [])
    literature_text = context.get("Literature_Support", "No specific medical literature found.")
    
    # 2. Build Clean Clinical Tables for the LLM
    
    # A. Hasta Demografisi Formatlama
    profile_summary = f"""
    - Age: {patient_profile.get('Age', 'Unknown')}
    - Gender: {patient_profile.get('Gender', 'Unknown')}
    - Chief Complaint: {patient_profile.get('Chief_Complaint', 'Not specified')}
    - Chronic Diseases: {', '.join(patient_profile.get('Chronic_Diseases', [])) or 'None'}
    - Allergies: {', '.join(patient_profile.get('Allergies', [])) or 'None'}
    - Current Medications: {', '.join(patient_profile.get('Medications', [])) or 'None'}
    """

    # B. Anormallikler Formatlama
    if not lab_anomalies and not image_anomalies:
        clinical_summary = "All provided laboratory and radiological findings are within normal limits. No anomalies detected."
    else:
        clinical_summary = f"🩸 Laboratory Anomalies:\n- " + "\n- ".join(lab_anomalies) if lab_anomalies else "🩸 Laboratory: No anomalies detected."
        clinical_summary += f"\n\n📸 Radiological Anomalies:\n- " + "\n- ".join(image_anomalies) if image_anomalies else "\n\n📸 Radiology: No anomalies detected."

    # C. Sohbet Geçmişi Formatlama (LLM doktorun önceki sorularını bilsin)
    history_text = ""
    if chat_history:
        history_text = "PREVIOUS CONVERSATION HISTORY:\n"
        # Context taşmasın diye sadece son 6 mesajı (3 tur) alıyoruz
        for msg in chat_history[-6:]: 
            role_name = "Doctor" if msg.get("role") in ["DOCTOR", "user"] else "AI Assistant"
            history_text += f"[{role_name}]: {msg.get('content')}\n"

    # ==========================================
    # 3. CHIEF MEDICAL OFFICER PROMPT 
    # ==========================================
    system_instruction = """You are the Chief Medical Officer and the final analytical engine of an advanced Clinical Decision Support System (CDSS).
You will be provided with the patient's demographics, clinical history, laboratory/radiological anomalies, and relevant medical literature (RAG).

Your Tasks and Constraints:
1. Holistic Synthesis: Evaluate the provided clinical and radiological findings comprehensively, keeping the patient's age, gender, and chronic diseases in mind.
2. Missing Modalities & Limitations: Evaluate ONLY what is provided. Do NOT hallucinate missing tests. If the absence of a specific modality prevents a definitive assessment, explicitly state this limitation.
3. Cross-Modality Intelligence: If both laboratory and radiological data are present, act like a medical detective. Identify and explain any clinical correlations between the two sources. 
4. Evidence-Based Medicine: Ground your recommendations in the provided "Medical Literature (RAG)". If the literature is missing, rely on standard medical protocols.
5. Ethical Boundaries: Do not provide a definitive, legally binding diagnosis. Provide risk assessments, differential possibilities, and triage recommendations. Tell the doctor/patient exactly which medical specialist they should consult next.
6. Tone & Style: Use a professional, highly scientific, yet empathetic language. Ensure the output is strictly in English.

PATIENT DEMOGRAPHICS & HISTORY:
{profile_summary}

CLINICAL PICTURE (ANOMALIES):
{clinical_summary}

MEDICAL LITERATURE (RAG):
{final_retrieved_docs}

{guidance}
Please format your final report strictly using the following structure:
- Clinical Status Summary
- Cross-Modality Findings & Diagnostic Limitations
- Evidence-Based Evaluation
- Recommended Next Steps & Specialist Referrals
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_instruction),
        ("human", "{history_text}\nDoctor's Current Query/Instruction: {query}\n\nPlease generate your detailed and professional medical report.")
    ])
    
    try:
        llm = ActiveLLMFactory.diagnostic_llm()
        chain = prompt | llm
        
        # Bütün eksik parçaları prompt'a gönderiyoruz
        response = chain.invoke({
            "profile_summary": profile_summary,
            "clinical_summary": clinical_summary,
            "final_retrieved_docs": literature_text, 
            "guidance": guidance,
            "history_text": history_text,
            "query": query
        })
        
        final_report = response.content if hasattr(response, 'content') else str(response)
        
    except Exception as e:
        print(f"❌ [DIAGNOSTIC AGENT] LLM Error: {str(e)}")
        final_report = "Due to system overload, the medical report could not be generated."

    print("✅ [DIAGNOSTIC AGENT] Final medical report successfully generated!")
    return {"final_report": final_report}