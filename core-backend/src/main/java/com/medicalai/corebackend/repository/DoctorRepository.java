package com.medicalai.corebackend.repository;

import com.medicalai.corebackend.entity.Doctor;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface DoctorRepository extends JpaRepository<Doctor, String> {

    // Spring Data JPA bu isimden otomatik olarak şu SQL'i üretir:
    // SELECT * FROM doctors WHERE email = ?
    Optional<Doctor> findByEmail(String email);

    // Yeni doktor kaydederken lisans nosu veya emaili çakışıyor mu kontrolü için
    boolean existsByEmail(String email);
    boolean existsByLicenseNumber(String licenseNumber);
}