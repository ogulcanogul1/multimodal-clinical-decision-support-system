package com.medicalai.corebackend.entity;

import com.medicalai.corebackend.entity.enums.BloodType;
import com.medicalai.corebackend.entity.enums.Gender;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "patients")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Patient {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    @Column(nullable = false, length = 11, unique = true)
    private String nationalId;

    @Column(nullable = false, length = 50)
    private String firstName;

    @Column(nullable = false, length = 50)
    private String lastName;

    @Column(nullable = false)
    private LocalDate dateOfBirth;

    @Enumerated(EnumType.STRING)
    @Column(length = 20)
    private Gender gender;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false,length = 20)
    private BloodType bloodType;

    @ElementCollection(fetch = FetchType.EAGER) // RAG yaparken hemen gelsin diye EAGER yapabilirsin
    @CollectionTable(name = "patient_chronic_diseases", joinColumns = @JoinColumn(name = "patient_id"))
    @Column(name = "disease_name")
    private List<String> chronicDiseases;

    // 2. Alerjiler Tablosu
    @ElementCollection(fetch = FetchType.EAGER)
    @CollectionTable(name = "patient_allergies", joinColumns = @JoinColumn(name = "patient_id"))
    @Column(name = "allergy_name")
    private List<String> allergies;

    // 3. Kullanılan İlaçlar Tablosu
    @ElementCollection(fetch = FetchType.EAGER)
    @CollectionTable(name = "patient_medications", joinColumns = @JoinColumn(name = "patient_id"))
    @Column(name = "medication_name")
    private List<String> currentMedications;

    @Column(updatable = false)
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }

    public String getFullName() {
        return firstName + " " + lastName;
    }
}
