package com.medicalai.corebackend.service;

import com.medicalai.corebackend.entity.ChatMessage;
import com.medicalai.corebackend.entity.Consultation;
import com.medicalai.corebackend.entity.enums.MessageSender;
import com.medicalai.corebackend.repository.ChatMessageRepository;
import com.medicalai.corebackend.repository.ConsultationRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class ChatMessageService {

    private final ChatMessageRepository chatMessageRepository;
    private final ConsultationRepository consultationRepository;
    // private final AiIntegrationService aiIntegrationService; // Birazdan yazacağız

    @Transactional
    public ChatMessageResponse sendMessage(String consultationId, ChatMessageRequest request) {
        // 1. Muayene kontrolü (Açık mı?)
        Consultation consultation = consultationRepository.findById(consultationId)
                .orElseThrow(() -> new RuntimeException("Muayene bulunamadı."));

        if (consultation.getStatus().name().equals("CLOSED")) {
            throw new RuntimeException("Kapatılmış bir muayene üzerinden mesaj gönderilemez!");
        }

        // 2. Doktorun mesajını kaydet
        ChatMessage doctorMessage = ChatMessage.builder()
                .consultation(consultation)
                .senderRole(MessageSender.DOCTOR)
                .messageContent(request.content())
                .build();

        chatMessageRepository.save(doctorMessage);

        // 3. AI AJANINI TETİKLE (Burada Python'a gideceğiz)
        // Şimdilik dummy bir AI cevabı oluşturuyoruz
        return askAi(consultation, request.content());
    }

    private ChatMessageResponse askAi(Consultation consultation, String userQuery) {
        // TODO: Python FastAPI entegrasyonu buraya gelecek
        ChatMessage aiResponse = ChatMessage.builder()
                .consultation(consultation)
                .senderRole(MessageSender.AI)
                .messageContent("AI Analizi: Hastanın verileri RAG üzerinden inceleniyor...")
                .citedSources("[{\"source\": \"ESC Guidelines 2023\", \"page\": 42}]") // Örnek JSONB
                .build();

        chatMessageRepository.save(aiResponse);
        return mapToResponse(aiResponse);
    }

    private ChatMessageResponse mapToResponse(ChatMessage m) {
        return new ChatMessageResponse(m.getId(), m.getSenderRole(), m.getMessageContent(), m.getCitedSources(), m.getTimestamp());
    }
}