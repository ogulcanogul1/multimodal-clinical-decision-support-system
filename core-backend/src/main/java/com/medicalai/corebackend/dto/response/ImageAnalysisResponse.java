package com.medicalai.corebackend.dto.response;

import com.medicalai.corebackend.entity.enums.AnalysisType;
import java.time.LocalDateTime;

public record ImageAnalysisResponse(
        String id,
        String consultationId,
        String originalImageUrl,
        AnalysisType analysisType,
        String aiPrediction,
        Double confidenceScore,
        String heatmapUrl,
        Boolean doctorFeedback,
        LocalDateTime createdAt
) {}