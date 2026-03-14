package com.medicalai.corebackend.dto.response;

import com.medicalai.corebackend.entity.enums.ConsultationStatus;
import java.time.LocalDateTime;

public record ConsultationResponse(
        String id,
        String patientId,
        String patientFullName,
        String doctorId,
        String doctorFullName,
        ConsultationStatus status,
        LocalDateTime createdAt
) {}
