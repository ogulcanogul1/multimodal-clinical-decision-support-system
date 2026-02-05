# src/engine.py
import torch
from tqdm import tqdm

def train_one_epoch(model, loader, optimizer, criterion, device):
    model.train()
    running_loss = 0.0
    all_logits = []
    all_labels = []
    
    pbar = tqdm(loader, desc="Training", leave=False)
    for x, y in pbar:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        logits = model(x)
        loss = criterion(logits, y)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
        all_logits.append(logits.detach().cpu())
        all_labels.append(y.detach().cpu())
        
    epoch_loss = running_loss / len(loader)
    return epoch_loss, torch.cat(all_logits), torch.cat(all_labels)

def validate_one_epoch(model, loader, criterion, device):
    model.eval()
    running_loss = 0.0
    all_logits = []
    all_labels = []
    
    with torch.no_grad():
        for x, y in tqdm(loader, desc="Validating", leave=False):
            x, y = x.to(device), y.to(device)
            logits = model(x)
            loss = criterion(logits, y)
            
            running_loss += loss.item()
            all_logits.append(logits.detach().cpu())
            all_labels.append(y.detach().cpu())
            
    epoch_loss = running_loss / len(loader)
    return epoch_loss, torch.cat(all_logits), torch.cat(all_labels)