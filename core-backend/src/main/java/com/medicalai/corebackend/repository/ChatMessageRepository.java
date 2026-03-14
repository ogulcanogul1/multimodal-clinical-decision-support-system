package com.medicalai.corebackend.repository;

import com.medicalai.corebackend.entity.ChatMessage;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ChatMessageRepository extends JpaRepository<ChatMessage, String> {

    // Belirli bir muayeneye ait mesajları, atılma sırasına (zamanına) göre baştan sona getir.
    // Python LangGraph'a geçmiş (history) gönderirken bu listeyi kullanacağız!
    List<ChatMessage> findByConsultationIdOrderByTimestampAsc(String consultationId);
}