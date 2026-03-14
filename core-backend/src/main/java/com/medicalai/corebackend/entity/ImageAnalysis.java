package com.medicalai.corebackend.entity;

import com.medicalai.corebackend.entity.enums.AnalysisType;
import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "image_analyses")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ImageAnalysis {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "consultation_id", nullable = false)
    private Consultation consultation;

    @Column(nullable = false, length = 500)
    private String originalImageUrl; // S3/MinIO'daki orijinal röntgen linki

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 50)
    private AnalysisType analysisType; // XRAY vb.

    @Column(length = 100)
    private String aiPrediction; // Modelin tahmini

    private Double confidenceScore; // Örn: 0.98

    @Column(length = 500)
    private String heatmapUrl; // Grad-CAM açıklanabilir AI ısı haritası linki

    private Boolean doctorFeedback; // Doktor bu teşhisi onayladı mı? (True/False)

    @Column(updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
    }
}