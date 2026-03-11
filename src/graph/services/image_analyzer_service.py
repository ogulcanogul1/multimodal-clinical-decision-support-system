import os
import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
from src.graph.state import GraphState

# ==========================================
# 1. CNN MODEL & CLASS CONFIGURATION (ENGLISH)
# ==========================================
CNN_CONFIG = {
    "BRAIN": {
        "Brain_Tumor_Specialist": {
            "path": "data/cnn/best_brain_model.pth", 
            # Alphabetical order for: glioma, meningioma, notumor, pituitary
            "classes": {0: "Glioma Tumor", 1: "Meningioma Tumor", 2: "Normal (No Tumor)", 3: "Pituitary Tumor"}
        }
    },
    "EYE": {
        "Eye_Disease_Specialist": {
            "path": "data/cnn/best_eye_model.pth", 
            # Alphabetical order for: cataract, diabetic_retinopathy, glaucoma, normal
            "classes": {0: "Cataract", 1: "Diabetic Retinopathy", 2: "Glaucoma", 3: "Normal"}
        }
    },
    "LUNG": {
        "Gatekeeper": {
            "path": "data/cnn/best_lung_gatekeeper_model.pth",
            "classes": {0: "Normal", 1: "Abnormal (Disease Detected)"} # 0: Sağlıklı, 1: Hasta kabul edildi
        },
        "Specialists": {
            "Atelectasis": {"path": "data/cnn/best_Atelectasis_model.pth"},
            "Cardiomegaly": {"path": "data/cnn/best_Cardiomegaly_model.pth"},
            "Consolidation": {"path": "data/cnn/best_Consolidation_model.pth"},
            "Edema": {"path": "data/cnn/best_Edema_model.pth"},
            "Effusion": {"path": "data/cnn/best_Effusion_model.pth"},
            "Pneumonia": {"path": "data/cnn/best_Pneumonia_model.pth"},
            "Pneumothorax": {"path": "data/cnn/best_Pneumothorax_model.pth"}
        }
    }
}

# ==========================================
# 2. IMAGE PREPROCESSING
# ==========================================
def preprocess_image(image_path):
    """Görüntüyü PyTorch CNN modellerinin beklediği formata (Tensor) sokar."""
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    image = Image.open(image_path).convert('RGB')
    return transform(image).unsqueeze(0)

# ==========================================
# 3. LANGGRAPH CNN NODE
# ==========================================
def image_analyzer_service(state: GraphState):
    modality = state.get("modality", "OTHER")
    is_valid = state.get("is_valid", False)
    image_path = state.get("image_path")
    
    if not is_valid or modality == "OTHER" or modality not in CNN_CONFIG:
        return {"image_analysis_results": {"System_Note": "No valid radiological image detected. CNN analysis skipped."}}
    
    print(f"\n📸 [IMAGE ANALYZER] Target Organ: {modality} | Initializing Models...")
    
    input_tensor = preprocess_image(image_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    input_tensor = input_tensor.to(device)
    
    analysis_results = {}

    # DÜZELTME 1: tensor ve device parametre olarak alındı
    def run_inference(model_path, tensor, dev, class_mapping=None):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")
            
        model = torch.load(model_path, map_location=dev)
        model.eval()
        
        with torch.no_grad():
            outputs = model(tensor)
            probabilities = F.softmax(outputs, dim=1)[0]
            confidence, predicted_idx = torch.max(probabilities, 0)
            
            pred_idx_val = predicted_idx.item()
            conf_val = confidence.item() * 100
            
            # DÜZELTME 2: Return bloğu düzeltildi
            if class_mapping:
                pred_label = class_mapping.get(pred_idx_val, "Unknown")
            else:
                pred_label = "Positive" if pred_idx_val == 1 else "Negative"
                
            return pred_label, conf_val

    # ==============================================
    # 🌟 GÖĞÜS (LUNG) İÇİN ÖZEL GATEKEEPER MANTIĞI
    # ==============================================
    if modality == "LUNG":
        gatekeeper_config = CNN_CONFIG["LUNG"]["Gatekeeper"]
        try:
            print("   -> Running Lung Gatekeeper...")
            pred_label, conf_val = run_inference(gatekeeper_config["path"], input_tensor, device, gatekeeper_config["classes"])
            
            if pred_label == "Normal":
                print(f"   🟢 Gatekeeper Result: Normal (Confidence: {conf_val:.1f}%). Skipping specialists.")
                analysis_results["Lung_General_Status"] = f"Normal (Confidence: {conf_val:.1f}%)"
            else:
                print(f"   🔴 Gatekeeper Result: Abnormal (Confidence: {conf_val:.1f}%). Running 7 Specialists...")
                analysis_results["Lung_General_Status"] = f"Abnormal (Confidence: {conf_val:.1f}%)"
                
                specialists = CNN_CONFIG["LUNG"]["Specialists"]
                for spec_name, spec_config in specialists.items():
                    try:
                        # DÜZELTME: parametreler eklendi
                        spec_pred, spec_conf = run_inference(spec_config["path"], input_tensor, device)
                        if spec_pred == "Positive":
                            analysis_results[f"Finding_{spec_name}"] = f"Detected (Confidence: {spec_conf:.1f}%)"
                            print(f"      🚨 {spec_name}: Detected ({spec_conf:.1f}%)")
                    except Exception as e:
                        analysis_results[f"Finding_{spec_name}"] = f"Error: {str(e)}"
                        
        except Exception as e:
            analysis_results["Lung_General_Status"] = f"Gatekeeper Error: {str(e)}"

    # ==============================================
    # 🧠 BEYİN VE GÖZ İÇİN STANDART MANTIK
    # ==============================================
    else:
        models_to_run = CNN_CONFIG[modality]
        for model_name, config in models_to_run.items():
            try:
                # DÜZELTME: parametreler eklendi
                pred_label, conf_val = run_inference(config["path"], input_tensor, device, config["classes"])
                analysis_results[model_name] = f"{pred_label} (Confidence: {conf_val:.1f}%)"
                print(f"   -> {model_name}: {pred_label} ({conf_val:.1f}%)")
            except Exception as e:
                analysis_results[model_name] = f"Error: {str(e)}"

    print("✅ Image analysis complete!")
    return {"image_analysis_results": analysis_results}