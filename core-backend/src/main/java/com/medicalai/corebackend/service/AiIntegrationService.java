package com.medicalai.corebackend.service;

import com.medicalai.corebackend.dto.request.AiAgentRequest;
import com.medicalai.corebackend.dto.response.AiAgentResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
@RequiredArgsConstructor
public class AiIntegrationService {

    private final RestTemplate restTemplate;

    // application.yml'dan Python sunucunun adresini alıyoruz
    // Örn: http://localhost:8000/api/v1/agent/chat
    @Value("${app.python-agent.url:http://localhost:8000/api/agent/chat}")
    private String pythonAgentUrl;

    public AiAgentResponse askFastApi(AiAgentRequest request) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<AiAgentRequest> requestEntity = new HttpEntity<>(request, headers);

        try {
            // Python'a POST isteği atıyoruz
            ResponseEntity<AiAgentResponse> response = restTemplate.postForEntity(
                    pythonAgentUrl,
                    requestEntity,
                    AiAgentResponse.class
            );
            return response.getBody();

        } catch (Exception e) {
            // Python tarafı çökerse veya kapalıysa Java patlamasın diye hata yönetimi
            throw new RuntimeException("Python Yapay Zeka sunucusuna bağlanılamadı: " + e.getMessage());
        }
    }
}
