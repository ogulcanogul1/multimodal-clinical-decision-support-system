package com.medicalai.corebackend.service;

import com.medicalai.corebackend.dto.request.DocumentAiResultUpdateRequest;
import com.medicalai.corebackend.dto.response.DocumentAnalysisResponse;
import com.medicalai.corebackend.entity.Consultation;
import com.medicalai.corebackend.entity.DocumentAnalysis;
import com.medicalai.corebackend.entity.enums.DocumentType;
import com.medicalai.corebackend.repository.ConsultationRepository;
import com.medicalai.corebackend.repository.DocumentAnalysisRepository;
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
public class DocumentAnalysisService {

    private final DocumentAnalysisRepository documentAnalysisRepository;
    private final ConsultationRepository consultationRepository;

    @Value("${app.storage.document-dir}")
    private String documentDir;

    @Transactional
    public DocumentAnalysisResponse createDocumentAnalysis(String consultationId, DocumentType documentType, MultipartFile file) {
        Consultation consultation = consultationRepository.findById(consultationId)
                .orElseThrow(() -> new RuntimeException("Muayene bulunamadı: " + consultationId));

        String savedDocumentUrl = saveFileLocally(file);

        // Not: Entity'de documentType'ı String yaptıysan .name() ile çevirebilirsin,
        // Enum yaptıysan direkt verebilirsin. Burada Enum varsayarak yazıyorum.
        DocumentAnalysis analysis = DocumentAnalysis.builder()
                .consultation(consultation)
                .documentUrl(savedDocumentUrl)
                .documentType(documentType.name()) // Entity'de String tanımlı olduğu için .name() kullandık
                .build();

        return mapToResponse(documentAnalysisRepository.save(analysis));
    }

    @Transactional
    public DocumentAnalysisResponse updateAiResults(String id, DocumentAiResultUpdateRequest request) {
        DocumentAnalysis analysis = documentAnalysisRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Belge analizi bulunamadı: " + id));

        analysis.setMlpPrediction(request.mlpPrediction());
        analysis.setConfidenceScore(request.confidenceScore());
        analysis.setFeatureImportance(request.featureImportance());

        return mapToResponse(documentAnalysisRepository.save(analysis));
    }

    @Transactional
    public DocumentAnalysisResponse submitDoctorFeedback(String id, boolean isApproved) {
        DocumentAnalysis analysis = documentAnalysisRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Belge analizi bulunamadı: " + id));

        analysis.setDoctorFeedback(isApproved);
        return mapToResponse(documentAnalysisRepository.save(analysis));
    }

    @Transactional(readOnly = true)
    public List<DocumentAnalysisResponse> getAnalysesByConsultation(String consultationId) {
        return documentAnalysisRepository.findByConsultationIdOrderByCreatedAtDesc(consultationId)
                .stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    private String saveFileLocally(MultipartFile file) {
        try {
            Path uploadPath = Paths.get(documentDir);
            if (!Files.exists(uploadPath)) {
                Files.createDirectories(uploadPath);
            }

            String originalFileName = file.getOriginalFilename();
            String extension = originalFileName != null && originalFileName.contains(".")
                    ? originalFileName.substring(originalFileName.lastIndexOf("."))
                    : ".pdf"; // Varsayılan olarak PDF kabul ediyoruz

            String newFileName = UUID.randomUUID().toString() + extension;
            Path filePath = uploadPath.resolve(newFileName);

            Files.copy(file.getInputStream(), filePath);

            return filePath.toString().replace("\\", "/");
        } catch (Exception e) {
            throw new RuntimeException("Belge kaydedilirken hata oluştu: " + e.getMessage());
        }
    }

    private DocumentAnalysisResponse mapToResponse(DocumentAnalysis a) {
        return new DocumentAnalysisResponse(
                a.getId(),
                a.getConsultation().getId(),
                a.getDocumentUrl(),
                DocumentType.valueOf(a.getDocumentType()), // String'den Enum'a geri çeviriyoruz
                a.getMlpPrediction(),
                a.getConfidenceScore(),
                a.getFeatureImportance(),
                a.getDoctorFeedback(),
                a.getCreatedAt()
        );
    }
}
