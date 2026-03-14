package com.medicalai.corebackend.repository;

import com.medicalai.corebackend.entity.DocumentAnalysis;
import org.springframework.data.jpa.repository.JpaRepository;

public interface DocumentAnalysisRepository extends JpaRepository<DocumentAnalysis, String> {
}
