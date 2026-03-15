package com.medicalai.corebackend.service;

import com.medicalai.corebackend.dto.request.AiResultUpdateRequest;
import com.medicalai.corebackend.dto.request.ImageAnalysisRequest;
import com.medicalai.corebackend.dto.response.ImageAnalysisResponse;
import com.medicalai.corebackend.entity.Consultation;
import com.medicalai.corebackend.entity.ImageAnalysis;
import com.medicalai.corebackend.repository.ConsultationRepository;
import com.medicalai.corebackend.repository.ImageAnalysisRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ImageAnalysisService {

    private final ImageAnalysisRepository imageAnalysisRepository;
    private final ConsultationRepository consultationRepository;

    /**
     * 1. Adım: Doktor görüntüyü yüklediğinde kaydı oluşturur.
     * (Henüz AI tahmini yoktur, PENDING durumu gibi düşünebilirsin).
     */
    @Transactional
    public ImageAnalysisResponse createImageAnalysis(ImageAnalysisRequest request) {
        Consultation consultation = consultationRepository.findById(request.consultationId())
                .orElseThrow(() -> new RuntimeException("Muayene bulunamadı: " + request.consultationId()));

        ImageAnalysis analysis = ImageAnalysis.builder()
                .consultation(consultation)
                .originalImageUrl(request.originalImageUrl())
                .analysisType(request.analysisType())
                .build();

        return mapToResponse(imageAnalysisRepository.save(analysis));
    }

    /**
     * 2. Adım: Python'daki model çalıştıktan sonra bu metodu tetikleyip sonuçları yazar.
     */
    @Transactional
    public ImageAnalysisResponse updateAiResults(String id, AiResultUpdateRequest resultRequest) {
        ImageAnalysis analysis = imageAnalysisRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Görüntü analizi bulunamadı: " + id));

        analysis.setAiPrediction(resultRequest.aiPrediction());
        analysis.setConfidenceScore(resultRequest.confidenceScore());
        analysis.setHeatmapUrl(resultRequest.heatmapUrl());

        return mapToResponse(imageAnalysisRepository.save(analysis));
    }

    /**
     * 3. Adım: Doktor yapay zekanın teşhisine katılıyor mu? (RLHF - Reinforcement Learning from Human Feedback için çok değerli!)
     */
    @Transactional
    public ImageAnalysisResponse submitDoctorFeedback(String id, boolean isApproved) {
        ImageAnalysis analysis = imageAnalysisRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Görüntü analizi bulunamadı: " + id));

        analysis.setDoctorFeedback(isApproved);
        return mapToResponse(imageAnalysisRepository.save(analysis));
    }

    /**
     * Bir muayeneye ait tüm analizleri getir.
     */
    @Transactional(readOnly = true)
    public List<ImageAnalysisResponse> getAnalysesByConsultation(String consultationId) {
        return imageAnalysisRepository.findByConsultationIdOrderByCreatedAtDesc(consultationId)
                .stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    private ImageAnalysisResponse mapToResponse(ImageAnalysis a) {
        return new ImageAnalysisResponse(
                a.getId(),
                a.getConsultation().getId(),
                a.getOriginalImageUrl(),
                a.getAnalysisType(),
                a.getAiPrediction(),
                a.getConfidenceScore(),
                a.getHeatmapUrl(),
                a.getDoctorFeedback(),
                a.getCreatedAt()
        );
    }
}
