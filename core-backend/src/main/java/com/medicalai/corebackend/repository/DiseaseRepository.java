package com.medicalai.corebackend.repository;

import com.medicalai.corebackend.entity.Disease;
import org.springframework.data.jpa.repository.JpaRepository;

public interface DiseaseRepository extends JpaRepository<Disease, Long> {
}
