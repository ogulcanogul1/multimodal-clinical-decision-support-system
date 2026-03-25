package com.medicalai.corebackend.dto.response;

public record AuthResponse(
        String token,
        String doctorId,
        String email,
        String firstName,
        String lastName
) {}
