from fastapi import FastAPI, HTTPException
import uvicorn
from src.api.contract.contract import AgentRequest, AgentResponse
from src.graph.workflow import app as medical_graph 
import json
from pathlib import Path

# ==========================================
# 📂 YOL BULUCU (PATH RESOLVER) AYARLARI
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

IMAGE_DIR = BASE_DIR / "data" / "resource_db" / "images"
DOC_DIR = BASE_DIR / "data" / "resource_db" / "documents"

def get_absolute_image_path(filename: str | None) -> str | None:
    if not filename:
        return None
    clean_filename = Path(filename).name
    return str(IMAGE_DIR / clean_filename)

def get_absolute_doc_path(filename: str | None) -> str | None:
    if not filename:
        return None
    clean_filename = Path(filename).name
    return str(DOC_DIR / clean_filename)

# ==========================================
# 🚀 FASTAPI UYGULAMASI
# ==========================================

app = FastAPI(title="Medical AI CDSS Agent API")

@app.post("/api/agent/chat", response_model=AgentResponse)
async def consult_agent(request: AgentRequest):
    try:
        print('*' * 50)
        
        safe_image_path = get_absolute_image_path(request.imageUrl)
        safe_doc_path = get_absolute_doc_path(request.documentUrl)

        initial_state = {
            "message_content": request.messageContent,
            "image_url": safe_image_path,   
            "document_url": safe_doc_path,  
            "chief_complaint": request.chiefComplaint,
            
            "patient_age": request.patientAge,
            "patient_gender": request.patientGender,
            "blood_type": request.bloodType,
            "chronic_diseases": request.chronicDiseases,
            "allergies": request.allergies,
            "current_medications": request.currentMedications,
            
            "chat_history": [{"role": m.role, "content": m.content} for m in request.chatHistory],
            
            "active_branches": [],
            "status": "PROCESSING",
            "retrieval_retry_count": 0,
            "conflict_retry_count": 0,
            "retrieved_docs": []
        }

        print("\n--- INITIAL STATE ---")
        print(json.dumps(initial_state, indent=4, ensure_ascii=False))
        print("---------------------\n")

        # 2. LANGGRAPH'I ÇALIŞTIR
        final_state = medical_graph.invoke(initial_state)

        print('*' * 50)

        agent_response : AgentResponse = AgentResponse(
            aiMessage=final_state.get("final_report", "Analiz yapılamadı."),
            sources=final_state.get("evidence_links", []),
            
            imagePrediction=final_state.get("image_prediction"),
            imageConfidenceScore=final_state.get("image_confidence"),
            heatmapUrl=final_state.get("grad_cam_path"),
            
            documentPrediction=final_state.get("lab_prediction"),
            documentConfidenceScore=final_state.get("lab_confidence"),
            featureImportance=final_state.get("feature_importance")
        )

        return agent_response

    except Exception as e:
        print(f"🚨 GRAPH ÇALIŞIRKEN HATA OLUŞTU: {e}")
        # 🛡️ DÜZELTME: Java'yı kandırmak yerine, doğrudan HTTP 500 hatası fırlatıyoruz!
        # Java bu hatayı aldığı an veri tabanına kaydetmeyi iptal edecek (Rollback).
        raise HTTPException(
            status_code=500, 
            detail="Yapay zeka analiz sürecinde (LangGraph) beklenmeyen bir hata oluştu."
        )

if __name__ == "__main__":
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)