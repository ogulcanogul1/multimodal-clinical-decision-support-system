from fastapi import FastAPI, HTTPException
import uvicorn
from src.api.contract.contract import AgentRequest, AgentResponse, AgentStatus
# SENİN GRAPH DOSYAN: 
# Burası senin 'workflow.compile()' dediğin yerdir.
from src.graph.workflow import app as medical_graph 

app = FastAPI(title="Medical AI CDSS Agent API")

@app.post("/api/consult", response_model=AgentResponse)
async def consult_agent(request: AgentRequest):
    try:
        # 1. BAŞLANGIÇ DURUMUNU (INITIAL STATE) OLUŞTUR
        # Java'dan gelen her şeyi senin GraphState yapına tek tek koyuyoruz
        initial_state = {
            "query": request.query,
            "history": [{"role": m.role, "content": m.content} for m in request.history],
            "image_path": request.image_url,
            "pdf_path": request.pdf_url,
            "raw_document_text": request.patient_context,
            "active_branches": [],
            "status": AgentStatus.PROCESSING,
            "retrieval_retry_count": 0,
            "conflict_retry_count": 0,
            "retrieved_docs": [] # Annotated list olduğu için boş başlıyor
        }

        # 2. İŞTE BURADA ÇALIŞTIRIYORUZ (INVOKE)
        # Bu satır çalıştığı an senin Parser düğümün uyanır, 
        # CNN veya RAG yollarından hangisine gideceğine karar verir.
        # Düğüm düğüm gezer ve en son 'final_report'u doldurur.
        
        final_state = medical_graph.invoke(initial_state)

        # 3. GRAPH'TAN ÇIKAN SONUCU JAVA'YA PAKETLE
        # Artık hayal değil, final_state içindeki gerçek verileri dönüyoruz
        return AgentResponse(
            consultation_id=request.consultation_id,
            status=AgentStatus.SUCCESS if final_state.get("status") == "success" else AgentStatus.FAILED,
            message_content=final_state.get("final_report", "Analiz yapılamadı."),
            evidence_links=final_state.get("evidence_links", {}),
            grad_cam_url=final_state.get("grad_cam_path"),
            feature_importance=final_state.get("feature_importance"),
            gatekeeper_warnings=final_state.get("gatekeeper_notes")
        )

    except Exception as e:
        print(f"HATA OLUŞTU: {e}")
        return AgentResponse(
            consultation_id=request.consultation_id,
            status=AgentStatus.FAILED,
            message_content=final_state.get("final_report", "Analiz yapılamadı."),
            evidence_links=final_state.get("evidence_links", {}),
            grad_cam_url=final_state.get("grad_cam_path",""),
            feature_importance=final_state.get("feature_importance",""),
            gatekeeper_warnings=final_state.get("gatekeeper_notes","")
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)