package com.medicalai.corebackend.entity;

import com.medicalai.corebackend.entity.enums.MessageSender;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

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

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "consultation_id", nullable = false)
    private Consultation consultation;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private MessageSender senderRole; // DOCTOR veya AI

    @Column(columnDefinition = "TEXT", nullable = false)
    private String messageContent;

    // HATA ALMAMAK İÇİN STRING YERİNE LIST<MAP> YAPTIK!
    // Pinecone'dan dönen: [ {"source": "ESC", "page": 15} ]
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "jsonb")
    private List<Map<String, Object>> citedSources;

    // --- MULTIMODAL BAĞLANTILARI (Opsiyonel) ---
    @Column(name = "image_analysis_id")
    private String imageAnalysisId; // Eğer röntgen soruluyorsa

    @Column(name = "document_analysis_id")
    private String documentAnalysisId; // Eğer kan tahlili/PDF soruluyorsa

    @Column(nullable = false, updatable = false)
    private LocalDateTime timestamp;

    @PrePersist
    protected void onCreate() {
        this.timestamp = LocalDateTime.now();
    }
}