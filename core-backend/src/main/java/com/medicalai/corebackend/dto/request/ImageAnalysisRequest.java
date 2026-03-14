package com.medicalai.corebackend.dto.request;

import com.medicalai.corebackend.entity.enums.AnalysisType;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record ImageAnalysisRequest(
        @NotBlank(message = "Muayene ID zorunludur")
        String consultationId,

        @NotBlank(message = "Görüntü URL'si zorunludur")
        String originalImageUrl,

        @NotNull(message = "Analiz tipi (XRAY, MRI vb.) zorunludur")
        AnalysisType analysisType
) {}