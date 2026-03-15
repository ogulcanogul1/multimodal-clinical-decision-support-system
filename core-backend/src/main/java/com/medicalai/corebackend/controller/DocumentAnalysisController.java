package com.medicalai.corebackend.controller;

import com.medicalai.corebackend.dto.request.DocumentAiResultUpdateRequest;
import com.medicalai.corebackend.dto.response.DocumentAnalysisResponse;
import com.medicalai.corebackend.entity.enums.DocumentType;
import com.medicalai.corebackend.service.DocumentAnalysisService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@RestController
@RequestMapping("/api/document-analysis")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class DocumentAnalysisController {

    private final DocumentAnalysisService documentAnalysisService;

    @PostMapping(consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<DocumentAnalysisResponse> createAnalysis(
            @RequestParam("consultationId") String consultationId,
            @RequestParam("documentType") DocumentType documentType,
            @RequestParam("file") MultipartFile file) {

        if (file.isEmpty()) {
            throw new RuntimeException("Lütfen yüklenecek bir belge (PDF vb.) seçin!");
        }

        DocumentAnalysisResponse response = documentAnalysisService.createDocumentAnalysis(consultationId, documentType, file);
        return new ResponseEntity<>(response, HttpStatus.CREATED);
    }

    @PatchMapping("/{id}/ai-results")
    public ResponseEntity<DocumentAnalysisResponse> updateAiResults(
            @PathVariable String id,
            @RequestBody DocumentAiResultUpdateRequest request) {
        return ResponseEntity.ok(documentAnalysisService.updateAiResults(id, request));
    }

    @PatchMapping("/{id}/feedback")
    public ResponseEntity<DocumentAnalysisResponse> submitFeedback(
            @PathVariable String id,
            @RequestParam boolean isApproved) {
        return ResponseEntity.ok(documentAnalysisService.submitDoctorFeedback(id, isApproved));
    }

    @GetMapping("/consultation/{consultationId}")
    public ResponseEntity<List<DocumentAnalysisResponse>> getByConsultation(@PathVariable String consultationId) {
        return ResponseEntity.ok(documentAnalysisService.getAnalysesByConsultation(consultationId));
    }
}
