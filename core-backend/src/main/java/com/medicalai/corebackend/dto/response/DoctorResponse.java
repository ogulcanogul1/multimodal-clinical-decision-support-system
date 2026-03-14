package com.medicalai.corebackend.dto.response;

import com.medicalai.corebackend.entity.enums.Specialty;
import java.time.LocalDateTime;

public record DoctorResponse(
        String id,
        String firstName,
        String lastName,
        String email,
        String licenseNumber,
        Specialty specialty,
        LocalDateTime createdAt
) {}
