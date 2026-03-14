package com.medicalai.corebackend.dto.request;

import jakarta.validation.constraints.NotBlank;

public record ConsultationRequest(
        @NotBlank(message = "Hasta ID zorunludur")
        String patientId,

        @NotBlank(message = "Doktor ID zorunludur")
        String doctorId
) {}
