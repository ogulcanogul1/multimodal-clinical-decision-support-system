package com.medicalai.corebackend.controller;

import com.medicalai.corebackend.dto.request.DoctorRequest;
import com.medicalai.corebackend.dto.response.DoctorResponse;
import com.medicalai.corebackend.entity.enums.Specialty;
import com.medicalai.corebackend.service.DoctorService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/doctors")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class DoctorController {

    private final DoctorService doctorService;

    /**
     * Yeni bir doktor kaydı oluşturur (Register).
     */
    @PostMapping
    public ResponseEntity<DoctorResponse> registerDoctor(@Valid @RequestBody DoctorRequest request) {
        DoctorResponse response = doctorService.createDoctor(request);
        return new ResponseEntity<>(response, HttpStatus.CREATED);
    }

    /**
     * Tüm doktorları listeler.
     */
    @GetMapping
    public ResponseEntity<List<DoctorResponse>> getAllDoctors() {
        return ResponseEntity.ok(doctorService.getAllDoctors());
    }

    /**
     * Veritabanı ID'si üzerinden doktor getirir.
     */
    @GetMapping("/id/{id}")
    public ResponseEntity<DoctorResponse> getDoctorById(@PathVariable String id) {
        return ResponseEntity.ok(doctorService.getDoctorById(id));
    }

    /**
     * Uzmanlık alanına göre doktorları filtreler.
     * Kullanım: /api/doctors/specialty/CARDIOLOGY
     */
    @GetMapping("/specialty/{specialty}")
    public ResponseEntity<List<DoctorResponse>> getDoctorsBySpecialty(@PathVariable Specialty specialty) {
        return ResponseEntity.ok(doctorService.getDoctorsBySpecialty(specialty));
    }

    /**
     * Email adresi üzerinden doktor sorgular.
     * Kullanım: /api/doctors/search/email?email=dr.asd@hastane.com
     */
    @GetMapping("/search/email")
    public ResponseEntity<DoctorResponse> getDoctorByEmail(@RequestParam String email) {
        return ResponseEntity.ok(doctorService.getDoctorByEmail(email));
    }

    /**
     * Lisans/Diploma numarası üzerinden doktor sorgular.
     * Kullanım: /api/doctors/search/license?licenseNumber=TR-12345
     */
    @GetMapping("/search/license")
    public ResponseEntity<DoctorResponse> getDoctorByLicense(@RequestParam String licenseNumber) {
        return ResponseEntity.ok(doctorService.getDoctorByLicense(licenseNumber));
    }
}
