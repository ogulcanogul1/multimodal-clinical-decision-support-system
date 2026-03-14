package com.medicalai.corebackend.entity;

import com.medicalai.corebackend.entity.enums.MessageSender;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;
import java.time.LocalDateTime;

@Entity
@Table(name = "chat_messages")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ChatMessage {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    // Mesaj hangi muayene oturumunda atıldı?
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "consultation_id", nullable = false)
    private Consultation consultation;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private MessageSender senderRole; // DOCTOR veya AI

    @Column(columnDefinition = "TEXT", nullable = false)
    private String messageContent;

    // Hibernate 6 ile gelen muazzam özellik: PostgreSQL'de native JSONB olarak tutulur!
    // İçine Pinecone'dan dönen [ {"source": "ESC", "page": 15} ] gibi referansları basacağız.
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "jsonb")
    private String citedSources;

    @Column(nullable = false, updatable = false)
    private LocalDateTime timestamp;

    @PrePersist
    protected void onCreate() {
        this.timestamp = LocalDateTime.now();
    }
}
