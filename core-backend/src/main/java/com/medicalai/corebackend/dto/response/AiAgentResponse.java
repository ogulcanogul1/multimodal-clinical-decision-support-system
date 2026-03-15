package com.medicalai.corebackend.dto.response;

import java.util.List;
import java.util.Map;

public record AiAgentResponse(
        String aiMessage,
        List<Map<String, Object>> sources // Python'dan gelecek JSON listesi
) {}
