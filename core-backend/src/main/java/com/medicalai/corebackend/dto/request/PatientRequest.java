package com.medicalai.corebackend.dto.request;

import com.medicalai.corebackend.entity.enums.BloodType;
import com.medicalai.corebackend.entity.enums.Gender;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import java.time.LocalDate;

public record PatientRequest(
        @NotBlank(message = "TC Kimlik no zorunludur")
        @Size(min = 11, max = 11, message = "TC No 11 hane olmalıdır")
        String nationalId,

        @NotBlank(message = "Ad zorunludur")
        String firstName,

        @NotBlank(message = "Soyad zorunludur")
        String lastName,

        @NotNull(message = "Doğum tarihi zorunludur")
        LocalDate dateOfBirth,

        Gender gender,
        BloodType bloodType,
        String chronicDiseases
) {}