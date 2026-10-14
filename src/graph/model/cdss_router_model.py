"""
CDSS Router — Yerel Modalite Sınıflandırıcı
Eğitim kodu: data/cnn/chest/cdss_model/cdss_kod.ipynb
Model: ResNet-18, 4 sınıf (BRAIN / LUNG / EYE / OTHER)
"""

import torch
import torch.nn as nn
from torchvision import transforms, models

from src.core.config import Config

CLASSES = ["BRAIN", "LUNG", "EYE", "OTHER"]

EVAL_TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class CDSS_Router(nn.Module):
    """Notebook'taki mimariyle birebir aynı — state_dict uyumu için değiştirme."""

    def __init__(self, num_classes: int = 4):
        super().__init__()
        self.model = models.resnet18(weights=None)
        in_ftrs = self.model.fc.in_features
        self.model.fc = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(in_ftrs, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.model(x)


_router_instance: CDSS_Router | None = None


def get_router_model() -> CDSS_Router:
    """Singleton loader — modeli ilk çağrıda yükler, sonraki çağrılarda önbellekten döner."""
    global _router_instance
    if _router_instance is None:
        model_path = Config.ROUTER_MODEL_PATH
        print(f"CDSS Router yukleniyor: {model_path}")
        router = CDSS_Router(num_classes=len(CLASSES))
        state_dict = torch.load(str(model_path), map_location=DEVICE, weights_only=True)
        router.load_state_dict(state_dict)
        router.to(DEVICE)
        router.eval()
        _router_instance = router
        print(f"CDSS Router hazir | Device: {DEVICE} | Siniflar: {CLASSES}")
    return _router_instance
