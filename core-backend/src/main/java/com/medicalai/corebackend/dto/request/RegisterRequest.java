package com.medicalai.corebackend.dto.request;

import com.medicalai.corebackend.entity.enums.Specialty;
import jakarta.validation.constraints.*;

public record RegisterRequest(
        @NotBlank(message = "Ad zorunludur")
        String firstName,

        @NotBlank(message = "Soyad zorunludur")
        String lastName,

        @Email(message = "Geçerli bir email adresi giriniz")
        @NotBlank(message = "Email zorunludur")
        String email,

        @NotBlank(message = "Lisans numarası zorunludur")
        String licenseNumber,

        @NotNull(message = "Uzmanlık alanı zorunludur")
        Specialty specialty,

        @NotBlank(message = "Şifre zorunludur")
        @Size(min = 8, message = "Şifre en az 8 karakter olmalıdır")
        @Pattern(
                regexp = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@#$%^&+=!]).*$",
                message = "Şifre en az bir büyük harf, bir küçük harf, bir rakam ve bir özel karakter (@#$%^&+=!) içermelidir"
        )
        String password
) {}
