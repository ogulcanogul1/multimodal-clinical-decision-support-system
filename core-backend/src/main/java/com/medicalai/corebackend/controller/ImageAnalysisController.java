package com.medicalai.corebackend.controller;

import com.medicalai.corebackend.dto.request.AiResultUpdateRequest;
import com.medicalai.corebackend.dto.request.ImageAnalysisRequest;
import com.medicalai.corebackend.dto.response.ImageAnalysisResponse;
import com.medicalai.corebackend.service.ImageAnalysisService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/image-analysis")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class ImageAnalysisController {

    private final ImageAnalysisService imageAnalysisService;

    // 1. Yeni görüntü kaydı (yüklendikten sonra URL'si buraya atılır)
    @PostMapping
    public ResponseEntity<ImageAnalysisResponse> createAnalysis(@Valid @RequestBody ImageAnalysisRequest request) {
        return new ResponseEntity<>(imageAnalysisService.createImageAnalysis(request), HttpStatus.CREATED);
    }

    // 2. Python'dan dönecek AI sonuçlarını kaydetme (Genelde arka planda / webhook ile tetiklenir)
    @PatchMapping("/{id}/ai-results")
    public ResponseEntity<ImageAnalysisResponse> updateAiResults(
            @PathVariable String id,
            @RequestBody AiResultUpdateRequest request) {
        return ResponseEntity.ok(imageAnalysisService.updateAiResults(id, request));
    }

    // 3. Doktorun AI sonucuna geri bildirim vermesi
    @PatchMapping("/{id}/feedback")
    public ResponseEntity<ImageAnalysisResponse> submitFeedback(
            @PathVariable String id,
            @RequestParam boolean isApproved) {
        return ResponseEntity.ok(imageAnalysisService.submitDoctorFeedback(id, isApproved));
    }

    // 4. Muayeneye ait tüm görüntü analizlerini listeleme
    @GetMapping("/consultation/{consultationId}")
    public ResponseEntity<List<ImageAnalysisResponse>> getByConsultation(@PathVariable String consultationId) {
        return ResponseEntity.ok(imageAnalysisService.getAnalysesByConsultation(consultationId));
    }
}