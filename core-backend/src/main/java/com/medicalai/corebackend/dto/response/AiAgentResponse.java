package com.medicalai.corebackend.dto.response;

import java.util.List;
import java.util.Map;

public record AiAgentResponse(
        String aiMessage,
        List<Map<String, Object>> sources, // RAG kaynakları

        // --- GÖRÜNTÜ ANALİZİ (X-RAY vb.) SONUÇLARI (Opsiyonel) ---
        String imagePrediction,
        Double imageConfidenceScore,
        String heatmapUrl, // Python ısı haritasını MinIO/diske kaydedip linkini bize dönecek

        // --- BELGE/TAHLİL ANALİZİ SONUÇLARI (Opsiyonel) ---
        String documentPrediction,
        Double documentConfidenceScore,
        Map<String, Object> featureImportance // Hangi değerler etkili oldu?
) {}
