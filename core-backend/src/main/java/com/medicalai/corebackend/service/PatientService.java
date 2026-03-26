package com.medicalai.corebackend.service;

import com.medicalai.corebackend.dto.request.PatientRequest;
import com.medicalai.corebackend.dto.response.PatientResponse;
import com.medicalai.corebackend.entity.Allergy;
import com.medicalai.corebackend.entity.Disease;
import com.medicalai.corebackend.entity.Medication;
import com.medicalai.corebackend.entity.Patient;
import com.medicalai.corebackend.exception.BusinessException;
import com.medicalai.corebackend.exception.ErrorCode;
import com.medicalai.corebackend.repository.AllergyRepository;
import com.medicalai.corebackend.repository.DiseaseRepository;
import com.medicalai.corebackend.repository.MedicationRepository;
import com.medicalai.corebackend.repository.PatientRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class PatientService {

    private final PatientRepository patientRepository;
    private final DiseaseRepository diseaseRepository;
    private final AllergyRepository allergyRepository;
    private final MedicationRepository medicationRepository;

    // 1. POST - Yeni Hasta Kaydı (Senin Controller'daki savePatient metodu)
    @Transactional
    public PatientResponse savePatient(PatientRequest request) {

        // Aynı TC ile kayıt var mı kontrolü
        if (patientRepository.findByNationalId(request.nationalId()).isPresent()) {
            throw new BusinessException(ErrorCode.TC_ALREADY_EXISTS, "Bu TC Kimlik numarası ile kayıtlı bir hasta zaten var!");
        }

        Patient patient = Patient.builder()
                .nationalId(request.nationalId())
                .firstName(request.firstName())
                .lastName(request.lastName())
                .dateOfBirth(request.dateOfBirth())
                .gender(request.gender())
                .bloodType(request.bloodType())
                .build();

        // Sözlük ilişkilerini kur (ID listelerini Entity listelerine çevir)
        updatePatientAssociations(patient, request);

        return mapToResponse(patientRepository.save(patient));
    }

    // 2. GET - Tüm Hastaları Listele
    @Transactional(readOnly = true)
    public List<PatientResponse> getAllPatients() {
        return patientRepository.findAll()
                .stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    // 3. GET - ID ile Hasta Getir
    @Transactional(readOnly = true)
    public PatientResponse getPatientById(String id) {
        Patient patient = patientRepository.findById(id)
                .orElseThrow(() -> new BusinessException(ErrorCode.PATIENT_NOT_FOUND, "Hasta bulunamadı. ID: " + id));
        return mapToResponse(patient);
    }

    // 4. GET - TC Kimlik No ile Hasta Getir
    @Transactional(readOnly = true)
    public PatientResponse getPatientByNationalId(String nationalId) {
        Patient patient = patientRepository.findByNationalId(nationalId)
                .orElseThrow(() -> new BusinessException(ErrorCode.PATIENT_NOT_FOUND, "Hasta bulunamadı. TC: " + nationalId));
        return mapToResponse(patient);
    }

    // 5. PUT - Hastayı Güncelle (RAG performansı için kritik)
    @Transactional
    public PatientResponse updatePatient(String id, PatientRequest request) {
        Patient patient = patientRepository.findById(id)
                .orElseThrow(() -> new BusinessException(ErrorCode.PATIENT_NOT_FOUND, "Güncellenecek hasta bulunamadı. ID: " + id));

        // Temel bilgileri güncelle
        patient.setNationalId(request.nationalId());
        patient.setFirstName(request.firstName());
        patient.setLastName(request.lastName());
        patient.setDateOfBirth(request.dateOfBirth());
        patient.setGender(request.gender());
        patient.setBloodType(request.bloodType());

        // Sözlük ilişkilerini güncelle (Eski listelerin üzerine yazar)
        updatePatientAssociations(patient, request);

        return mapToResponse(patientRepository.save(patient));
    }

    // --- YARDIMCI METODLAR ---

    // İlişkileri kuran ortak metod (Kod tekrarını önler)
    private void updatePatientAssociations(Patient patient, PatientRequest request) {
        if (request.chronicDiseaseIds() != null) {
            patient.setChronicDiseases(diseaseRepository.findAllById(request.chronicDiseaseIds()));
        } else {
            patient.setChronicDiseases(Collections.emptyList());
        }

        if (request.allergyIds() != null) {
            patient.setAllergies(allergyRepository.findAllById(request.allergyIds()));
        } else {
            patient.setAllergies(Collections.emptyList());
        }

        if (request.currentMedicationIds() != null) {
            patient.setCurrentMedications(medicationRepository.findAllById(request.currentMedicationIds()));
        } else {
            patient.setCurrentMedications(Collections.emptyList());
        }
    }

    // Entity'den Response DTO'ya dönüştüren metod
    private PatientResponse mapToResponse(Patient p) {
        return new PatientResponse(
                p.getId(),
                p.getNationalId(),
                p.getFirstName(),
                p.getLastName(),
                p.getDateOfBirth(),
                p.getAge(),
                p.getGender(),
                p.getBloodType(),

                // Entity listelerini String (isim) listelerine çeviriyoruz
                p.getChronicDiseases() == null ? Collections.emptyList() :
                        p.getChronicDiseases().stream().map(Disease::getName).toList(),

                p.getAllergies() == null ? Collections.emptyList() :
                        p.getAllergies().stream().map(Allergy::getName).toList(),

                p.getCurrentMedications() == null ? Collections.emptyList() :
                        p.getCurrentMedications().stream().map(Medication::getName).toList(),

                p.getCreatedAt()
        );
    }
}