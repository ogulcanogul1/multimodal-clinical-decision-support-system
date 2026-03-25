package com.medicalai.corebackend.controller;

import com.medicalai.corebackend.dto.response.AllergyResponse;
import com.medicalai.corebackend.dto.response.DiseaseResponse;
import com.medicalai.corebackend.dto.response.MedicationResponse;
import com.medicalai.corebackend.repository.AllergyRepository;
import com.medicalai.corebackend.repository.DiseaseRepository;
import com.medicalai.corebackend.repository.MedicationRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class DictionaryController {

    private final DiseaseRepository diseaseRepository;
    private final AllergyRepository allergyRepository;
    private final MedicationRepository medicationRepository;

    @GetMapping("/diseases")
    public ResponseEntity<List<DiseaseResponse>> getAllDiseases() {
        List<DiseaseResponse> diseases = diseaseRepository.findAll()
                .stream()
                .map(d -> new DiseaseResponse(d.getId(), d.getName(), d.getIcd10Code()))
                .toList();
        return ResponseEntity.ok(diseases);
    }

    @GetMapping("/allergies")
    public ResponseEntity<List<AllergyResponse>> getAllAllergies() {
        List<AllergyResponse> allergies = allergyRepository.findAll()
                .stream()
                .map(a -> new AllergyResponse(a.getId(), a.getName()))
                .toList();
        return ResponseEntity.ok(allergies);
    }

    @GetMapping("/medications")
    public ResponseEntity<List<MedicationResponse>> getAllMedications() {
        List<MedicationResponse> medications = medicationRepository.findAll()
                .stream()
                .map(m -> new MedicationResponse(m.getId(), m.getName()))
                .toList();
        return ResponseEntity.ok(medications);
    }
}
