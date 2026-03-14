package com.medicalai.corebackend.controller;

import com.medicalai.corebackend.dto.request.ConsultationRequest;
import com.medicalai.corebackend.dto.response.ConsultationResponse;
import com.medicalai.corebackend.service.ConsultationService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/consultations")
@RequiredArgsConstructor
@CrossOrigin(origins = "*") // Frontend entegrasyonu için şimdiden ekleyelim
public class ConsultationController {

    private final ConsultationService consultationService;

    /**
     * Yeni bir muayene (Consultation) başlatır.
     * POST /api/consultations
     */
    @PostMapping
    public ResponseEntity<ConsultationResponse> create(@Valid @RequestBody ConsultationRequest request) {
        ConsultationResponse response = consultationService.createConsultation(request);
        return new ResponseEntity<>(response, HttpStatus.CREATED);
    }

    /**
     * Belirli bir muayeneyi ID üzerinden getirir.
     * GET /api/consultations/{id}
     */
    @GetMapping("/{id}")
    public ResponseEntity<ConsultationResponse> getById(@PathVariable String id) {
        return ResponseEntity.ok(consultationService.getConsultationById(id));
    }

    /**
     * Bir hastanın tüm muayene geçmişini listeler.
     * GET /api/consultations/patient/{patientId}
     */
    @GetMapping("/patient/{patientId}")
    public ResponseEntity<List<ConsultationResponse>> getByPatient(@PathVariable String patientId) {
        return ResponseEntity.ok(consultationService.getConsultationsByPatientId(patientId));
    }

    /**
     * Bir doktorun şu an açık (aktif) olan muayenelerini listeler.
     * GET /api/consultations/active/doctor/{doctorId}
     */
    @GetMapping("/active/doctor/{doctorId}")
    public ResponseEntity<List<ConsultationResponse>> getActiveByDoctor(@PathVariable String doctorId) {
        return ResponseEntity.ok(consultationService.getActiveConsultationsByDoctor(doctorId));
    }

    /**
     * Devam eden bir muayeneyi kapatır/tamamlar.
     * PATCH /api/consultations/{id}/close
     */
    @PatchMapping("/{id}/close")
    public ResponseEntity<ConsultationResponse> close(@PathVariable String id) {
        return ResponseEntity.ok(consultationService.closeConsultation(id));
    }
}