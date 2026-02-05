import os
import pandas as pd
import torch
from torch.utils.data import Dataset
from torchvision import transforms
from PIL import Image
from sklearn.model_selection import train_test_split
from src.modules.cnn.chest_xray_project import config

def get_transforms():
    train_tf = transforms.Compose([
        transforms.Resize((256,256)),
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.3, contrast=0.3),
        transforms.ToTensor(),
        transforms.Normalize(config.IMAGENET_MEAN, config.IMAGENET_STD)
    ])
    test_tf = transforms.Compose([
        transforms.Resize((256,256)),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(config.IMAGENET_MEAN, config.IMAGENET_STD)
    ])
    return train_tf, test_tf


def prepare_professional_data(csv_path, sample_size=None):
    combined_data = []

    # 1. NIH
    if os.path.exists(csv_path):
        print("1/3: NIH Dataset yükleniyor...")
        df_nih = pd.read_csv(csv_path)
        df_nih = df_nih[['Image Index', 'Finding Labels']]
        df_nih['Source'] = 'NIH'
        combined_data.append(df_nih)
    else:
        print("NIH CSV dosyası bulunamadı!")

    # 2. PNEUMONIA
    pneumo_dir = '/kaggle/input/chest-xray-pneumonia/chest_xray'
    if os.path.exists(pneumo_dir):
        print("📥 2/3: Pneumonia Dataset taranıyor...")
        pneumo_rows = []
        for split in ['train', 'test', 'val']:
            for label in ['NORMAL', 'PNEUMONIA']:
                path = os.path.join(pneumo_dir, split, label)
                if os.path.exists(path):
                    for img in os.listdir(path):
                        if img.lower().endswith(('.png', '.jpg', '.jpeg')):
                            final_label = 'Pneumonia' if label == 'PNEUMONIA' else 'No Finding'
                            pneumo_rows.append({
                                'Image Index': img, 
                                'Finding Labels': final_label,
                                'Source': 'Pneumonia'
                            })
        if pneumo_rows:
            combined_data.append(pd.DataFrame(pneumo_rows))
            print(f"   -> {len(pneumo_rows)} resim Pneumonia datasetinden eklendi.")

    # 3. CHEXPERT
    chexpert_root = '/kaggle/input/chexpert'
    chexpert_csv = os.path.join(chexpert_root, 'train.csv')
    
    if os.path.exists(chexpert_csv):
        print(f"📥 3/3: CheXpert Dataset bulundu! ({chexpert_csv})")
        df_chex = pd.read_csv(chexpert_csv)
        df_chex = df_chex.fillna(0).replace(-1.0, 0)
        
        print("   -> CheXpert verileri dönüştürülüyor...")
        chex_rows = []
        for _, row in df_chex.head(50000).iterrows():
            raw_path = row['Path']
            if 'train/' in raw_path:
                clean_path = raw_path.split('train/', 1)[1]
                full_path = os.path.join(chexpert_root, 'train', clean_path)
            else:
                full_path = os.path.join(chexpert_root, raw_path)

            labels = []
            if row.get('No Finding', 0) == 1: labels.append('No Finding')
            if row.get('Atelectasis', 0) == 1: labels.append('Atelectasis')
            if row.get('Cardiomegaly', 0) == 1: labels.append('Cardiomegaly')
            if row.get('Edema', 0) == 1: labels.append('Edema')
            if row.get('Consolidation', 0) == 1: labels.append('Consolidation')
            if row.get('Pneumonia', 0) == 1: labels.append('Pneumonia')
            if row.get('Pneumothorax', 0) == 1: labels.append('Pneumothorax')
            if row.get('Pleural Effusion', 0) == 1: labels.append('Effusion') 
            
            final_label_str = "|".join(labels) if labels else "No Finding"
            
            chex_rows.append({
                'Image Index': full_path, 
                'Finding Labels': final_label_str,
                'Source': 'CheXpert'
            })
            
        if chex_rows:
            combined_data.append(pd.DataFrame(chex_rows))
            print(f"   -> {len(chex_rows)} resim CheXpert'ten eklendi.")

    if not combined_data:
        raise ValueError("Hiçbir dataset bulunamadı!")

    df_final = pd.concat(combined_data, ignore_index=True)
    print(f"OPLAM HAVUZ: {len(df_final)} resim.")
    
    # AKILLI ÖRNEKLEME
    if sample_size and sample_size < len(df_final):
        print(f"Akıllı Dengeleme Çalışıyor (Hedef: {sample_size})...")
        df_priority = df_final[df_final['Source'].isin(['Pneumonia', 'CheXpert'])]
        needed = sample_size - len(df_priority)
        
        if needed > 0:
            df_nih_only = df_final[df_final['Source'] == 'NIH']
            df_nih_sample = df_nih_only.sample(n=min(len(df_nih_only), needed), random_state=42)
            df_final = pd.concat([df_priority, df_nih_sample], ignore_index=True)
            print(f"   -> {len(df_priority)} öncelikli veri (Pneumo/Chex) korundu.")
            print(f"   -> {len(df_nih_sample)} NIH verisi eklendi.")
        else:
            df_final = df_priority.sample(sample_size, random_state=42)
            
    df_final = df_final.sample(frac=1, random_state=42).reset_index(drop=True)
    
    train_df, rest_df = train_test_split(df_final, test_size=0.2, random_state=42, shuffle=True)
    val_df, test_df = train_test_split(rest_df, test_size=0.5, random_state=42, shuffle=True)
    
    return train_df, val_df, test_df


class NIHChestDataset(Dataset):
    def __init__(self, df, img_dir, transform=None):
        self.df = df.copy()
        self.img_dir = img_dir 
        self.transform = transform
        self.labels = config.LABELS
        
        print(f"🚀 Dosya haritalama (Sadece NIH ve Pneumonia)...")
        self.path_map = {}
        count = 0
        
        target_dirs = [
            '/kaggle/input/data',                  
            '/kaggle/input/chest-xray-pneumonia'   
        ]
        
        for target_dir in target_dirs:
            if os.path.exists(target_dir):
                print(f"Taranıyor: {target_dir}...")
                for root, dirs, files in os.walk(target_dir):
                    for file in files:
                        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                            self.path_map[file] = os.path.join(root, file)
                            count += 1
                            if count % 10000 == 0:
                                print(f"🔎 Bulunan: {count}...", end='\r')
                        
        print(f"\nHaritalama bitti! {len(self.path_map)} resim hafızada.")

        print("Etiketler işleniyor...")
        for label in self.labels:
            if label not in self.df.columns:
                self.df[label] = self.df['Finding Labels'].astype(str).map(lambda x: 1.0 if label in x else 0.0)
            else:
                self.df[label] = self.df[label].fillna(0).astype(float)

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        img_ref = str(self.df.iloc[idx]['Image Index'])
        if os.path.exists(img_ref):
            img_path = img_ref
        else:
            img_path = self.path_map.get(img_ref)
        
        if img_path is None: 
            image = Image.new('RGB', (224, 224))
        else:
            try:
                image = Image.open(img_path).convert('RGB')
            except:
                image = Image.new('RGB', (224, 224))
            
        label_vector = self.df.iloc[idx][self.labels].values.astype('float32')
        if self.transform: image = self.transform(image)
        return image, torch.tensor(label_vector)