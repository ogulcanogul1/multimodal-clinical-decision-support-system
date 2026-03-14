package com.medicalai.corebackend.dto.request;

import com.medicalai.corebackend.entity.enums.Specialty;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record DoctorRequest(
        @NotBlank(message = "Ad zorunludur")
        String firstName,

        @NotBlank(message = "Soyad zorunludur")
        String lastName,

        @Email(message = "Geçerli bir email adresi giriniz")
        @NotBlank(message = "Email zorunludur")
        String email,

        @NotBlank(message = "Diploma/Lisans numarası zorunludur")
        String licenseNumber,

        @NotNull(message = "Uzmanlık alanı zorunludur")
        Specialty specialty,

        @NotBlank(message = "Şifre zorunludur")
        String password // Şimdilik ham alıyoruz, Service'de encode edeceğiz
) {}
