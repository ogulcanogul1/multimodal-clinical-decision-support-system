package com.medicalai.corebackend.repository;

import com.medicalai.corebackend.entity.ImageAnalysis;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ImageAnalysisRepository extends JpaRepository<ImageAnalysis, String> {

    // Bir muayeneye ait röntgen/MR analiz sonuçlarını getir
    List<ImageAnalysis> findByConsultationIdOrderByCreatedAtDesc(String consultationId);
}
