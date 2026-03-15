package com.medicalai.corebackend.dto.request;

import java.util.Map;

public record DocumentAiResultUpdateRequest(
        String mlpPrediction,
        Double confidenceScore,
        Map<String, Object> featureImportance // String yerine Map oldu
) {}
