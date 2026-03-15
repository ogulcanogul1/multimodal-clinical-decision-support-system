package com.medicalai.corebackend.repository;

import com.medicalai.corebackend.entity.DocumentAnalysis;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface DocumentAnalysisRepository extends JpaRepository<DocumentAnalysis, String> {
    List<DocumentAnalysis> findByConsultationIdOrderByCreatedAtDesc(String consultationId);
}
