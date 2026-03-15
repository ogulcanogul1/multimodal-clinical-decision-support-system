package com.medicalai.corebackend.dto.response;

import com.medicalai.corebackend.entity.enums.MessageSender;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

public record ChatMessageResponse(
        String id,
        MessageSender senderRole,
        String messageContent,
        List<Map<String, Object>> citedSources,
        String imageAnalysisId,
        String documentAnalysisId,
        LocalDateTime timestamp
) {}
