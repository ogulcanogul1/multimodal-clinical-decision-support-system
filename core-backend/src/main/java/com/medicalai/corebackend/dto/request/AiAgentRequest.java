package com.medicalai.corebackend.dto.request;

import com.medicalai.corebackend.entity.enums.BloodType;
import com.medicalai.corebackend.entity.enums.Gender;

import java.util.List;

public record AiAgentRequest(
        String consultationId,
        String messageContent,
        String imageUrl,      // ID değil, URL/Path gidiyor!
        String documentUrl,    // ID değil, URL/Path gidiyor!

        // --- KLİNİK BAĞLAM (CLINICAL CONTEXT) ---
        Integer patientAge,
        Gender patientGender,
        BloodType bloodType,
        List<String> chronicDiseases,
        List<String> allergies
) {}
