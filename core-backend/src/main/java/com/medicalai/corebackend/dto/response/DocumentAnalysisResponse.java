package com.medicalai.corebackend.dto.response;

import com.medicalai.corebackend.entity.enums.DocumentType;
import java.time.LocalDateTime;

public record DocumentAnalysisResponse(
        String id,
        String consultationId,
        String documentUrl,
        DocumentType documentType,
        String mlpPrediction,
        Double confidenceScore,
        String featureImportance,
        Boolean doctorFeedback,
        LocalDateTime createdAt
) {}
