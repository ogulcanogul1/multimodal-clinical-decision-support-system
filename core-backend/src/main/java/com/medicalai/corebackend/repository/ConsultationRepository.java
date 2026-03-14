package com.medicalai.corebackend.repository;

import com.medicalai.corebackend.entity.Consultation;
import com.medicalai.corebackend.entity.enums.ConsultationStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ConsultationRepository extends JpaRepository<Consultation, String> {

    // Bir hastanın tüm muayenelerini en yenisi en üstte olacak şekilde getir
    // SQL: SELECT * FROM consultations WHERE patient_id = ? ORDER BY created_at DESC
    List<Consultation> findByPatientIdOrderByCreatedAtDesc(String patientId);

    // Bir doktorun şu an açık olan (devam eden) muayenelerini getir
    List<Consultation> findByDoctorIdAndStatus(String doctorId, ConsultationStatus status);
}
