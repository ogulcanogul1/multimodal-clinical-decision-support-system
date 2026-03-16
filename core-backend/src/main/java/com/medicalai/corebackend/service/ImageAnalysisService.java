package com.medicalai.corebackend.service;

import com.medicalai.corebackend.dto.request.AiResultUpdateRequest;
import com.medicalai.corebackend.dto.response.ImageAnalysisResponse;
import com.medicalai.corebackend.entity.Consultation;
import com.medicalai.corebackend.entity.ImageAnalysis;
import com.medicalai.corebackend.entity.enums.AnalysisType;
import com.medicalai.corebackend.repository.ConsultationRepository;
import com.medicalai.corebackend.repository.ImageAnalysisRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ImageAnalysisService {

    private final ImageAnalysisRepository imageAnalysisRepository;
    private final ConsultationRepository consultationRepository;

    // Görüntülerin kaydedileceği lokal dizin (application.yml'den geliyor)
    @Value("${app.storage.image-dir}")
    private String UPLOAD_IMAGE_DIR;

    /**
     * 1. Adım: Doktor frontend'den resmi yükler. Dosya sunucuya kaydedilir,
     * veritabanında PENDING (bekleyen) bir analiz kaydı açılır.
     */
    @Transactional
    public ImageAnalysisResponse createImageAnalysis(String consultationId, AnalysisType analysisType, MultipartFile file) {

        Consultation consultation = consultationRepository.findById(consultationId)
                .orElseThrow(() -> new RuntimeException("Muayene bulunamadı: " + consultationId));

        // Dosyayı diske kaydet ve SADECE DOSYA ADINI (UUID.png) al
        String savedImageName = saveFileLocally(file);

        ImageAnalysis analysis = ImageAnalysis.builder()
                .consultation(consultation)
                .originalImageUrl(savedImageName) // Veritabanına sadece isim kaydediliyor!
                .analysisType(analysisType)
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

        // Eğer Python Heatmap ürettiyse, onun da sadece ismini (heatmap_uuid.png) veritabanına kaydederiz
        analysis.setHeatmapUrl(resultRequest.heatmapUrl());

        return mapToResponse(imageAnalysisRepository.save(analysis));
    }

    /**
     * 3. Adım: Doktor yapay zekanın teşhisine katılıyor mu? (RLHF)
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

    /**
     * Dosyayı sunucuya fiziksel olarak kaydeden yardımcı metod.
     */
    private String saveFileLocally(MultipartFile file) {
        try {
            Path uploadPath = Paths.get(UPLOAD_IMAGE_DIR);
            // Klasör yoksa oluştur
            if (!Files.exists(uploadPath)) {
                Files.createDirectories(uploadPath);
            }

            String originalFileName = file.getOriginalFilename();
            String extension = "";
            if (originalFileName != null && originalFileName.contains(".")) {
                extension = originalFileName.substring(originalFileName.lastIndexOf("."));
            }

            // İsim çakışmasını önlemek için rastgele UUID kullanıyoruz
            String newFileName = UUID.randomUUID().toString() + extension;
            Path filePath = uploadPath.resolve(newFileName);

            // Dosyayı diske yaz (Fiziksel olarak application.yml'deki adrese gider)
            Files.copy(file.getInputStream(), filePath);

            // MİMARİ DÜZELTME: Geriye klasör yolunu değil, SADECE DOSYA ADINI dönüyoruz
            return newFileName;

        } catch (Exception e) {
            throw new RuntimeException("Dosya kaydedilirken hata oluştu: " + e.getMessage());
        }
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