package com.medicalai.corebackend.dto.response;

import com.medicalai.corebackend.entity.enums.BloodType;
import com.medicalai.corebackend.entity.enums.Gender;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

public record PatientResponse(
        String id,
        String nationalId,
        String firstName,
        String lastName,
        LocalDate dateOfBirth,
        Integer age, // Dinamik hesaplanan yaşı da frontend'e gönderiyoruz!
        Gender gender,
        BloodType bloodType,

        // Frontend ekranda listeleyebilsin diye isimlerini dönüyoruz
        List<String> chronicDiseases,
        List<String> allergies,
        List<String> currentMedications,

        LocalDateTime createdAt
) {}
