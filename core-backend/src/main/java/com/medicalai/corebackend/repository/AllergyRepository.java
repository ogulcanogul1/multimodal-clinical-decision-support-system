package com.medicalai.corebackend.repository;

import com.medicalai.corebackend.entity.Allergy;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AllergyRepository extends JpaRepository<Allergy, Long> {
}
