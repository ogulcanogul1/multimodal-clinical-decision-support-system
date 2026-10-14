from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import uvicorn
from src.api.contract.contract import AgentRequest, AgentResponse
from src.graph.workflow import app as medical_graph
from src.core.config import Config
import json
from pathlib import Path
import os

# ==========================================
# 📂 YOL BULUCU (PATH RESOLVER) AYARLARI
# ==========================================

BASE_DIR = Config.BASE_DIR

IMAGE_DIR = BASE_DIR / "data" / "resource_db" / "images"
DOC_DIR = BASE_DIR / "data" / "resource_db" / "documents"
HEATMAP_DIR = Config.HEATMAP_DIR

# Heatmap dizinini başlangıçta oluştur (StaticFiles mount için şart)
os.makedirs(HEATMAP_DIR, exist_ok=True)

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

# Grad-CAM heatmap'lerini statik dosya olarak servis et
# Frontend: http://localhost:8000/heatmaps/<uuid>.png
app.mount("/heatmaps", StaticFiles(directory=str(HEATMAP_DIR)), name="heatmaps")

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

        # grad_cam_path sadece basename (uuid.png) döner; tam URL'e çevir
        heatmap_basename = final_state.get("grad_cam_path")
        heatmap_url = f"http://localhost:8000/heatmaps/{heatmap_basename}" if heatmap_basename else None

        agent_response : AgentResponse = AgentResponse(
            aiMessage=final_state.get("final_report", "Analiz yapılamadı."),
            sources=final_state.get("evidence_links", []),

            imagePrediction=final_state.get("image_prediction"),
            imageConfidenceScore=final_state.get("image_confidence"),
            heatmapUrl=heatmap_url,

            documentPrediction=final_state.get("lab_prediction"),
            documentConfidenceScore=final_state.get("lab_confidence"),
            featureImportance=final_state.get("feature_importance")
        )

        return agent_response

    except Exception as e:
        print(f"🚨 GRAPH ÇALIŞIRKEN HATA OLUŞTU: {e}")
        
        raise HTTPException(
            status_code=500, 
            detail="Yapay zeka analiz sürecinde (LangGraph) beklenmeyen bir hata oluştu."
        )

if __name__ == "__main__":
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)