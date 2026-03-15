package com.medicalai.corebackend.dto.request;

import java.util.List;

public record AiAgentRequest(
        String messageContent, // Doktorun anlık sorusu
        String imageUrl,
        String documentUrl,
        String chiefComplaint, // Hastanın ana şikayeti

        // --- KLİNİK BAĞLAM (Hasta Verileri) ---
        Integer patientAge,
        String patientGender,
        String bloodType,
        List<String> chronicDiseases,
        List<String> allergies,
        List<String> currentMedications,

        // --- SOHBET GEÇMİŞİ (Context) ---
        List<ChatHistoryItem> chatHistory
) {
    // Sohbet geçmişi için küçük bir alt veri yapısı (Rol ve Mesaj)
    public record ChatHistoryItem(String role, String content) {}
}
