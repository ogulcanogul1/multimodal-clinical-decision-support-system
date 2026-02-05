# src/config.py
import torch
import os

# Cihaz Ayarı
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Etiketler
LABELS = [
    'Atelectasis', 'Cardiomegaly', 'Effusion', 'Infiltration', 'Mass',
    'Nodule', 'Pneumonia', 'Pneumothorax', 'Consolidation', 'Edema',
    'Emphysema', 'Fibrosis', 'Pleural_Thickening', 'Hernia', 'No Finding'
]

# ImageNet Normalizasyon
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]

# Eğitim Parametreleri
PARAMS = {
    "csv_path": '/kaggle/input/data/Data_Entry_2017.csv',
    "img_dir": '/kaggle/input', 
    "sample_size": 100000, 
    "batch": 32,
    "lr": 1e-4,
    "epochs": 30,
    "freeze_initial": True,
    "unfreeze_at": 5,
    "num_workers": 4 
}

# Pathler
BEST_MODEL_DIR = "./models/best"
MODELS_PATH = "./models/checkpoints"
os.makedirs(BEST_MODEL_DIR, exist_ok=True)
os.makedirs(MODELS_PATH, exist_ok=True)