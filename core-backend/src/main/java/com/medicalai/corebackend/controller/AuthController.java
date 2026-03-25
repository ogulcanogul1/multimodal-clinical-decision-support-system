package com.medicalai.corebackend.controller;

import com.medicalai.corebackend.dto.request.DoctorRequest;
import com.medicalai.corebackend.dto.request.LoginRequest;
import com.medicalai.corebackend.dto.request.RegisterRequest;
import com.medicalai.corebackend.dto.response.AuthResponse;
import com.medicalai.corebackend.entity.Doctor;
import com.medicalai.corebackend.repository.DoctorRepository;
import com.medicalai.corebackend.security.JwtTokenProvider;
import com.medicalai.corebackend.service.DoctorService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthenticationManager authenticationManager;
    private final JwtTokenProvider jwtTokenProvider;
    private final DoctorRepository doctorRepository;
    private final DoctorService doctorService;

    @PostMapping("/register")
    public ResponseEntity<AuthResponse> register(@Valid @RequestBody RegisterRequest request) {
        DoctorRequest doctorRequest = new DoctorRequest(
                request.firstName(), request.lastName(), request.email(),
                request.licenseNumber(), request.specialty(), request.password()
        );
        doctorService.createDoctor(doctorRequest);

        Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(request.email(), request.password())
        );
        String token = jwtTokenProvider.generateToken(authentication);

        Doctor doctor = doctorRepository.findByEmail(request.email()).orElseThrow();
        return ResponseEntity.status(HttpStatus.CREATED).body(new AuthResponse(
                token, doctor.getId(), doctor.getEmail(), doctor.getFirstName(), doctor.getLastName()
        ));
    }

    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@Valid @RequestBody LoginRequest request) {
        Authentication authentication = authenticationManager.authenticate(

                new UsernamePasswordAuthenticationToken(request.email(), request.password())
        );

        String token = jwtTokenProvider.generateToken(authentication);

        Doctor doctor = doctorRepository.findByEmail(request.email()).orElseThrow();

        return ResponseEntity.ok(new AuthResponse(
                token,
                doctor.getId(),
                doctor.getEmail(),
                doctor.getFirstName(),
                doctor.getLastName()
        ));
    }
}
