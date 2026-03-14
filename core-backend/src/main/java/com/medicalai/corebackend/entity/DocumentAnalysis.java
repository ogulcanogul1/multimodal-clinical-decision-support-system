package com.medicalai.corebackend.entity;


import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;
import java.time.LocalDateTime;

@Entity
@Table(name = "document_analyses")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DocumentAnalysis {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "consultation_id", nullable = false)
    private Consultation consultation;

    @Column(nullable = false, length = 500)
    private String documentUrl; // S3/MinIO'daki orijinal PDF'in linki

    @Column(length = 50)
    private String documentType; // BLOOD_TEST, EKG_REPORT, CLINICAL_NOTE vb.

    @Column(length = 100)
    private String mlpPrediction; // MLP modelinin tahmini (Örn: Diyabet Riski Yüksek)

    private Double confidenceScore; // Örn: 0.85

    // Açıklanabilir Yapay Zeka (XAI) için: Hangi değerler bu sonuca etki etti?
    // Örn: {"glucose": "high_impact", "age": "medium_impact"}
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "jsonb")
    private String featureImportance;

    private Boolean doctorFeedback; // Doktor onayladı mı?

    @Column(updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
    }
}