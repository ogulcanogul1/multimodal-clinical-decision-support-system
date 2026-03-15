package com.medicalai.corebackend.service;

import com.medicalai.corebackend.dto.request.AiAgentRequest;
import com.medicalai.corebackend.dto.request.ChatMessageRequest;
import com.medicalai.corebackend.dto.response.AiAgentResponse;
import com.medicalai.corebackend.dto.response.ChatMessageResponse;
import com.medicalai.corebackend.entity.ChatMessage;
import com.medicalai.corebackend.entity.Consultation;
import com.medicalai.corebackend.entity.DocumentAnalysis;
import com.medicalai.corebackend.entity.ImageAnalysis;
import com.medicalai.corebackend.entity.enums.ConsultationStatus;
import com.medicalai.corebackend.entity.enums.MessageSender;
import com.medicalai.corebackend.repository.ChatMessageRepository;
import com.medicalai.corebackend.repository.ConsultationRepository;
import com.medicalai.corebackend.repository.ImageAnalysisRepository;
import com.medicalai.corebackend.repository.DocumentAnalysisRepository;
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

    // URL'leri bulmak için Repoları ekledik
    private final ImageAnalysisRepository imageAnalysisRepository;
    private final DocumentAnalysisRepository documentAnalysisRepository;

    @Transactional
    public ChatMessageResponse sendMessage(String consultationId, ChatMessageRequest request) {
        Consultation consultation = consultationRepository.findById(consultationId)
                .orElseThrow(() -> new RuntimeException("Muayene bulunamadı: " + consultationId));

        if (consultation.getStatus() == ConsultationStatus.CLOSED) {
            throw new RuntimeException("Bu muayene kapatılmış! Yeni mesaj gönderilemez.");
        }

        // 1. DOKTORUN MESAJINI KAYDET (Veritabanında ID tutmak mantıklı, ilişkisel veri için)
        ChatMessage doctorMessage = ChatMessage.builder()
                .consultation(consultation)
                .senderRole(MessageSender.DOCTOR)
                .messageContent(request.messageContent())
                .imageAnalysisId(request.imageAnalysisId())
                .documentAnalysisId(request.documentAnalysisId())
                .build();
        chatMessageRepository.save(doctorMessage);

        // --- ID'LERİ URL'YE ÇEVİRME İŞLEMİ (SENİN HARİKA UYARIN) ---
        String imageUrl = null;
        if (request.imageAnalysisId() != null) {
            imageUrl = imageAnalysisRepository.findById(request.imageAnalysisId())
                    .map(ImageAnalysis::getOriginalImageUrl)
                    .orElse(null);
        }

        String documentUrl = null;
        if (request.documentAnalysisId() != null) {
            documentUrl = documentAnalysisRepository.findById(request.documentAnalysisId())
                    .map(DocumentAnalysis::getDocumentUrl)
                    .orElse(null);
        }

        // 2. PYTHON FASTAPI'YE GERÇEK HTTP İSTEĞİ AT (Artık URL'ler gidiyor)
        AiAgentRequest aiRequest = new AiAgentRequest(
                consultationId,
                request.messageContent(),
                imageUrl,      // Python direkt resmi okuyacak
                documentUrl    // Python direkt PDF'i okuyacak
        );

        AiAgentResponse aiResponse = aiIntegrationService.askFastApi(aiRequest);

        // 3. PYTHON'DAN GELEN CEVABI AI OLARAK KAYDET
        ChatMessage aiMessage = ChatMessage.builder()
                .consultation(consultation)
                .senderRole(MessageSender.AI)
                .messageContent(aiResponse.aiMessage())
                .citedSources(aiResponse.sources())
                .imageAnalysisId(request.imageAnalysisId())
                .documentAnalysisId(request.documentAnalysisId())
                .build();

        ChatMessage savedAiMessage = chatMessageRepository.save(aiMessage);
        return mapToResponse(savedAiMessage);
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