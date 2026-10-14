import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
import torchxrayvision as xrv
from torchvision import transforms
from PIL import Image
from src.graph.state import GraphState

# ==========================================
# 1. CNN MODEL & CLASS CONFIGURATION
# ==========================================
CNN_CONFIG = {
    "BRAIN": {
        "Brain_Tumor_Specialist": {
            "path": "data/cnn/brain/models/best_brain_model.pth",
            "classes": {0: "Glioma Tümörü", 1: "Menenjiyom Tümörü", 2: "Normal (Tümör Yok)", 3: "Hipofiz Tümörü"},
            "arch": "resnet50"
        }
    },
    "EYE": {
        "Eye_Disease_Specialist": {
            "path": "data/cnn/eye/models/best_eye_disease_model.pth",
            "classes": {0: "Katarakt", 1: "Diyabetik Retinopati", 2: "Glokom", 3: "Normal"},
            "arch": "resnet50"
        }
    },
    "LUNG": {
        "Gatekeeper": {
            "path": "data/cnn/chest/gate_keeper/Gatekeeper_Results/best_gatekeeper.pth",
            "threshold": 0.169751,   # Constrained Recall >=0.94 stratejisi
            "arch": "densenet121_single_logit",
        },
        "Chest_Multilabel": {
            "path": "data/cnn/chest/last_chest_model/multilabel_output/best_multilabel_model.pth",
            # DualHead concat sırası: STABLE(3) + NOISY(4) — indeks sırası kritik!
            "class_names": ["Effüzyon", "Ödem", "Kardiyomegali", "Atelektazi", "Konsolidasyon", "Pnömoni", "Pnömotoraks"],
            "active_classes": ["Effüzyon", "Ödem", "Kardiyomegali", "Konsolidasyon"],
            "thresholds": {   # Max F1 stratejisi
                "Effüzyon":      0.5286,
                "Ödem":          0.6893,
                "Kardiyomegali": 0.8666,
                "Konsolidasyon": 0.8941,
            },
            "arch": "dual_head_xrv",
        },
    }
}

# ==========================================
# 2. LAZY MODEL CACHE (modeller ağır — bir kez yükle)
# ==========================================
_GATEKEEPER_MODEL = None
_CHEST_MODEL = None

# ==========================================
# 3. MODEL MİMARİLERİ
# ==========================================

class DualHeadChestCNN(nn.Module):
    """
    Notebook (training_multilabel4.ipynb) ile birebir aynı mimari.
    State dict yüklemek için sınıf tanımı burada tutulur.
    backbone = xrv DenseNet features
    head_a   = STABLE sınıflar (Effusion, Edema, Cardiomegaly) → 3 logit
    head_b   = NOISY  sınıflar (Atelectasis, Consolidation, Pneumonia, Pneumothorax) → 4 logit
    Toplam çıktı: 7 logit (concat sırası kritik — class_names ile hizalı)
    """
    def __init__(self):
        super().__init__()
        base_model = xrv.models.DenseNet(weights="densenet121-res224-all")
        self.backbone = base_model.features
        self.head_a = nn.Sequential(
            nn.Linear(1024, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(512, 3)
        )
        self.head_b = nn.Sequential(
            nn.Linear(1024, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(512, 4)
        )

    def forward(self, x):
        features = self.backbone(x)
        features = F.relu(features, inplace=True)
        features = F.adaptive_avg_pool2d(features, (1, 1)).view(features.size(0), -1)
        logits_a = self.head_a(features)
        logits_b = self.head_b(features)
        return torch.cat([logits_a, logits_b], dim=1)  # shape [B, 7]


# ==========================================
# 4. IMAGE PREPROCESSING
# ==========================================

def preprocess_image(image_path):
    """BRAIN ve EYE modelleri için ImageNet RGB preprocessing (224x224)."""
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    image = Image.open(image_path).convert('RGB')
    return transform(image).unsqueeze(0)


def preprocess_chest_xrv(image_path):
    """
    Yeni CHEST multi-label modeli için torchxrayvision preprocessing.
    Grayscale + xrv.datasets.normalize (ImageNet normalize DEĞİL).
    Çıktı: Tensor[1, 1, 224, 224]
    """
    img = Image.open(image_path).convert("L")          # Grayscale zorunlu
    arr = np.array(img, dtype=np.float32)              # 0..255 float
    arr = xrv.datasets.normalize(arr, maxval=255, reshape=True)  # (1, 224, 224)
    return torch.from_numpy(arr).unsqueeze(0).float()  # (1, 1, 224, 224)


# ==========================================
# 5. YARDIMCI FONKSİYON (BRAIN/EYE INFERENCE)
# ==========================================

def run_inference(model_path, tensor, dev, arch="resnet50", class_mapping=None):
    """BRAIN ve EYE için 2-class softmax inference. LUNG için kullanılmaz."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")

    num_classes = len(class_mapping) if class_mapping else 2
    state_dict = torch.load(model_path, map_location=dev)

    if arch == "resnet50":
        model = models.resnet50(weights=None)
        num_ftrs = model.fc.in_features
        if "fc.1.weight" in state_dict:
            model.fc = nn.Sequential(nn.Dropout(0.5), nn.Linear(num_ftrs, num_classes))
        else:
            model.fc = nn.Linear(num_ftrs, num_classes)

    elif arch == "densenet121":
        model = models.densenet121(weights=None)
        num_ftrs = model.classifier.in_features
        if "classifier.1.weight" in state_dict:
            model.classifier = nn.Sequential(nn.Dropout(0.5), nn.Linear(num_ftrs, num_classes))
        else:
            model.classifier = nn.Linear(num_ftrs, num_classes)
    else:
        raise ValueError(f"Bilinmeyen mimari: {arch}")

    model.load_state_dict(state_dict)
    model = model.to(dev)
    model.eval()

    with torch.no_grad():
        outputs = model(tensor)
        probabilities = F.softmax(outputs, dim=1)[0]
        confidence, predicted_idx = torch.max(probabilities, 0)
        pred_idx_val = predicted_idx.item()
        conf_val = confidence.item() * 100
        if class_mapping:
            pred_label = class_mapping.get(pred_idx_val, "Unknown")
        else:
            pred_label = "Positive" if pred_idx_val == 1 else "Negative"
        return pred_label, conf_val


# ==========================================
# 6. CHEST MODELLERI LAZY LOADER
# ==========================================

def _get_gatekeeper(model_path, device):
    """Chest gatekeeper modelini lazy yükler ve cache'ler (tek-logit sigmoid)."""
    global _GATEKEEPER_MODEL
    if _GATEKEEPER_MODEL is None:
        print("   🔄 Chest Gatekeeper yükleniyor (ilk çağrı)...")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Gatekeeper model bulunamadı: {model_path}")
        state_dict = torch.load(model_path, map_location=device)
        model = models.densenet121(weights=None)
        model.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(model.classifier.in_features, 1)
        )
        model.load_state_dict(state_dict)
        model = model.to(device)
        model.eval()
        _GATEKEEPER_MODEL = model
        print("   ✅ Chest Gatekeeper yüklendi.")
    return _GATEKEEPER_MODEL


def _get_chest_multilabel(model_path, device):
    """DualHeadChestCNN modelini lazy yükler ve cache'ler."""
    global _CHEST_MODEL
    if _CHEST_MODEL is None:
        print("   🔄 Chest Multi-label modeli yükleniyor (ilk çağrı, XRV ağırlıkları gerekebilir)...")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Chest multi-label model bulunamadı: {model_path}")
        model = DualHeadChestCNN()
        state_dict = torch.load(model_path, map_location=device)
        model.load_state_dict(state_dict, strict=True)
        model = model.to(device)
        model.eval()
        _CHEST_MODEL = model
        print("   ✅ Chest Multi-label modeli yüklendi.")
    return _CHEST_MODEL


# ==========================================
# 7. LANGGRAPH CNN NODE
# ==========================================

def image_analyzer_service(state: GraphState):
    modality = state.get("modality", "OTHER")
    is_valid = state.get("is_valid", False)

    print('*' * 50)
    print("IMAGE_ANALYZER_SERVICE")

    image_path = state.get("image_url")

    if not is_valid or modality == "OTHER" or modality not in CNN_CONFIG or not image_path:
        return {
            "image_analysis_results": {"System_Note": "No valid radiological image detected."},
            "image_prediction": None,
            "image_confidence": None
        }

    print(f"\n📸 [IMAGE ANALYZER] Hedef Organ: {modality} | Modeller başlatılıyor...")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    analysis_results = {}
    primary_prediction = "Unknown"
    primary_confidence = 0.0

    # ==============================================
    # 🌟 GÖĞÜS (LUNG) — YENİ CHEST MODEL MANTIĞI
    # ==============================================
    if modality == "LUNG":
        gk_cfg = CNN_CONFIG["LUNG"]["Gatekeeper"]
        try:
            print("   -> Chest Gatekeeper çalıştırılıyor...")
            gk_model = _get_gatekeeper(gk_cfg["path"], device)

            gk_tensor = preprocess_image(image_path).to(device)  # ImageNet RGB
            with torch.no_grad():
                logit = gk_model(gk_tensor)                       # shape [1, 1]
                sick_prob = torch.sigmoid(logit).item()

            gk_conf_pct = sick_prob * 100
            threshold = gk_cfg["threshold"]

            if sick_prob < threshold:
                print(f"   🟢 Gatekeeper Sonucu: Normal (Sick prob: {gk_conf_pct:.1f}%, eşik: {threshold:.4f}). Multi-label atlanıyor.")
                analysis_results["Lung_General_Status"] = (
                    f"Normal (Sick prob: {gk_conf_pct:.1f}%, threshold: {threshold:.4f})"
                )
                primary_prediction = "Normal Lungs"
                primary_confidence = (1.0 - sick_prob) * 100
            else:
                print(f"   🔴 Gatekeeper Sonucu: Abnormal (Sick prob: {gk_conf_pct:.1f}%). Multi-label modeli çalıştırılıyor...")
                analysis_results["Lung_General_Status"] = (
                    f"Abnormal (Sick prob: {gk_conf_pct:.1f}%)"
                )
                primary_prediction = "Abnormal Lungs (Scanning...)"
                primary_confidence = gk_conf_pct

                ml_cfg = CNN_CONFIG["LUNG"]["Chest_Multilabel"]
                try:
                    ml_model = _get_chest_multilabel(ml_cfg["path"], device)
                    ml_tensor = preprocess_chest_xrv(image_path).to(device)  # Grayscale + XRV normalize

                    with torch.no_grad():
                        probs = torch.sigmoid(ml_model(ml_tensor))[0]        # shape [7]

                    detected = []
                    highest_conf = 0.0
                    for idx, cls in enumerate(ml_cfg["class_names"]):
                        if cls not in ml_cfg["active_classes"]:
                            continue  # Atelectasis / Pneumonia / Pneumothorax logitleri atlanır
                        p = probs[idx].item()
                        th = ml_cfg["thresholds"][cls]
                        if p >= th:
                            pct = p * 100
                            analysis_results[f"Finding_{cls}"] = (
                                f"Detected (Confidence: {pct:.1f}%, threshold: {th:.4f})"
                            )
                            detected.append(cls)
                            print(f"      🚨 {cls}: Tespit edildi ({pct:.1f}%)")
                            if pct > highest_conf:
                                highest_conf = pct
                                primary_prediction = cls
                                primary_confidence = pct

                    if len(detected) == 0:
                        analysis_results["Lung_General_Status"] += (
                            " — but no findings above threshold in active disease set"
                        )
                        print("      ⚠️  Aktif 4 hastalıkta eşik aşılmadı.")
                    elif len(detected) > 1:
                        primary_prediction += f" (+{len(detected)-1} others)"

                except Exception as e:
                    analysis_results["Chest_Multilabel_Error"] = f"Error: {str(e)}"
                    print(f"   ❌ Chest multi-label hatası: {e}")

        except Exception as e:
            analysis_results["Lung_General_Status"] = f"Gatekeeper Error: {str(e)}"
            print(f"   ❌ Gatekeeper hatası: {e}")

    # ==============================================
    # 🧠 BEYİN VE GÖZ İÇİN STANDART MANTIK
    # ==============================================
    elif modality in ["BRAIN", "EYE"]:
        input_tensor = preprocess_image(image_path).to(device)
        models_to_run = CNN_CONFIG[modality]
        for model_name, config in models_to_run.items():
            try:
                pred_label, conf_val = run_inference(
                    config["path"],
                    input_tensor,
                    device,
                    arch=config["arch"],
                    class_mapping=config["classes"]
                )
                analysis_results[model_name] = f"{pred_label} (Confidence: {conf_val:.1f}%)"
                print(f"   -> {model_name}: {pred_label} ({conf_val:.1f}%)")
                primary_prediction = pred_label
                primary_confidence = conf_val
            except Exception as e:
                analysis_results[model_name] = f"Error: {str(e)}"
                print(f"   ❌ ERROR: {e}")

    # --- DÖNGÜLER VE IF'LER BİTTİ. ŞİMDİ GÜVENLE YAZDIRABİLİRİZ ---
    print(f"\nimage_analysis_results : {analysis_results}")
    print(f"image_prediction : {primary_prediction}")
    print(f"image_confidence : {float(primary_confidence)}\n")
    print("✅ Image analysis complete!")

    # JAVA'NIN VE DİĞER FONKSİYONLARIN BEKLEDİĞİ STATE DÖNÜLÜYOR
    return {
        "image_analysis_results": analysis_results,
        "image_prediction": primary_prediction,
        "image_confidence": float(primary_confidence)
    }
