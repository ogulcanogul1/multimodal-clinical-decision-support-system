"""
Standalone XAI tanılama + kıyaslama testi: beyin MR → inference → Grad-CAM karşılaştırması

Çalıştırma (proje kökünden):
    python -m src.test_xai_brain

Çıktı (data/resource_db/heatmaps/ altında):
    brain_gradcam.png          — standart GradCAM
    brain_gradcam_pp.png       — GradCAM++ (genellikle daha keskin)
    brain_gradcam_smooth.png   — GradCAM + aug_smooth + eigen_smooth
    brain_gradcam_pp_smooth.png— GradCAM++ + aug_smooth + eigen_smooth (önerilen)
    brain_raw_cam.png          — ham heatmap (overlay yok, sorun tespiti için)
"""

import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import numpy as np
import torch
import torch.nn as nn
import torchvision.models as models
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
from pytorch_grad_cam import GradCAM, GradCAMPlusPlus
from pytorch_grad_cam.utils.image import show_cam_on_image
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

# ──────────────────────────────────────────
# TEST PARAMETRELERİ
# ──────────────────────────────────────────
IMAGE_PATH  = "data/resource_db/images/f5dfef8b-caf6-4474-98fb-a428022c8ea6.png"
MODEL_PATH  = "data/cnn/brain/models/best_brain_model.pth"
CLASSES     = {0: "Glioma Tumor", 1: "Meningioma Tumor", 2: "Normal (No Tumor)", 3: "Pituitary Tumor"}
OUT_DIR     = "data/resource_db/heatmaps"


# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def _check_files():
    ok = True
    for label, path in [("Görüntü", IMAGE_PATH), ("Model", MODEL_PATH)]:
        if not os.path.exists(path):
            print(f"❌ {label} bulunamadı: {path}")
            ok = False
        else:
            print(f"✅ {label} bulundu: {path}")
    if not ok:
        sys.exit(1)


def _build_model(state_dict: dict, device: torch.device) -> models.ResNet:
    """State-dict'e bakarak fc başlığı seçip modeli döndürür."""
    num_classes = len(CLASSES)
    m = models.resnet50(weights=None)
    num_ftrs = m.fc.in_features
    if "fc.1.weight" in state_dict:
        m.fc = nn.Sequential(nn.Dropout(0.5), nn.Linear(num_ftrs, num_classes))
    else:
        m.fc = nn.Linear(num_ftrs, num_classes)
    m.load_state_dict(state_dict)
    return m.to(device).eval()


def _preprocess(path: str, device: torch.device) -> torch.Tensor:
    """ImageNet normalize, (1, 3, 224, 224) tensor."""
    from torchvision import transforms
    tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225]),
    ])
    return tf(Image.open(path).convert("RGB")).unsqueeze(0).to(device)


def _rgb_float(path: str) -> np.ndarray:
    """[0,1] float32 RGB (224×224) — show_cam_on_image için."""
    return np.array(Image.open(path).convert("RGB").resize((224, 224)),
                    dtype=np.float32) / 255.0


def _run_inference(model: nn.Module, tensor: torch.Tensor) -> tuple[int, str, float]:
    with torch.no_grad():
        probs = torch.softmax(model(tensor), dim=1)[0]
    idx = probs.argmax().item()
    return idx, CLASSES[idx], probs[idx].item() * 100, probs.cpu().numpy()


def _cam_variant(
    cam_cls,
    model: nn.Module,
    tensor: torch.Tensor,
    target_idx: int,
    aug_smooth: bool = False,
    eigen_smooth: bool = False,
) -> np.ndarray:
    """Belirtilen CAM sınıfı ve parametrelerle grayscale_cam döndürür."""
    target_layers = [model.layer4[-1]]
    with cam_cls(model=model, target_layers=target_layers) as cam:
        return cam(
            input_tensor=tensor,
            targets=[ClassifierOutputTarget(target_idx)],
            aug_smooth=aug_smooth,
            eigen_smooth=eigen_smooth,
        )[0]


def _save_overlay(rgb_float: np.ndarray, grayscale: np.ndarray,
                  filename: str, alpha: float = 0.5) -> str:
    """Overlay'i kaydet, tam path döndür."""
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, filename)
    vis = show_cam_on_image(rgb_float, grayscale, use_rgb=True, image_weight=alpha)
    Image.fromarray(vis).save(out)
    return out


def _save_raw_cam(grayscale: np.ndarray, filename: str) -> str:
    """Ham ısı haritasını (jet colormap) kaydet."""
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, filename)
    plt.imsave(out, grayscale, cmap="jet")
    return out


def _print_cam_stats(name: str, g: np.ndarray):
    print(f"   {name:30s} min={g.min():.4f}  max={g.max():.4f}  "
          f"mean={g.mean():.4f}  std={g.std():.4f}")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 65)
    print("  BRAIN XAI TANI TESTİ")
    print("=" * 65)

    _check_files()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n🖥️  Device: {device}")

    # ── Model + state_dict ────────────────────────────────────────────────────
    print("\n--- [1/3] Model yükleniyor ---")
    state_dict = torch.load(MODEL_PATH, map_location=device, weights_only=True)
    model = _build_model(state_dict, device)
    print(f"   fc katmanı : {model.fc}")
    print(f"   state_dict anahtar sayısı : {len(state_dict)}")

    # ── Inference ─────────────────────────────────────────────────────────────
    print("\n--- [2/3] Inference ---")
    tensor  = _preprocess(IMAGE_PATH, device)
    pred_idx, pred_label, confidence, all_probs = _run_inference(model, tensor)
    print(f"🧠 Tahmin  : {pred_label}")
    print(f"📊 Güven   : {confidence:.1f}%")
    print("   Tüm sınıflar:")
    for i, (k, v) in enumerate(CLASSES.items()):
        print(f"     [{k}] {v:<30s} {all_probs[i]*100:.1f}%")

    if "Normal" in pred_label:
        print("\n⚠️  Tahmin Normal → Heatmap üretilir ama anlamlı olmayabilir.")

    # ── Grad-CAM varyantları ──────────────────────────────────────────────────
    print("\n--- [3/3] Grad-CAM varyantları ---")
    rgb = _rgb_float(IMAGE_PATH)

    variants = {
        "GradCAM":            (GradCAM,       False, False),
        "GradCAM++":          (GradCAMPlusPlus, False, False),
        "GradCAM+smooth":     (GradCAM,       True,  True),
        "GradCAM+++smooth":   (GradCAMPlusPlus, True,  True),
    }

    cams = {}
    for name, (cls, aug, eig) in variants.items():
        g = _cam_variant(cls, model, tensor, pred_idx, aug_smooth=aug, eigen_smooth=eig)
        cams[name] = g
        _print_cam_stats(name, g)

    # ── Kayıt ─────────────────────────────────────────────────────────────────
    print("\n--- Dosyalar kaydediliyor ---")
    files = {
        "brain_gradcam.png":           ("GradCAM",          0.5),
        "brain_gradcam_pp.png":        ("GradCAM++",         0.5),
        "brain_gradcam_smooth.png":    ("GradCAM+smooth",    0.45),
        "brain_gradcam_pp_smooth.png": ("GradCAM+++smooth",  0.45),
    }
    for fname, (key, alpha) in files.items():
        p = _save_overlay(rgb, cams[key], fname, alpha=alpha)
        print(f"   💾 {fname}  →  {p}")

    raw_p = _save_raw_cam(cams["GradCAM+++smooth"], "brain_raw_cam.png")
    print(f"   💾 brain_raw_cam.png (ham jet) → {raw_p}")

    # ── Öneri ─────────────────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("✅ Test tamamlandı.")
    print()
    print("  Sırasıyla karşılaştır:")
    print("  1. brain_gradcam.png          ← baseline")
    print("  2. brain_gradcam_pp.png       ← GradCAM++ (genellikle daha keskin)")
    print("  3. brain_gradcam_pp_smooth.png← ÖNERİLEN — smoothing + eigen")
    print("  4. brain_raw_cam.png          ← ham heatmap (sorun teşhisi için)")
    print()

    # Ek uyarılar
    g_best = cams["GradCAM+++smooth"]
    if g_best.max() < 0.1:
        print("⚠️  UYARI: grayscale_cam max < 0.1 — aktivasyon çok zayıf.")
        print("   Muhtemel neden: model bu sınıf için güçlü gradient üretmiyor.")
        print("   Deneme: farklı target_layer (örn. model.layer3[-1]) kullanın.")
    elif g_best.std() < 0.05:
        print("⚠️  UYARI: std < 0.05 — aktivasyon uniform (tüm görüntüye yayılmış).")
        print("   Bu genellikle çok yüksek confidence'ta olur.")
    else:
        print(f"ℹ️  Aktivasyon istatistikleri sağlıklı görünüyor (std={g_best.std():.3f}).")

    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
