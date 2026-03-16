import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
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
            "classes": {0: "Glioma Tumor", 1: "Meningioma Tumor", 2: "Normal (No Tumor)", 3: "Pituitary Tumor"},
            "arch": "resnet50"
        }
    },
    "EYE": {
        "Eye_Disease_Specialist": {
            "path": "data/cnn/eye/models/best_eye_disease_model.pth", 
            "classes": {0: "Cataract", 1: "Diabetic Retinopathy", 2: "Glaucoma", 3: "Normal"},
            "arch": "resnet50"
        }
    },
    "LUNG": {
        "Gatekeeper": {
            "path": "data/cnn/best_lung_gatekeeper_model.pth",
            "classes": {0: "Normal", 1: "Abnormal (Disease Detected)"},
            "arch": "densenet121"
        },
        "Specialists": {
            "Atelectasis": {"path": "data/cnn/best_Atelectasis_model.pth", "arch": "densenet121"},
            "Cardiomegaly": {"path": "data/cnn/best_Cardiomegaly_model.pth", "arch": "densenet121"},
            "Consolidation": {"path": "data/cnn/best_Consolidation_model.pth", "arch": "densenet121"},
            "Edema": {"path": "data/cnn/best_Edema_model.pth", "arch": "densenet121"},
            "Effusion": {"path": "data/cnn/best_Effusion_model.pth", "arch": "densenet121"},
            "Pneumonia": {"path": "data/cnn/best_Pneumonia_model.pth", "arch": "densenet121"},
            "Pneumothorax": {"path": "data/cnn/best_Pneumothorax_model.pth", "arch": "densenet121"}
        }
    }
}

# ==========================================
# 2. IMAGE PREPROCESSING
# ==========================================
def preprocess_image(image_path):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    image = Image.open(image_path).convert('RGB')
    return transform(image).unsqueeze(0)

# ==========================================
# 3. YARDIMCI FONKSİYON (INFERENCE)
# ==========================================
def run_inference(model_path, tensor, dev, arch="resnet50", class_mapping=None):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")

    # Sınıf sayısını bul (Eğer verilmemişse default 2'dir: Positive/Negative)
    num_classes = len(class_mapping) if class_mapping else 2

    # 1. Önce ağırlıkları (Sözlüğü) yüklüyoruz ki içine bakıp iskeleti ona göre kuralım
    state_dict = torch.load(model_path, map_location=dev)

    # --- 2. İSKELETİ (MİMARİYİ) OLUŞTUR ---
    if arch == "resnet50":
        # Uyarıları gizlemek için pretrained=False yerine weights=None kullanıyoruz
        model = models.resnet50(weights=None) 
        num_ftrs = model.fc.in_features
        
        # Eğitilen modelin son katmanının yapısına bakıyoruz (Dropout var mı?)
        if "fc.1.weight" in state_dict:
            model.fc = nn.Sequential(
                nn.Dropout(0.5),
                nn.Linear(num_ftrs, num_classes)
            )
        else:
            model.fc = nn.Linear(num_ftrs, num_classes)
            
    elif arch == "densenet121":
        model = models.densenet121(weights=None)
        num_ftrs = model.classifier.in_features
        
        # Eğitilen modelin son katmanının yapısına bakıyoruz (Dropout var mı?)
        if "classifier.1.weight" in state_dict:
            model.classifier = nn.Sequential(
                nn.Dropout(0.5),
                nn.Linear(num_ftrs, num_classes)
            )
        else:
            model.classifier = nn.Linear(num_ftrs, num_classes)
    else:
        raise ValueError(f"Bilinmeyen mimari: {arch}")

    # --- 3. AĞIRLIKLARI İSKELETE GİYDİR VE ÇALIŞTIR ---
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
# 4. LANGGRAPH CNN NODE
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
    
    print(f"\n📸 [IMAGE ANALYZER] Target Organ: {modality} | Initializing Models...")
    
    input_tensor = preprocess_image(image_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    input_tensor = input_tensor.to(device)
    
    analysis_results = {}
    primary_prediction = "Unknown"
    primary_confidence = 0.0

    # ==============================================
    # 🌟 GÖĞÜS (LUNG) İÇİN ÖZEL GATEKEEPER MANTIĞI
    # ==============================================
    if modality == "LUNG":
        gatekeeper_config = CNN_CONFIG["LUNG"]["Gatekeeper"]
        try:
            print("   -> Running Lung Gatekeeper...")
            pred_label, conf_val = run_inference(
                gatekeeper_config["path"], 
                input_tensor, 
                device, 
                arch=gatekeeper_config["arch"], 
                class_mapping=gatekeeper_config["classes"]
            )
            
            if pred_label == "Normal":
                print(f"   🟢 Gatekeeper Result: Normal (Confidence: {conf_val:.1f}%). Skipping specialists.")
                analysis_results["Lung_General_Status"] = f"Normal (Confidence: {conf_val:.1f}%)"
                primary_prediction = "Normal Lungs"
                primary_confidence = conf_val
            else:
                print(f"   🔴 Gatekeeper Result: Abnormal (Confidence: {conf_val:.1f}%). Running 7 Specialists...")
                analysis_results["Lung_General_Status"] = f"Abnormal (Confidence: {conf_val:.1f}%)"
                primary_prediction = "Abnormal Lungs (Scanning...)" 
                primary_confidence = conf_val
                
                specialists = CNN_CONFIG["LUNG"]["Specialists"]
                highest_spec_conf = 0.0
                detected_diseases = []
                
                for spec_name, spec_config in specialists.items():
                    try:
                        spec_pred, spec_conf = run_inference(
                            spec_config["path"], 
                            input_tensor, 
                            device, 
                            arch=spec_config["arch"]
                        )
                        if spec_pred == "Positive":
                            analysis_results[f"Finding_{spec_name}"] = f"Detected (Confidence: {spec_conf:.1f}%)"
                            detected_diseases.append(spec_name)
                            print(f"      🚨 {spec_name}: Detected ({spec_conf:.1f}%)")
                            
                            if spec_conf > highest_spec_conf:
                                highest_spec_conf = spec_conf
                                primary_prediction = spec_name 
                                primary_confidence = spec_conf
                    except Exception as e:
                        analysis_results[f"Finding_{spec_name}"] = f"Error: {str(e)}"
                
                if len(detected_diseases) > 1:
                    primary_prediction += f" (+{len(detected_diseases)-1} others)"
                    
        except Exception as e:
            analysis_results["Lung_General_Status"] = f"Gatekeeper Error: {str(e)}"

    # ==============================================
    # 🧠 BEYİN VE GÖZ İÇİN STANDART MANTIK
    # ==============================================
    elif modality in ["BRAIN", "EYE"]:
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
                
                # SÖZLÜĞE KAYDET!
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