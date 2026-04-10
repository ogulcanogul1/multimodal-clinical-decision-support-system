package com.medicalai.corebackend.dto.request;

import com.medicalai.corebackend.entity.enums.Specialty;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;

public record DoctorRequest(
        @NotBlank(message = "Ad zorunludur")
        String firstName,

        @NotBlank(message = "Soyad zorunludur")
        String lastName,

        @Email(message = "Geçerli bir email adresi giriniz")
        @NotBlank(message = "Email zorunludur")
        String email,

        @NotBlank(message = "Diploma/Lisans numarası zorunludur")
        @Pattern(regexp = "^LIC-\\d+$", message = "Lisans numarası LIC-{numara} formatında olmalıdır (örn: LIC-12345)")
        String licenseNumber,

        @NotNull(message = "Uzmanlık alanı zorunludur")
        Specialty specialty,

        @NotBlank(message = "Şifre zorunludur")
        String password // Şimdilik ham alıyoruz, Service'de encode edeceğiz
) {}
