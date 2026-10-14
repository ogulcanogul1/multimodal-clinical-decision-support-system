import torch
from PIL import Image

from src.graph.state import GraphState
from src.graph.model.cdss_router_model import CLASSES, DEVICE, EVAL_TRANSFORM, get_router_model
from src.core.config import Config


def image_gatekeeper_service(state: GraphState):
    """Yerel CDSS Router CNN ile görüntünün tıbbi modalitesini belirler."""
    print("*" * 50)
    print("IMAGE_GATEKEEPER_SERVICE".upper())

    image_path = state.get("image_url")
    print(f"image_path : {image_path}")

    if image_path is None:
        return {"modality": "OTHER", "is_valid": False, "vlm_note": "Görüntü yok"}

    try:
        img = Image.open(image_path).convert("RGB")
        tensor = EVAL_TRANSFORM(img).unsqueeze(0).to(DEVICE)  # (1, 3, 224, 224)

        router = get_router_model()
        with torch.no_grad():
            logits = router(tensor)
            probs = torch.softmax(logits, dim=1)[0]

        top_conf: float = probs.max().item()
        top_idx: int = probs.argmax().item()
        predicted: str = CLASSES[top_idx]

        threshold: float = Config.ROUTER_CONFIDENCE_THRESHOLD

        if predicted == "OTHER" or top_conf < threshold:
            modality = "OTHER"
            is_valid = False
        else:
            modality = predicted
            is_valid = True

        vlm_note = f"Yerel router: {predicted} ({top_conf * 100:.1f}% güven)"
        print(f"Router sonucu -> {predicted} | Guven: {top_conf:.3f} | Modalite: {modality} | Gecerli: {is_valid}")

    except Exception as e:
        print(f"Router inference hatasi: {e}")
        modality = "OTHER"
        is_valid = False
        vlm_note = "Router inference hatası"

    print("IMAGE GATEKEEPER SERVICE SON")

    return {
        "modality": modality,
        "is_valid": is_valid,
        "vlm_note": vlm_note,
    }
