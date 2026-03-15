package com.medicalai.corebackend.dto.request;

import jakarta.validation.constraints.NotBlank;

public record ChatMessageRequest(
        @NotBlank(message = "Mesaj içeriği boş olamaz")
        String messageContent,
        String imageAnalysisId,    // Opsiyonel
        String documentAnalysisId  // Opsiyonel
) {}
