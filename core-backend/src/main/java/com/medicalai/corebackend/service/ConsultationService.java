package com.medicalai.corebackend.service;

import com.medicalai.corebackend.dto.request.ConsultationRequest;
import com.medicalai.corebackend.dto.response.ConsultationResponse;
import com.medicalai.corebackend.entity.Consultation;
import com.medicalai.corebackend.entity.Doctor;
import com.medicalai.corebackend.entity.Patient;
import com.medicalai.corebackend.entity.enums.ConsultationStatus;
import com.medicalai.corebackend.repository.ConsultationRepository;
import com.medicalai.corebackend.repository.DoctorRepository;
import com.medicalai.corebackend.repository.PatientRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ConsultationService {

    private final ConsultationRepository consultationRepository;
    private final PatientRepository patientRepository;
    private final DoctorRepository doctorRepository;

    /**
     * Yeni bir muayene başlatır.
     * Veritabanında ilgili doktor ve hastanın varlığını kontrol eder.
     */
    @Transactional
    public ConsultationResponse createConsultation(ConsultationRequest request) {
        // 1. Referential Integrity: Hasta ve Doktor gerçekten var mı?
        Patient patient = patientRepository.findById(request.patientId())
                .orElseThrow(() -> new RuntimeException("Muayene açılacak hasta bulunamadı!"));

        Doctor doctor = doctorRepository.findById(request.doctorId())
                .orElseThrow(() -> new RuntimeException("Muayene açacak doktor bulunamadı!"));

        // 2. Yeni muayene nesnesini kur (Varsayılan olarak OPEN statüsünde başlar)
        Consultation consultation = Consultation.builder()
                .patient(patient)
                .doctor(doctor)
                .status(ConsultationStatus.OPEN)
                .build();

        Consultation saved = consultationRepository.save(consultation);
        return mapToResponse(saved);
    }

    /**
     * Belirli bir hastanın tüm muayene geçmişini, en yeni tarihten en eskiye doğru getirir.
     */
    @Transactional(readOnly = true)
    public List<ConsultationResponse> getConsultationsByPatientId(String patientId) {
        return consultationRepository.findByPatientIdOrderByCreatedAtDesc(patientId)
                .stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    /**
     * Bir doktorun şu an devam eden (açık) tüm muayenelerini listeler.
     */
    @Transactional(readOnly = true)
    public List<ConsultationResponse> getActiveConsultationsByDoctor(String doctorId) {
        return consultationRepository.findByDoctorIdAndStatus(doctorId, ConsultationStatus.OPEN)
                .stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    /**
     * Tek bir muayeneyi ID üzerinden detaylıca getirir.
     */
    @Transactional(readOnly = true)
    public ConsultationResponse getConsultationById(String id) {
        Consultation consultation = consultationRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Muayene bulunamadı: " + id));
        return mapToResponse(consultation);
    }

    /**
     * Entity -> Response DTO dönüşümünü yapan yardımcı metod.
     */
    private ConsultationResponse mapToResponse(Consultation c) {
        return new ConsultationResponse(
                c.getId(),
                c.getPatient().getId(),
                c.getPatient().getFirstName() + " " + c.getPatient().getLastName(),
                c.getDoctor().getId(),
                c.getDoctor().getFirstName() + " " + c.getDoctor().getLastName(),
                c.getStatus(),
                c.getCreatedAt()
        );
    }

    @Transactional
    public ConsultationResponse closeConsultation(String id) {
        Consultation consultation = consultationRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Kapatılacak muayene bulunamadı: " + id));

        if (consultation.getStatus() == ConsultationStatus.CLOSED) {
            throw new RuntimeException("Bu muayene zaten daha önce kapatılmış.");
        }

        // Statüyü güncelle
        consultation.setStatus(ConsultationStatus.CLOSED);

        Consultation updated = consultationRepository.save(consultation);

        return mapToResponse(updated);
    }
}