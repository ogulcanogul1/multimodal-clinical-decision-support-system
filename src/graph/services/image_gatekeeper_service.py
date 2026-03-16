import base64
from src.graph.state import GraphState
from langchain_core.messages import HumanMessage
from src.graph.model.model_abstraction import ActiveLLMFactory
from src.graph.model.OpenAI_llm_factory import OpenAILLMFactory

from src.schemas.node_schemas.gate_keeper_schemas import ImageAnalysis

def encode_image(image_path: str):
    """Görüntüyü VLM'in okuyabileceği Base64 formatına dönüştürür."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def image_gatekeeper_service(state: GraphState):
    """Görüntüyü analiz eder ve Pydantic değişkenlerini prompt ile eşleştirir."""
    print('*' * 50)

    print("image_gatekeeper_service".upper())
    image_path = state["image_url"]

    print("image_path : " + image_path)
    if image_path is None:
        return 
    
    vlm = OpenAILLMFactory.image_gatekeeper_llm()
    base64_image = encode_image(image_path)
    
    instruction = """You are a professional medical image classification expert.
    Analyze the provided image and strictly determine the following three parameters:

    1. **modality**: Assign 'BRAIN' if the image is a Brain MRI, 'LUNG' if it is a Chest X-ray, or 'EYE' if it is an Eye fundus/retina image. For undefined or non-medical images, assign 'OTHER'.
    2. **is_high_quality**: Assign True if the image is clear and free from excessive noise, blur, or artifacts that would prevent diagnosis. Otherwise, assign False.
    3. **brief_description**: Provide a technical, one-sentence explanation of the primary anatomical structure or any visible abnormality observed in the image.

    Your output must strictly follow the provided JSON schema based on these variables."""

    message = HumanMessage(
        content=[
            {"type": "text", "text": instruction},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
        ]
    )
    

    # Pydantic objesi olarak yanıtı alıyoruz
    analysis_result: ImageAnalysis = vlm.invoke([message])
    
    print("IMAGE GATEKEEPER SERVICE SON")

    return {
        "modality": analysis_result.modality,
        "is_valid": analysis_result.is_high_quality,
        "vlm_note": analysis_result.brief_description
    }