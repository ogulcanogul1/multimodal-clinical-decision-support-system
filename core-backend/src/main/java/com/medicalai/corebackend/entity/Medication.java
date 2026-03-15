package com.medicalai.corebackend.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "medications_dictionary")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Medication {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String name; // Örn: "Metformin 1000mg"
}
