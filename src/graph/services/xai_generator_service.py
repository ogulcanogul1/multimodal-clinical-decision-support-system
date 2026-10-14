import os
import uuid
import torch
import torch.nn as nn
import numpy as np
from PIL import Image
from pytorch_grad_cam import GradCAMPlusPlus
from pytorch_grad_cam.utils.image import show_cam_on_image
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
import torchvision.models as models

from src.graph.state import GraphState
from src.graph.services.image_analyzer_service import (
    CNN_CONFIG,
    DualHeadChestCNN,
    preprocess_image,
    preprocess_chest_xrv,
    _get_gatekeeper,
    _get_chest_multilabel,
)
from src.core.config import Config
from src import logger

HEATMAP_DIR = str(Config.HEATMAP_DIR)


def xai_generator_service(state: GraphState) -> dict:
    modality = state.get("modality")
    is_valid = state.get("is_valid", False)
    image_path = state.get("image_url")
    prediction = state.get("image_prediction")

    print('\n' + '*' * 50)
    print("XAI_GENERATOR_SERVICE")

    # Erken çıkışlar
    if not (is_valid and image_path and modality in {"BRAIN", "EYE", "LUNG"}):
        print("⏭️ [XAI] Geçerli medikal görüntü yok veya modality desteklenmiyor. Atlanıyor.")
        return {"grad_cam_path": None}

    if not prediction or "Normal" in prediction:
        print(f"⏭️ [XAI] Tahmin normal ({prediction!r}). Heatmap üretilmiyor.")
        return {"grad_cam_path": None}

    print(f"🔥 [XAI] Grad-CAM başlatılıyor — Modality: {modality} | Tahmin: {prediction}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    heatmap_path = None

    try:
        os.makedirs(HEATMAP_DIR, exist_ok=True)
        output_filename = uuid.uuid4().hex + ".png"
        output_path = os.path.join(HEATMAP_DIR, output_filename)

        if modality == "BRAIN":
            cfg = CNN_CONFIG["BRAIN"]["Brain_Tumor_Specialist"]
            target_idx = _class_idx_from_label(prediction, cfg["classes"])
            heatmap_path = _gradcam_resnet50(
                model_path=cfg["path"],
                image_path=image_path,
                target_class=target_idx,
                output_path=output_path,
                device=device,
                num_classes=len(cfg["classes"]),
            )

        elif modality == "EYE":
            cfg = CNN_CONFIG["EYE"]["Eye_Disease_Specialist"]
            target_idx = _class_idx_from_label(prediction, cfg["classes"])
            heatmap_path = _gradcam_resnet50(
                model_path=cfg["path"],
                image_path=image_path,
                target_class=target_idx,
                output_path=output_path,
                device=device,
                num_classes=len(cfg["classes"]),
            )

        elif modality == "LUNG":
            target_logit_idx = _lung_target_index(prediction)
            heatmap_path = _gradcam_chest_multilabel(
                image_path=image_path,
                target_logit_idx=target_logit_idx,
                output_path=output_path,
                device=device,
            )

        if heatmap_path:
            print(f"✅ [XAI] Heatmap üretildi: {heatmap_path}")
        else:
            print("⚠️ [XAI] Heatmap üretilemedi (None döndü).")

    except Exception as e:
        logger.warning(f"[XAI] Grad-CAM üretimi başarısız: {e}")
        print(f"❌ [XAI] Hata: {e}")
        heatmap_path = None

    return {"grad_cam_path": heatmap_path}


# ==========================================
# YARDIMCI FONKSİYONLAR
# ==========================================

def _class_idx_from_label(label: str, classes_dict: dict) -> int:
    """
    CNN_CONFIG'deki {idx: label_str} sözlüğünü ters çevirip label → index döner.
    '(+N others)' suffix temizliği yapılır.
    """
    clean_label = label.split(" (+")[0].strip()
    for idx, lbl in classes_dict.items():
        if lbl.lower() == clean_label.lower():
            return idx
    return 0  # fallback: ilk sınıf


def _lung_target_index(prediction: str) -> int:
    """
    LUNG multi-label için logit index hesaplar.
    Chest_Multilabel.class_names listesinde tahmin etiketini arar.
    """
    class_names = CNN_CONFIG["LUNG"]["Chest_Multilabel"]["class_names"]
    clean_pred = prediction.split(" (+")[0].strip()
    try:
        return class_names.index(clean_pred)
    except ValueError:
        return 0


def _gradcam_resnet50(
    model_path: str,
    image_path: str,
    target_class: int,
    output_path: str,
    device: torch.device,
    num_classes: int,
) -> str | None:
    """ResNet-50 için Grad-CAM üretir ve dosyaya kaydeder."""
    if not os.path.exists(model_path):
        logger.warning(f"[XAI] Model bulunamadı: {model_path}")
        return None

    state_dict = torch.load(model_path, map_location=device)
    model = models.resnet50(weights=None)
    num_ftrs = model.fc.in_features
    if "fc.1.weight" in state_dict:
        model.fc = nn.Sequential(nn.Dropout(0.5), nn.Linear(num_ftrs, num_classes))
    else:
        model.fc = nn.Linear(num_ftrs, num_classes)
    model.load_state_dict(state_dict)
    model = model.to(device)
    model.eval()

    input_tensor = preprocess_image(image_path).to(device)
    target_layers = [model.layer4[-1]]

    with GradCAMPlusPlus(model=model, target_layers=target_layers) as cam:
        targets = [ClassifierOutputTarget(target_class)]
        grayscale_cam = cam(input_tensor=input_tensor, targets=targets,
                            aug_smooth=True, eigen_smooth=True)[0]

    rgb_img = _load_rgb_float(image_path)
    visualization = show_cam_on_image(rgb_img, grayscale_cam, use_rgb=True)
    Image.fromarray(visualization).save(output_path)
    return os.path.basename(output_path)


def _gradcam_chest_multilabel(
    image_path: str,
    target_logit_idx: int,
    output_path: str,
    device: torch.device,
) -> str | None:
    """DualHeadChestCNN için Grad-CAM üretir."""
    cfg = CNN_CONFIG["LUNG"]["Chest_Multilabel"]
    if not os.path.exists(cfg["path"]):
        logger.warning(f"[XAI] Chest model bulunamadı: {cfg['path']}")
        return None

    model = _get_chest_multilabel(cfg["path"], device)
    model.eval()

    input_tensor = preprocess_chest_xrv(image_path).to(device)

    # xrv DenseNet son feature block (backbone = base_model.features, notebook ile aynı)
    target_layers = [model.backbone.denseblock4]

    # Multi-output için custom target: ilgili logit index
    class MultiOutputTarget:
        def __init__(self, idx):
            self.idx = idx
        def __call__(self, output):
            return output[:, self.idx]

    with GradCAMPlusPlus(model=model, target_layers=target_layers) as cam:
        grayscale_cam = cam(
            input_tensor=input_tensor,
            targets=[MultiOutputTarget(target_logit_idx)],
            aug_smooth=True,
            eigen_smooth=True,
        )[0]

    # Grayscale giriş → 3 kanal float RGB'ye çevir
    rgb_img = _load_rgb_float(image_path)
    visualization = show_cam_on_image(rgb_img, grayscale_cam, use_rgb=True)
    Image.fromarray(visualization).save(output_path)
    return os.path.basename(output_path)


def _load_rgb_float(image_path: str) -> np.ndarray:
    """PIL görüntüyü [0,1] float32 RGB numpy array'e dönüştürür (show_cam_on_image için)."""
    img = Image.open(image_path).convert("RGB").resize((224, 224))
    return np.array(img, dtype=np.float32) / 255.0
