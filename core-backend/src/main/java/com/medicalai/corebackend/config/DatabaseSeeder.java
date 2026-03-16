package com.medicalai.corebackend.config;

import com.medicalai.corebackend.entity.Allergy;
import com.medicalai.corebackend.entity.Disease;
import com.medicalai.corebackend.entity.Medication;
import com.medicalai.corebackend.repository.AllergyRepository;
import com.medicalai.corebackend.repository.DiseaseRepository;
import com.medicalai.corebackend.repository.MedicationRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
@RequiredArgsConstructor
public class DatabaseSeeder implements CommandLineRunner {

    private final DiseaseRepository diseaseRepository;
    private final AllergyRepository allergyRepository;
    private final MedicationRepository medicationRepository;

    @Override
    public void run(String... args) throws Exception {
        System.out.println("\n🌱 [DATABASE SEEDER] Veritabanı kontrol ediliyor...");

        try {
            seedDiseases();
            seedAllergies();
            seedMedications();
            System.out.println("✅ [DATABASE SEEDER] Başlangıç verileri hazır.\n");
        } catch (Exception e) {
            System.err.println("❌ [DATABASE SEEDER] Veri eklenirken kritik bir hata oluştu: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private void seedDiseases() {
        long count = diseaseRepository.count();
        System.out.println(" 🔍 Hastalık Tablosu Kayıt Sayısı: " + count);

        if (count == 0) {
            List<Disease> diseases = List.of(
                    Disease.builder().name("Tip 2 Diyabet (Type 2 Diabetes)").build(),
                    Disease.builder().name("Hipertansiyon (Hypertension)").build(),
                    Disease.builder().name("Astım (Asthma)").build(),
                    Disease.builder().name("KOAH (COPD)").build(),
                    Disease.builder().name("Koroner Arter Hastalığı (CAD)").build()
            );
            diseaseRepository.saveAll(diseases);
            System.out.println(" ➔ Hastalık (Disease) sözlüğü oluşturuldu.");
        } else {
            System.out.println(" ⚠️ Hastalık tablosu zaten dolu, atlanıyor.");
        }
    }

    private void seedAllergies() {
        long count = allergyRepository.count();
        System.out.println(" 🔍 Alerji Tablosu Kayıt Sayısı: " + count);

        if (count == 0) {
            List<Allergy> allergies = List.of(
                    Allergy.builder().name("Penisilin (Penicillin)").build(),
                    Allergy.builder().name("Yer Fıstığı (Peanut)").build(),
                    Allergy.builder().name("Polen (Pollen)").build(),
                    Allergy.builder().name("Arı Zehri (Bee Sting)").build(),
                    Allergy.builder().name("Lateks (Latex)").build()
            );
            allergyRepository.saveAll(allergies);
            System.out.println(" ➔ Alerji (Allergy) sözlüğü oluşturuldu.");
        } else {
            System.out.println(" ⚠️ Alerji tablosu zaten dolu, atlanıyor.");
        }
    }

    private void seedMedications() {
        long count = medicationRepository.count();
        System.out.println(" 🔍 İlaç Tablosu Kayıt Sayısı: " + count);

        if (count == 0) {
            List<Medication> medications = List.of(
                    Medication.builder().name("Metformin 1000mg").build(),
                    Medication.builder().name("Lisinopril 10mg").build(),
                    Medication.builder().name("Albuterol Inhaler").build(),
                    Medication.builder().name("Aspirin 81mg").build(),
                    Medication.builder().name("Atorvastatin 20mg").build()
            );
            medicationRepository.saveAll(medications);
            System.out.println(" ➔ İlaç (Medication) sözlüğü oluşturuldu.");
        } else {
            System.out.println(" ⚠️ İlaç tablosu zaten dolu, atlanıyor.");
        }
    }
}