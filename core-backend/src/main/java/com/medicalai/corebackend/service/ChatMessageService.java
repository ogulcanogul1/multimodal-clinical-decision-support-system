package com.medicalai.corebackend.service;

import com.medicalai.corebackend.dto.request.AiAgentRequest;
import com.medicalai.corebackend.dto.request.ChatMessageRequest;
import com.medicalai.corebackend.dto.response.AiAgentResponse;
import com.medicalai.corebackend.dto.response.ChatMessageResponse;
import com.medicalai.corebackend.entity.*;
import com.medicalai.corebackend.entity.enums.ConsultationStatus;
import com.medicalai.corebackend.entity.enums.MessageSender;
import com.medicalai.corebackend.repository.ChatMessageRepository;
import com.medicalai.corebackend.repository.ConsultationRepository;
import com.medicalai.corebackend.repository.DocumentAnalysisRepository;
import com.medicalai.corebackend.repository.ImageAnalysisRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ChatMessageService {

    private final ChatMessageRepository chatMessageRepository;
    private final ConsultationRepository consultationRepository;
    private final AiIntegrationService aiIntegrationService;

    // URL'leri bulmak ve analizleri güncellemek için Repolar
    private final ImageAnalysisRepository imageAnalysisRepository;
    private final DocumentAnalysisRepository documentAnalysisRepository;

    @Transactional
    public ChatMessageResponse sendMessage(String consultationId, ChatMessageRequest request) {
        Consultation consultation = consultationRepository.findById(consultationId)
                .orElseThrow(() -> new RuntimeException("Muayene bulunamadı: " + consultationId));

        if (consultation.getStatus() == ConsultationStatus.CLOSED) {
            throw new RuntimeException("Bu muayene kapatılmış! Yeni mesaj gönderilemez.");
        }

        Patient patient = consultation.getPatient();
        if (patient == null) {
            throw new RuntimeException("Bu muayeneye atanmış bir hasta bulunamadı!");
        }

        // --- SOHBET GEÇMİŞİNİ ALIYORUZ ---
        List<AiAgentRequest.ChatHistoryItem> history = chatMessageRepository
                .findByConsultationIdOrderByTimestampAsc(consultationId)
                .stream()
                .map(m -> new AiAgentRequest.ChatHistoryItem(
                        m.getSenderRole().name(),
                        m.getMessageContent()
                ))
                .toList();

        // 1. DOKTORUN YENİ MESAJINI KAYDET
        ChatMessage doctorMessage = ChatMessage.builder()
                .consultation(consultation)
                .senderRole(MessageSender.DOCTOR)
                .messageContent(request.messageContent())
                .imageAnalysisId(request.imageAnalysisId())
                .documentAnalysisId(request.documentAnalysisId())
                .build();
        chatMessageRepository.save(doctorMessage);

        // --- ID'LERİ URL'YE ÇEVİRME ---
        String imageUrl = request.imageAnalysisId() != null ?
                imageAnalysisRepository.findById(request.imageAnalysisId()).map(ImageAnalysis::getOriginalImageUrl).orElse(null) : null;
        String documentUrl = request.documentAnalysisId() != null ?
                documentAnalysisRepository.findById(request.documentAnalysisId()).map(DocumentAnalysis::getDocumentUrl).orElse(null) : null;

        // 2. PYTHON FASTAPI'YE İSTEĞİ AT
        AiAgentRequest aiRequest = new AiAgentRequest(
                request.messageContent(),
                imageUrl,
                documentUrl,
                consultation.getChiefComplaint(), // hasta şikayeti

                patient.getAge(),
                patient.getGender() != null ? patient.getGender().name() : null,
                patient.getBloodType() != null ? patient.getBloodType().name() : null,

                patient.getChronicDiseases() == null ? java.util.Collections.emptyList() :
                        patient.getChronicDiseases().stream().map(Disease::getName).toList(),
                patient.getAllergies() == null ? java.util.Collections.emptyList() :
                        patient.getAllergies().stream().map(Allergy::getName).toList(),
                patient.getCurrentMedications() == null ? java.util.Collections.emptyList() :
                        patient.getCurrentMedications().stream().map(Medication::getName).toList(),

                history
        );

        // PYTHON'DAN CEVAP GELİYOR
        AiAgentResponse aiResponse = aiIntegrationService.askFastApi(aiRequest);

        // --- EKLENEN KISIM: MULTIMODAL VERİLERİ VERİTABANINA İŞLEME ---

        // A. Eğer bu mesajda bir Görüntü (X-Ray vb.) sorulduysa ve Python analiz ürettiyse:
        if (request.imageAnalysisId() != null) {
            imageAnalysisRepository.findById(request.imageAnalysisId()).ifPresent(img -> {
                // Null kontrolü yapıyoruz ki eski analiz varsa üzerine null yazıp silmesin
                if (aiResponse.imagePrediction() != null) img.setAiPrediction(aiResponse.imagePrediction());
                if (aiResponse.imageConfidenceScore() != null) img.setConfidenceScore(aiResponse.imageConfidenceScore());
                if (aiResponse.heatmapUrl() != null) img.setHeatmapUrl(aiResponse.heatmapUrl());

                imageAnalysisRepository.save(img); // Güncelledik!
            });
        }

        // B. Eğer bu mesajda bir Belge (Kan Tahlili vb.) sorulduysa ve Python analiz ürettiyse:
        if (request.documentAnalysisId() != null) {
            documentAnalysisRepository.findById(request.documentAnalysisId()).ifPresent(doc -> {
                if (aiResponse.documentPrediction() != null) doc.setMlpPrediction(aiResponse.documentPrediction());
                if (aiResponse.documentConfidenceScore() != null) doc.setConfidenceScore(aiResponse.documentConfidenceScore());
                if (aiResponse.featureImportance() != null) doc.setFeatureImportance(aiResponse.featureImportance());

                documentAnalysisRepository.save(doc); // Güncelledik!
            });
        }
        // -------------------------------------------------------------

        // 3. PYTHON'DAN GELEN METİN CEVABINI AI MESAJI OLARAK KAYDET
        ChatMessage aiMessage = ChatMessage.builder()
                .consultation(consultation)
                .senderRole(MessageSender.AI)
                .messageContent(aiResponse.aiMessage())
                .citedSources(aiResponse.sources())
                .imageAnalysisId(request.imageAnalysisId())
                .documentAnalysisId(request.documentAnalysisId())
                .build();

        return mapToResponse(chatMessageRepository.save(aiMessage));
    }

    @Transactional(readOnly = true)
    public List<ChatMessageResponse> getChatHistory(String consultationId) {
        return chatMessageRepository.findByConsultationIdOrderByTimestampAsc(consultationId)
                .stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    private ChatMessageResponse mapToResponse(ChatMessage m) {
        return new ChatMessageResponse(
                m.getId(),
                m.getSenderRole(),
                m.getMessageContent(),
                m.getCitedSources(),
                m.getImageAnalysisId(),
                m.getDocumentAnalysisId(),
                m.getTimestamp()
        );
    }
}