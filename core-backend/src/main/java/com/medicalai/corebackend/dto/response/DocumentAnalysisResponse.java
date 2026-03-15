package com.medicalai.corebackend.dto.response;

import com.medicalai.corebackend.entity.enums.DocumentType;

import java.time.LocalDateTime;
import java.util.Map;

public record DocumentAnalysisResponse(
        String id,
        String consultationId,
        String documentUrl,
        DocumentType documentType,
        String mlpPrediction,
        Double confidenceScore,
        Map<String, Object> featureImportance, // String yerine Map oldu
        Boolean doctorFeedback,
        LocalDateTime createdAt
) {}
