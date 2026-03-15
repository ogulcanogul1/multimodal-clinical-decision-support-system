package com.medicalai.corebackend.dto.request;

public record DocumentAiResultUpdateRequest(
        String mlpPrediction,
        Double confidenceScore,
        String featureImportance // JSON formatında bir String gelecek: "{\"glucose\": 0.8, \"age\": 0.3}"
) {}
