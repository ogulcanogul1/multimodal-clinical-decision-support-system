package com.medicalai.corebackend.dto.response;

public record DiseaseResponse(
        Long id,
        String name,
        String icd10Code
) {}
