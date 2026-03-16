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

# Klasörlerin kesin (absolute) yollarını belirliyoruz
IMAGE_DIR = BASE_DIR / "data" / "resource_db" / "images"
DOC_DIR = BASE_DIR / "data" / "resource_db" / "documents"

def get_absolute_image_path(filename: str | None) -> str | None:
    if not filename:
        return None
    # Sadece dosya adını alıyoruz (Örn: "123.png")
    clean_filename = Path(filename).name
    # Tam yolu oluşturup string olarak dönüyoruz
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
        
        # --- MİMARİ DÜZELTME: Java'dan gelen isimleri TAM YOLA çeviriyoruz ---
        safe_image_path = get_absolute_image_path(request.imageUrl)
        safe_doc_path = get_absolute_doc_path(request.documentUrl)

        # 1. BAŞLANGIÇ DURUMUNU (INITIAL STATE) OLUŞTUR
        initial_state = {
            "message_content": request.messageContent,
            "image_url": safe_image_path,   # Artık kusursuz "D:/.../images/uuid.png" oldu!
            "document_url": safe_doc_path,  # Artık kusursuz "D:/.../documents/uuid.pdf" oldu!
            "chief_complaint": request.chiefComplaint,
            
            "patient_age": request.patientAge,
            "patient_gender": request.patientGender,
            "blood_type": request.bloodType,
            "chronic_diseases": request.chronicDiseases,
            "allergies": request.allergies,
            "current_medications": request.currentMedications,
            
            # Pydantic objelerini dictionary listesine çeviriyoruz
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

        # 2. LANGGRAPH'I ÇALIŞTIR (INVOKE)
        final_state = medical_graph.invoke(initial_state)

        print('*' * 50)

        agent_response : AgentResponse = AgentResponse(
            aiMessage=final_state.get("final_report", "Analiz yapılamadı."),
            sources=final_state.get("evidence_links", []),
            
            # Görüntü Çıktıları
            imagePrediction=final_state.get("image_prediction"),
            imageConfidenceScore=final_state.get("image_confidence"),
            heatmapUrl=final_state.get("grad_cam_path"),
            
            # Belge Çıktıları
            documentPrediction=final_state.get("lab_prediction"),
            documentConfidenceScore=final_state.get("lab_confidence"),
            featureImportance=final_state.get("feature_importance")
        )

        print(f"""
final_report : {agent_response.aiMessage}

sources : {agent_response.sources}

image_prediction : {agent_response.imagePrediction}

imageConfidenceScore : {agent_response.imageConfidenceScore}

grad_cam_path : {agent_response.heatmapUrl}

lab_prediction : {agent_response.documentPrediction}

lab_confidence : {agent_response.documentConfidenceScore}

feature_importance : {agent_response.featureImportance}
""")

        # 3. GRAPH'TAN ÇIKAN SONUCU JAVA'YA PAKETLE
        return agent_response

    except Exception as e:
        print(f"GRAPH ÇALIŞIRKEN HATA OLUŞTU: {e}")
        # Graph çöktüğü için final_state boş olabilir, bu yüzden güvenli bir hata cevabı dönüyoruz
        return AgentResponse(
            aiMessage="Yapay zeka sunucusunda (LangGraph) beklenmeyen bir hata oluştu. Lütfen sistem yöneticisine başvurun.",
            sources=[],
            imagePrediction=None,
            imageConfidenceScore=None,
            heatmapUrl=None,
            documentPrediction=None,
            documentConfidenceScore=None,
            featureImportance=None
        )

if __name__ == "__main__":
    # Ufak düzeltme: Modül yolunu tam yazmak terminal hatalarını önler
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)