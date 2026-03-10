import json
from langchain_core.prompts import ChatPromptTemplate
from src.graph.state import GraphState
from src.graph.model.llm_factory_ollama import OllamaLLMFactory
from src.schemas.node_schemas.self_critique import CritiqueOutput

def self_critique_service(state: GraphState):
    print("\n🕵️‍♂️ [SELF-CRITIQUE] Tıbbi Denetçi raporu güvenlik testinden geçiriyor...")
    
    fused_context = state.get("fused_clinical_context", {})
    final_report = state.get("final_report", "")
    
    if not final_report:
        return {"critique_status": "conflict", "critique_feedback": "No final report found."}

    system_instruction = """You are a strict Medical Quality Assurance (QA) Auditor.
Compare the 'Raw Clinical Facts' against the 'Generated Doctor's Report'.

CRITICAL RULES FOR FAILURE (Output status: "conflict"):
1. Hallucination: Mentioning a disease/anomaly NOT present in the Raw Facts.
2. Contradiction: Calling an abnormal test 'normal' or vice versa.
3. Definitive Diagnosis: Making a definitive legal diagnosis instead of a risk assessment.

If ANY rule is violated, set status to "conflict" and write what needs to be fixed in "feedback".
If the report is 100% safe, accurate, and matches the facts, set status to "verified" and feedback to "Approved"."""

    human_message = "RAW CLINICAL FACTS:\n{context}\n\nGENERATED REPORT:\n{report}"

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_instruction),
        ("human", human_message)
    ])

    try:
        # Factory zaten structured_output gömülü modeli veriyor!
        llm = OllamaLLMFactory.critique_llm()
        chain = prompt | llm
        
        # Sonuç doğrudan Pydantic objesi (CritiqueOutput) olarak gelir
        critique_result: CritiqueOutput = chain.invoke({
            "context": json.dumps(fused_context, ensure_ascii=False, indent=2),
            "report": final_report
        })
        
        status = critique_result.status
        feedback = critique_result.feedback
        
        if status.lower() not in ["verified", "conflict"]:
            status = "conflict"
            
    except Exception as e:
        print(f"❌ [SELF-CRITIQUE] Hata: {str(e)}")
        status = "conflict"
        feedback = f"Critique failure: {str(e)}"

    if status == "verified":
        print("   ✅ Rapor ONAYLANDI (Verified).")
    else:
        print(f"   🚨 Rapor REDDEDİLDİ (Conflict)! Hata: {feedback}")

    return {
        "critique_status": status,
        "critique_feedback": feedback
    }