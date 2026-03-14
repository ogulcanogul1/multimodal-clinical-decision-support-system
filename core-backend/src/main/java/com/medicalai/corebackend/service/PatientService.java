package com.medicalai.corebackend.service;

import com.medicalai.corebackend.dto.request.PatientRequest;
import com.medicalai.corebackend.dto.response.PatientResponse;
import com.medicalai.corebackend.entity.Patient;
import com.medicalai.corebackend.repository.PatientRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class PatientService {

    private final PatientRepository patientRepository;

    @Transactional
    public PatientResponse savePatient(PatientRequest request) {
        // İş Kuralı: Aynı TC ile iki hasta olamaz
        if (patientRepository.existsByNationalId(request.nationalId())) {
            throw new RuntimeException("Bu TC Kimlik numarası zaten kayıtlı!");
        }

        // Mapping: Request -> Entity
        Patient patient = Patient.builder()
                .nationalId(request.nationalId())
                .firstName(request.firstName())
                .lastName(request.lastName())
                .dateOfBirth(request.dateOfBirth())
                .gender(request.gender())
                .bloodType(request.bloodType())
                .chronicDiseases(request.chronicDiseases())
                .build();

        Patient saved = patientRepository.save(patient);

        // Mapping: Entity -> Response
        return mapToResponse(saved);
    }

    private PatientResponse mapToResponse(Patient patient) {
        return new PatientResponse(
                patient.getId(),
                patient.getNationalId(),
                patient.getFirstName(),
                patient.getLastName(),
                patient.getDateOfBirth(),
                patient.getGender(),
                patient.getBloodType(),
                patient.getChronicDiseases(),
                patient.getCreatedAt()
        );
    }

    @Transactional(readOnly = true)
    public PatientResponse getPatientByNationalId(String nationalId) {
        Patient patient = patientRepository.findByNationalId(nationalId)
                .orElseThrow(() -> new RuntimeException("Hasta bulunamadı: " + nationalId));
        return mapToResponse(patient);
    }

    // ID ile Hasta Getir (İç sistemlerde, muayene açarken kullanacağız)
    @Transactional(readOnly = true)
    public PatientResponse getPatientById(String id) {
        Patient patient = patientRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("ID ile aranan hasta bulunamadı: " + id));
        return mapToResponse(patient);
    }

    //  Tüm Hastaları Listele (Admin paneli veya genel liste için)
    @Transactional(readOnly = true)
    public List<PatientResponse> getAllPatients() {
        return patientRepository.findAll().stream()
                .map(this::mapToResponse)
                .toList();
    }

    // Hasta Bilgilerini Güncelle (Kronik hastalıklar değiştikçe RAG'in doğru çalışması için şart!)
    @Transactional
    public PatientResponse updatePatient(String id, PatientRequest request) {
        Patient existingPatient = patientRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Güncellenecek hasta bulunamadı."));

        existingPatient.setFirstName(request.firstName());
        existingPatient.setLastName(request.lastName());
        existingPatient.setChronicDiseases(request.chronicDiseases());
        existingPatient.setBloodType(request.bloodType());
        // TC No genellikle değiştirilmez, o yüzden onu set etmiyoruz.

        return mapToResponse(patientRepository.save(existingPatient));
    }
}