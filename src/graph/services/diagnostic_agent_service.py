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
    
    # 1. Extract Synthesized Data and User Query from State
    context = state.get("fused_clinical_context", {})
    query = state.get("query", "Please analyze my overall health status based on the provided documents.")
    guidance = state.get("resolution_guidance", "")

    lab_anomalies = context.get("Lab_Anomalies", [])
    image_anomalies = context.get("Image_Anomalies", [])
    
    # DÜZELTME 1: Fusion düğümünden gelen metni doğru anahtarla (Literature_Support) çekiyoruz!
    literature_text = context.get("Literature_Support", "No specific medical literature found.")
    
    # 2. Build a Clean Clinical Table for the LLM
    if not lab_anomalies and not image_anomalies:
        clinical_summary = "All provided laboratory and radiological findings are within normal limits. No anomalies detected."
    else:
        clinical_summary = f"🩸 Laboratory Anomalies:\n- " + "\n- ".join(lab_anomalies) if lab_anomalies else "🩸 Laboratory: No data provided or no anomalies detected."
        clinical_summary += f"\n\n📸 Radiological Anomalies:\n- " + "\n- ".join(image_anomalies) if image_anomalies else "\n\n📸 Radiology: No data provided or no anomalies detected."

    # ==========================================
    # 3. CHIEF MEDICAL OFFICER PROMPT 
    # ==========================================
    system_instruction = """You are the Chief Medical Officer and the final analytical engine of an advanced Clinical Decision Support System (CDSS).
You will be provided with the patient's laboratory anomalies, radiological anomalies, and relevant medical literature (RAG) regarding the case.

Your Tasks and Constraints:
1. Holistic Synthesis: Evaluate the provided clinical and radiological findings comprehensively. 
2. Missing Modalities & Limitations: Patients may not provide all types of data. Evaluate ONLY what is provided. Do NOT hallucinate missing tests. If the absence of a specific modality prevents a definitive assessment, explicitly state this limitation and recommend the missing test.
3. Cross-Modality Intelligence: If both laboratory and radiological data are present, act like a medical detective. Identify and explain any clinical correlations between the two sources. If only one source is present, skip this cross-validation.
4. Evidence-Based Medicine: Ground your recommendations in the provided "Medical Literature (RAG)". If the literature is missing or irrelevant, rely on standard medical protocols.
5. Ethical Boundaries: Do not provide a definitive, legally binding diagnosis. Provide risk assessments, differential possibilities, and triage recommendations. Tell the patient exactly which medical specialist they should visit next.
6. Tone & Style: Use a professional, highly scientific, yet empathetic language. Ensure the output is strictly in English.

CLINICAL PICTURE:
{clinical_summary}

MEDICAL LITERATURE (RAG):
{final_retrieved_docs}

{guidance}
Please format your final report strictly using the following structure:
- 📌 Clinical Status Summary
- 🔗 Cross-Modality Findings & Diagnostic Limitations
- 📚 Evidence-Based Evaluation
- 🩺 Recommended Next Steps & Specialist Referrals
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_instruction),
        ("human", "Patient's Query/Complaint: {query}\n\nPlease generate your detailed and professional medical report.")
    ])
    
    try:
        llm = ActiveLLMFactory.diagnostic_llm()
        chain = prompt | llm
        
        # DÜZELTME 2: Promptun beklediği TÜM değişkenleri buraya ekliyoruz!
        response = chain.invoke({
            "clinical_summary": clinical_summary,
            "final_retrieved_docs": literature_text, 
            "guidance": guidance,
            "query": query
        })
        
        final_report = response.content if hasattr(response, 'content') else str(response)
        
    except Exception as e:
        print(f"❌ [DIAGNOSTIC AGENT] LLM Error: {str(e)}")
        final_report = "Due to system overload, the medical report could not be generated."

    print("✅ [DIAGNOSTIC AGENT] Final medical report successfully generated!")
    return {"final_report": final_report}