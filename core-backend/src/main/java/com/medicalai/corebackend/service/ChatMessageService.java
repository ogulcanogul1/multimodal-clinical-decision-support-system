package com.medicalai.corebackend.service;

import com.medicalai.corebackend.dto.request.ChatMessageRequest;
import com.medicalai.corebackend.dto.response.ChatMessageResponse;
import com.medicalai.corebackend.entity.ChatMessage;
import com.medicalai.corebackend.entity.Consultation;
import com.medicalai.corebackend.entity.enums.ConsultationStatus;
import com.medicalai.corebackend.entity.enums.MessageSender;
import com.medicalai.corebackend.repository.ChatMessageRepository;
import com.medicalai.corebackend.repository.ConsultationRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ChatMessageService {

    private final ChatMessageRepository chatMessageRepository;
    private final ConsultationRepository consultationRepository;

    @Transactional
    public ChatMessageResponse sendMessage(String consultationId, ChatMessageRequest request) {
        Consultation consultation = consultationRepository.findById(consultationId)
                .orElseThrow(() -> new RuntimeException("Muayene bulunamadı: " + consultationId));

        if (consultation.getStatus() == ConsultationStatus.CLOSED) {
            throw new RuntimeException("Bu muayene kapatılmış! Yeni mesaj gönderilemez.");
        }

        // 1. DOKTORUN MESAJINI KAYDET
        ChatMessage doctorMessage = ChatMessage.builder()
                .consultation(consultation)
                .senderRole(MessageSender.DOCTOR)
                .messageContent(request.messageContent())
                .imageAnalysisId(request.imageAnalysisId())
                .documentAnalysisId(request.documentAnalysisId())
                .build();

        chatMessageRepository.save(doctorMessage);

        // 2. YAPAY ZEKAYA (PYTHON) SOR VE CEVABI KAYDET
        return askAiAgent(consultation, request);
    }

    // Şimdilik Simülasyon: İleride buraya RestTemplate/WebClient ile Python'a giden kod gelecek
    private ChatMessageResponse askAiAgent(Consultation consultation, ChatMessageRequest userRequest) {

        // TODO: FastAPI'ye userRequest.messageContent() gönderilecek, cevap beklenecek.

        // Python'dan geldiğini varsaydığımız örnek bir JSONB kaynakça listesi:
        List<Map<String, Object>> mockSources = List.of(
                Map.of("source", "ESC Guidelines 2023", "page", 42, "relevance", 0.95)
        );

        ChatMessage aiMessage = ChatMessage.builder()
                .consultation(consultation)
                .senderRole(MessageSender.AI)
                .messageContent("Python Agent: Yüklediğiniz verilere ve RAG taramasına göre hastada pnömoni riski gözlemlenmiştir.")
                .citedSources(mockSources) // RAG Kaynakçaları
                .imageAnalysisId(userRequest.imageAnalysisId()) // Hangi analize baktığını hatırlatmak için
                .documentAnalysisId(userRequest.documentAnalysisId())
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
