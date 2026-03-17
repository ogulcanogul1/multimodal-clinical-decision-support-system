import json
from langchain_core.prompts import ChatPromptTemplate
from src.graph.state import GraphState
from src.graph.model.model_abstraction import ActiveLLMFactory
from src.schemas.node_schemas.self_critique import CritiqueOutput

def self_critique_service(state: GraphState):

    print('*' * 50)
    print("\n🕵️‍♂️ [SELF-CRITIQUE] Tıbbi Denetçi raporu güvenlik testinden geçiriyor...")
    
    fused_context = state.get("fused_clinical_context", {})
    final_report = state.get("final_report", "")
    
    # --- MİMARİ DÜZELTME 1: RAG MAKALELERİNİ DENETÇİYE DE VERİYORUZ ---
    final_docs = state.get("final_retrieved_docs", [])
    if final_docs:
        doc_texts = [getattr(doc, 'content', str(doc)) for doc in final_docs]
        literature_text = "\n\n".join(doc_texts)
    else:
        literature_text = "No external medical literature was used."
        
    if not final_report:
        return {"critique_status": "conflict", "critique_feedback": "No final report found."}

    # --- MİMARİ DÜZELTME 2: SİSTEM PROMPTU GÜNCELLENDİ ---
    system_instruction = """You are a pragmatic Senior Medical Reviewer evaluating an AI-generated Doctor's Report.
Compare the 'Raw Clinical Facts' & 'Medical Literature' against the 'Generated Doctor's Report'.

Your primary goal is PATIENT SAFETY. Do NOT nitpick vocabulary, tone, or minor semantic differences (e.g., do not reject the report just because it uses "probable" instead of "suggestive of").

ONLY reject the report (Output status: "conflict") if you find a MAJOR clinical error:
1. Dangerous Hallucination: Inventing a completely new severe disease, allergy, or current medication NOT present in the context. (Reasonable clinical inferences based on the facts are allowed).
2. Fatal Contradiction: Explicitly calling a critically abnormal lab result "normal", or recommending a drug the patient is allergic to.
3. Reckless Action: Recommending an immediate invasive surgery or prescribing dangerous drugs without advising a specialist consultation first. (Note: Stating the AI's high-confidence prediction as the primary diagnosis is ACCEPTABLE as long as specialist follow-up is recommended).

If the report is generally safe, logically follows the facts, and appropriately refers the patient to specialists, DO NOT over-analyze. Set status to "verified" and feedback to "Approved"."""

    human_message = "RAW CLINICAL FACTS:\n{context}\n\nMEDICAL LITERATURE:\n{literature}\n\nGENERATED REPORT:\n{report}"

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_instruction),
        ("human", human_message)
    ])

    try:
        llm = ActiveLLMFactory.critique_llm()
        chain = prompt | llm
        
        critique_result: CritiqueOutput = chain.invoke({
            "context": json.dumps(fused_context, ensure_ascii=False, indent=2),
            "literature": literature_text, # Literatür eklendi!
            "report": final_report
        })
        
        status = critique_result.status.strip().lower()
        feedback = critique_result.feedback
        
        if status not in ["verified", "conflict"]:
            status = "conflict"
            
    except Exception as e:
        print(f"❌ [SELF-CRITIQUE] Hata: {str(e)}")
        status = "conflict"
        feedback = f"Critique failure: {str(e)}"

    # --- MİMARİ KÖPRÜ (ÖLÜ KODLAR TEMİZLENDİ) ---
    if status == "verified":
        print("   ✅ Rapor ONAYLANDI (Verified).")
        print(f"""
critique_status : {status}
critique_feedback : {feedback}
""")
    else:
        print(f"   🚨 Rapor REDDEDİLDİ (Conflict)! Hata: {feedback}")

    # Sayaç artırma işi Conflict Resolver'da olduğu için sadece durumu dönüyoruz
    return {
        "critique_status": status,
        "critique_feedback": feedback,
    }