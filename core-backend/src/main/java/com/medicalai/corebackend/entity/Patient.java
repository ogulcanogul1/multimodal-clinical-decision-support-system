package com.medicalai.corebackend.entity;

import com.medicalai.corebackend.entity.enums.BloodType;
import com.medicalai.corebackend.entity.enums.Gender;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.Period;
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

    // 1. Kronik Hastalıklar (Many-To-Many)
    @ManyToMany(fetch = FetchType.LAZY)
    @JoinTable(
            name = "patient_chronic_diseases", // Kesişim tablosu
            joinColumns = @JoinColumn(name = "patient_id"),
            inverseJoinColumns = @JoinColumn(name = "disease_id")
    )
    private List<Disease> chronicDiseases;

    // 2. Alerjiler (Many-To-Many)
    @ManyToMany(fetch = FetchType.LAZY)
    @JoinTable(
            name = "patient_allergies",
            joinColumns = @JoinColumn(name = "patient_id"),
            inverseJoinColumns = @JoinColumn(name = "allergy_id")
    )
    private List<Allergy> allergies;

    // 3. Kullanılan İlaçlar (Many-To-Many)
    @ManyToMany(fetch = FetchType.LAZY)
    @JoinTable(
            name = "patient_medications",
            joinColumns = @JoinColumn(name = "patient_id"),
            inverseJoinColumns = @JoinColumn(name = "medication_id")
    )
    private List<Medication> currentMedications;

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

    public Integer getAge() {
        if (this.dateOfBirth == null) {
            return null; // Eğer doğum tarihi girilmemişse sistem çökmesin
        }
        return Period.between(this.dateOfBirth, LocalDate.now()).getYears();
    }
}

