package com.medicalai.corebackend.controller;

import com.medicalai.corebackend.dto.request.PatientRequest;
import com.medicalai.corebackend.dto.response.PatientResponse;
import com.medicalai.corebackend.service.PatientService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/patients")
@RequiredArgsConstructor
@CrossOrigin(origins = "*") // Frontend entegrasyonu başladığında güvenli bir adrese çekilebilir
public class PatientController {

    private final PatientService patientService;

    /**
     * Yeni bir hasta kaydı oluşturur.
     * @Valid anotasyonu, PatientRequest içindeki @NotBlank, @Size gibi kısıtlamaları kontrol eder.
     */
    @PostMapping
    public ResponseEntity<PatientResponse> createPatient(@Valid @RequestBody PatientRequest request) {
        PatientResponse response = patientService.savePatient(request);
        return new ResponseEntity<>(response, HttpStatus.CREATED);
    }

    /**
     * Sistemdeki tüm hastaları listeler.
     */
    @GetMapping
    public ResponseEntity<List<PatientResponse>> getAllPatients() {
        List<PatientResponse> patients = patientService.getAllPatients();
        return ResponseEntity.ok(patients);
    }

    /**
     * Veritabanı ID'si üzerinden tek bir hasta getirir.
     */
    @GetMapping("/id/{id}")
    public ResponseEntity<PatientResponse> getPatientById(@PathVariable String id) {
        return ResponseEntity.ok(patientService.getPatientById(id));
    }

    /**
     * TC Kimlik Numarası üzerinden hasta sorgular.
     * Doktorların en çok kullanacağı arama endpoint'i budur.
     */
    @GetMapping("/search")
    public ResponseEntity<PatientResponse> getPatientByNationalId(@RequestParam String nationalId) {
        return ResponseEntity.ok(patientService.getPatientByNationalId(nationalId));
    }

    /**
     * Mevcut bir hastanın bilgilerini günceller.
     * Özellikle kronik hastalıkların güncel tutulması RAG performansı için kritiktir.
     */
    @PutMapping("/{id}")
    public ResponseEntity<PatientResponse> updatePatient(
            @PathVariable String id,
            @Valid @RequestBody PatientRequest request) {
        return ResponseEntity.ok(patientService.updatePatient(id, request));
    }
}
