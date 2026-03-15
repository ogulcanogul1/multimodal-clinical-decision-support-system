package com.medicalai.corebackend.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "diseases_dictionary")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Disease {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String name; // Örn: "Tip 2 Diyabet"

    @Column(unique = true)
    private String icd10Code; // Örn: "E11.9" (Opsiyonel ama çok profesyonel)
}