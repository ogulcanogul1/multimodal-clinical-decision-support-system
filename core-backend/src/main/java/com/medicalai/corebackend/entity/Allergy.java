package com.medicalai.corebackend.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "allergies_dictionary")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Allergy {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String name; // Örn: "Penisilin"
}