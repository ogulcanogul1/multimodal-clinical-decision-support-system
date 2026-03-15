from fastapi import FastAPI, HTTPException
import uvicorn
from src.api.contract.contract import AgentRequest, AgentResponse
from src.graph.workflow import app as medical_graph 

app = FastAPI(title="Medical AI CDSS Agent API")

@app.post("/api/agent/chat", response_model=AgentResponse)
async def consult_agent(request: AgentRequest):
    try:
        # 1. BAŞLANGIÇ DURUMUNU (INITIAL STATE) OLUŞTUR
        # Java'dan gelen camelCase değişkenleri Python'ın snake_case GraphState yapısına atıyoruz
        initial_state = {
            "message_content": request.messageContent,
            "image_url": request.imageUrl,
            "document_url": request.documentUrl,
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

        # 2. LANGGRAPH'I ÇALIŞTIR (INVOKE)
        final_state = medical_graph.invoke(initial_state)

        # 3. GRAPH'TAN ÇIKAN SONUCU JAVA'YA PAKETLE
        return AgentResponse(
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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)