package com.medicalai.corebackend.dto.request;

import com.medicalai.corebackend.entity.enums.BloodType;
import com.medicalai.corebackend.entity.enums.Gender;
import java.time.LocalDate;
import java.time.LocalDateTime;

public record PatientResponse(
        String id,
        String nationalId,
        String firstName,
        String lastName,
        LocalDate dateOfBirth,
        Gender gender,
        BloodType bloodType,
        String chronicDiseases,
        LocalDateTime createdAt
) {}
