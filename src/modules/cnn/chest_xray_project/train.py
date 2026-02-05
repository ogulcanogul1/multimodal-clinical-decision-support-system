# train.py
import os
import copy
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import mlflow
from src.modules.cnn.chest_xray_project import config,dataset,model,engine,utils  


def run_pipeline():
    # =====================================================
    # ADIM 1: BAŞLANGIÇ AYARLARI (SETUP)
    # =====================================================
    print("Pipeline Başlatılıyor...")
    utils.seed_everything(42)
    
    # Cihaz ve Parametreleri Yükle
    device = config.DEVICE
    params = config.PARAMS
    print(f"Çalışma Cihazı: {device}")
    print(f"Parametreler: {params}")

    # =====================================================
    # ADIM 2: VERİ HAZIRLIĞI (DATA PREPARATION)
    # =====================================================
    print("\n[2/6] Veri Seti Hazırlanıyor...")
    
    # Transformları Al
    train_tf, test_tf = dataset.get_transforms()
    
    train_df, val_df, test_df = dataset.prepare_professional_data(
        csv_path=params["csv_path"], 
        sample_size=params["sample_size"]
    )
    
    train_ds = dataset.NIHChestDataset(train_df, params["img_dir"], transform=train_tf)
    val_ds   = dataset.NIHChestDataset(val_df, params["img_dir"], transform=test_tf)
    
    # DataLoader'ları Kur
    loader_args = {'batch_size': params["batch"], 'num_workers': params["num_workers"], 'pin_memory': True}
    train_loader = DataLoader(train_ds, shuffle=True, **loader_args)
    val_loader   = DataLoader(val_ds, shuffle=False, **loader_args)
    
    print(f"Veri Hazır! Train: {len(train_ds)}, Val: {len(val_ds)}")

    # =====================================================
    # ADIM 3: MODEL KURULUMU (MODEL INITIALIZATION)
    # =====================================================
    print("\n[3/6] Model İnşa Ediliyor (DenseNet121)...")
    
    cnn_model = model.create_densenet_model(
        num_classes=len(config.LABELS), 
        freeze=params["freeze_initial"]
    ).to(device)
    
    # Sınıf Dengesizliği için Ağırlık Hesapla
    pos_weights = utils.calculate_pos_weights(train_df, config.LABELS)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weights)
    
    # Optimizer ve Scheduler
    optimizer = optim.Adam(filter(lambda p: p.requires_grad, cnn_model.parameters()), lr=params["lr"])
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.1, patience=3)

    # =====================================================
    # ADIM 4: MLFLOW TAKİP SİSTEMİ (TRACKING)
    # =====================================================
    print("\n[4/6] MLflow Bağlantısı Kuruluyor...")
    
    # Merkezi mlruns klasörüne bağlan
    mlflow.set_tracking_uri("file:./mlruns")
    mlflow.set_experiment("Chest_XRay_Training") 
    
    # =====================================================
    # ADIM 5: EĞİTİM DÖNGÜSÜ (TRAINING LOOP)
    # =====================================================
    print("\n[5/6] Eğitim Başlıyor...")
    
    best_auc = 0.0
    best_model_wts = copy.deepcopy(cnn_model.state_dict())
    history = {'train_loss': [], 'val_loss': [], 'train_auc': [], 'val_auc': []}

    # MLflow Run Başlat
    with mlflow.start_run(run_name="DenseNet_Modular_Pipeline_v1"):
        mlflow.log_params(params) 
        
        for epoch in range(params["epochs"]):
            current_epoch = epoch + 1
            
            if params["unfreeze_at"] is not None and epoch == params["unfreeze_at"]:
                print(f"\n[Epoch {current_epoch}] Modelin tüm katmanları açılıyor (Fine-Tuning)...")
                for param in cnn_model.parameters(): param.requires_grad = True
                
                optimizer = optim.Adam(cnn_model.parameters(), lr=params["lr"] * 0.1)

            t_loss, t_logits, t_labels = engine.train_one_epoch(cnn_model, train_loader, optimizer, criterion, device)
            v_loss, v_logits, v_labels = engine.validate_one_epoch(cnn_model, val_loader, criterion, device)
            
            t_metrics = utils.calculate_metrics(t_logits, t_labels, t_loss)
            v_metrics = utils.calculate_metrics(v_logits, v_labels, v_loss)
            
            print(f"Epoch {current_epoch}/{params['epochs']} | "
                  f"Train Loss: {t_metrics['LOSS']:.4f} | Val AUC: {v_metrics['MEAN_AUC']:.4f}")
            
            mlflow.log_metric("train_loss", t_metrics['LOSS'], step=current_epoch)
            mlflow.log_metric("val_loss", v_metrics['LOSS'], step=current_epoch)
            mlflow.log_metric("val_auc", v_metrics['MEAN_AUC'], step=current_epoch)
            
            if v_metrics['MEAN_AUC'] > best_auc:
                best_auc = v_metrics['MEAN_AUC']
                best_model_wts = copy.deepcopy(cnn_model.state_dict())
                print(f"🌟 Yeni En İyi Skor! ({best_auc:.4f})")
            
            if current_epoch % 5 == 0:
                ckpt_path = os.path.join(config.MODELS_PATH, f"ckpt_epoch_{current_epoch}.pth")
                torch.save(cnn_model.state_dict(), ckpt_path)
            
            scheduler.step(v_metrics['MEAN_AUC'])

    # =====================================================
    # ADIM 6: KAYIT VE KAPANIŞ (FINALIZATION)
    # =====================================================
    print("\n[6/6] En İyi Model Kaydediliyor...")
    final_path = os.path.join(config.BEST_MODEL_DIR, "best_model.pth")
    torch.save(best_model_wts, final_path)
    
    print(f"Pipeline Başarıyla Tamamlandı! Model: {final_path}")
    print(f"Final Best AUC: {best_auc:.4f}")

if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as e:
        print(f"❌ Pipeline Hatası: {e}")
        
        import traceback
        traceback.print_exc()