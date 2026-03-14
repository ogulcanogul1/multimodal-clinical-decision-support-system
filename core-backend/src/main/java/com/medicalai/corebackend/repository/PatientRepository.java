package com.medicalai.corebackend.repository;

import com.medicalai.corebackend.entity.Patient;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface PatientRepository extends JpaRepository<Patient, String> {

    // TC kimlik numarasına göre hastayı bul
    Optional<Patient> findByNationalId(String nationalId);

    boolean existsByNationalId(String nationalId);
}
