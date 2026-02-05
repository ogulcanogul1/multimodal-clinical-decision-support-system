# src/utils.py
import os
import random
import numpy as np
import torch
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score
from src.modules.cnn.chest_xray_project import config # config dosyasından değişken çekiyoruz

def seed_everything(seed=42):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def calculate_pos_weights(df, labels):
    pos_counts = df[labels].sum(axis=0)
    neg_counts = len(df) - pos_counts
    weights = neg_counts / (pos_counts + 1e-5)
    weights = weights.replace([float('inf'), np.nan], 1.0)
    return torch.tensor(weights.values, dtype=torch.float).to(config.DEVICE)

def calculate_metrics(logits, labels, loss_value):
    probs = torch.sigmoid(logits).numpy()
    targets = labels.numpy()
    auc_list = []
    for i in range(targets.shape[1]):
        try:
            auc = roc_auc_score(targets[:, i], probs[:, i])
        except:
            auc = 0.5
        auc_list.append(auc)
    
    summary = {'LOSS': loss_value, 'MEAN_AUC': np.mean(auc_list), 'AUC_SCORES': auc_list}
    return summary

def plot_training_metrics(history, class_names, current_epoch):
    fig, axs = plt.subplots(1, 2, figsize=(12, 5))
    axs[0].plot(history['train_loss'], label='Train')
    axs[0].plot(history['val_loss'], label='Val')
    axs[0].set_title(f'Loss (Epoch {current_epoch})'); axs[0].legend()
    axs[1].plot(history['train_auc'], label='Train')
    axs[1].plot(history['val_auc'], label='Val')
    axs[1].set_title(f'Mean AUC (Epoch {current_epoch})'); axs[1].legend()
    plt.tight_layout()
    path = f"metrics_epoch_{current_epoch}.png"
    plt.savefig(path); plt.close()
    return path