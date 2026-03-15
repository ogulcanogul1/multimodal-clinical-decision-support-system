package com.medicalai.corebackend.controller;

import com.medicalai.corebackend.dto.request.ChatMessageRequest;
import com.medicalai.corebackend.dto.response.ChatMessageResponse;
import com.medicalai.corebackend.service.ChatMessageService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/chat")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class ChatMessageController {

    private final ChatMessageService chatMessageService;

    // Doktor mesaj atar, sistem hem doktorun mesajını kaydeder hem de AI cevabını dönüp kaydeder.
    @PostMapping("/consultation/{consultationId}/send")
    public ResponseEntity<ChatMessageResponse> sendMessage(
            @PathVariable String consultationId,
            @Valid @RequestBody ChatMessageRequest request) {

        // Dönüş olarak AI'ın cevabını veriyoruz (Frontend ekrana basabilsin diye)
        return new ResponseEntity<>(chatMessageService.sendMessage(consultationId, request), HttpStatus.CREATED);
    }

    // Muayene odası açıldığında eski mesajları (Sohbet Geçmişini) listeler
    @GetMapping("/consultation/{consultationId}")
    public ResponseEntity<List<ChatMessageResponse>> getChatHistory(@PathVariable String consultationId) {
        return ResponseEntity.ok(chatMessageService.getChatHistory(consultationId));
    }
}
