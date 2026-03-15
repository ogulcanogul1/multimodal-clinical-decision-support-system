package com.medicalai.corebackend.repository;

import com.medicalai.corebackend.entity.Medication;
import org.springframework.data.jpa.repository.JpaRepository;

public interface MedicationRepository extends JpaRepository<Medication, Long> {
}
