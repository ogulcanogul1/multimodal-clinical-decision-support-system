import torch.nn as nn
from torchvision import models

def create_densenet_model(num_classes=15, freeze=True):
    model = models.densenet121(weights=models.DenseNet121_Weights.IMAGENET1K_V1)
    if freeze:
        for param in model.parameters(): param.requires_grad = False
    in_features = model.classifier.in_features
    model.classifier = nn.Linear(in_features, num_classes)
    return model