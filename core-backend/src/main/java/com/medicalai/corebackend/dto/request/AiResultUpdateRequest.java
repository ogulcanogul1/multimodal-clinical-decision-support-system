package com.medicalai.corebackend.dto.request;

public record AiResultUpdateRequest(
        String aiPrediction,    // Örn: "Pnömoni"
        Double confidenceScore, // Örn: 0.95
        String heatmapUrl       // Opsiyonel: Grad-CAM ısı haritası
) {}
