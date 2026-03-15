package com.medicalai.corebackend.controller;

import com.medicalai.corebackend.dto.request.AiResultUpdateRequest;
import com.medicalai.corebackend.dto.response.ImageAnalysisResponse;
import com.medicalai.corebackend.entity.enums.AnalysisType;
import com.medicalai.corebackend.service.ImageAnalysisService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@RestController
@RequestMapping("/api/image-analysis")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class ImageAnalysisController {

    private final ImageAnalysisService imageAnalysisService;

    /**
     * 1. Yeni Görüntü Yükleme (Doktor tarafından)
     * JSON beklemiyoruz, form-data (dosya) bekliyoruz.
     * POST /api/image-analysis
     */
    @PostMapping(consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<ImageAnalysisResponse> createAnalysis(
            @RequestParam("consultationId") String consultationId,
            @RequestParam("analysisType") AnalysisType analysisType,
            @RequestParam("file") MultipartFile file) {

        if (file.isEmpty()) {
            throw new RuntimeException("Lütfen yüklenecek bir görüntü dosyası seçin!");
        }

        ImageAnalysisResponse response = imageAnalysisService.createImageAnalysis(consultationId, analysisType, file);
        return new ResponseEntity<>(response, HttpStatus.CREATED);
    }

    /**
     * 2. Python'dan dönecek AI sonuçlarını kaydetme
     * Genelde FastAPI tarafından atılacak arka plan isteğidir.
     * PATCH /api/image-analysis/{id}/ai-results
     */
    @PatchMapping("/{id}/ai-results")
    public ResponseEntity<ImageAnalysisResponse> updateAiResults(
            @PathVariable String id,
            @RequestBody AiResultUpdateRequest request) {

        return ResponseEntity.ok(imageAnalysisService.updateAiResults(id, request));
    }

    /**
     * 3. Doktorun AI sonucuna onay/red vermesi (RLHF)
     * PATCH /api/image-analysis/{id}/feedback?isApproved=true
     */
    @PatchMapping("/{id}/feedback")
    public ResponseEntity<ImageAnalysisResponse> submitFeedback(
            @PathVariable String id,
            @RequestParam boolean isApproved) {

        return ResponseEntity.ok(imageAnalysisService.submitDoctorFeedback(id, isApproved));
    }

    /**
     * 4. Bir muayeneye ait tüm görüntü analizlerini listeleme
     * GET /api/image-analysis/consultation/{consultationId}
     */
    @GetMapping("/consultation/{consultationId}")
    public ResponseEntity<List<ImageAnalysisResponse>> getByConsultation(@PathVariable String consultationId) {
        return ResponseEntity.ok(imageAnalysisService.getAnalysesByConsultation(consultationId));
    }
}