package com.medicalai.corebackend.controller;

import com.medicalai.corebackend.dto.request.PatientRequest;
import com.medicalai.corebackend.entity.enums.BloodType;
import com.medicalai.corebackend.entity.enums.Gender;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import tools.jackson.databind.ObjectMapper;

import java.time.LocalDate;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class PatientControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    @DisplayName("POST - Yeni hasta kaydı başarılı olmalı ve 201 dönmeli")
    void createPatient_Success() throws Exception {
        PatientRequest request = new PatientRequest(
                "11111111111",
                "Test",
                "User",
                LocalDate.of(2000, 1, 1),
                Gender.MALE,
                BloodType.A_POSITIVE,
                "Alerji yok"
        );

        mockMvc.perform(post("/api/patients")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.nationalId").value("11111111111"))
                .andExpect(jsonPath("$.firstName").value("Test"));
    }

    @Test
    @DisplayName("POST - Geçersiz TC (11 hane değil) 400 Bad Request dönmeli")
    void createPatient_InvalidNationalId_ShouldReturn400() throws Exception {
        PatientRequest request = new PatientRequest(
                "123", // Hatalı
                "Hatalı",
                "TC",
                LocalDate.of(2000, 1, 1),
                Gender.FEMALE,
                BloodType.O_NEGATIVE,
                null
        );

        mockMvc.perform(post("/api/patients")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("GET - Kayıtlı hasta TC ile sorgulanabilmeli")
    void getPatientByNationalId_Success() throws Exception {
        // Not: Önceki testlerde kaydedilen verinin DB'de olduğunu varsayar
        // veya DB her seferinde temizleniyorsa burada önce bir kayıt atılabilir.
        mockMvc.perform(get("/api/patients/search")
                        .param("nationalId", "12345678901")) // Postman'de kaydettiğin TC
                .andExpect(status().isOk());
    }

    @Test
    @DisplayName("GET - Tüm hastalar listelenebilmeli")
    void getAllPatients_Success() throws Exception {
        mockMvc.perform(get("/api/patients"))
                .andExpect(status().isOk())
                .andExpect(content().contentType(MediaType.APPLICATION_JSON));
    }
}
