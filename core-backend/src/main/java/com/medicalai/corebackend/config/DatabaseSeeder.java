package com.medicalai.corebackend.config;

import com.medicalai.corebackend.entity.Allergy;
import com.medicalai.corebackend.entity.Disease;
import com.medicalai.corebackend.entity.Doctor;
import com.medicalai.corebackend.entity.Medication;
import com.medicalai.corebackend.entity.Patient;
import com.medicalai.corebackend.entity.enums.BloodType;
import com.medicalai.corebackend.entity.enums.Gender;
import com.medicalai.corebackend.entity.enums.Specialty;
import com.medicalai.corebackend.repository.AllergyRepository;
import com.medicalai.corebackend.repository.DiseaseRepository;
import com.medicalai.corebackend.repository.DoctorRepository;
import com.medicalai.corebackend.repository.MedicationRepository;
import com.medicalai.corebackend.repository.PatientRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import java.time.LocalDate;
import java.util.List;

@Component
@RequiredArgsConstructor
public class DatabaseSeeder implements CommandLineRunner {

    private final DiseaseRepository diseaseRepository;
    private final AllergyRepository allergyRepository;
    private final MedicationRepository medicationRepository;
    private final DoctorRepository doctorRepository;
    private final PatientRepository patientRepository;
    private final PasswordEncoder passwordEncoder;

    @Override
    public void run(String... args) throws Exception {
        System.out.println("\n🌱 [DATABASE SEEDER] Veritabanı kontrol ediliyor...");

        try {
            seedDiseases();
            seedAllergies();
            seedMedications();
            seedTestDoctor();
            seedPatients();
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

    private void seedTestDoctor() {
        String testEmail = "test@medicalai.com";
        if (!doctorRepository.existsByEmail(testEmail)) {
            Doctor testDoctor = Doctor.builder()
                    .email(testEmail)
                    .passwordHash(passwordEncoder.encode("Test@1234"))
                    .firstName("Test")
                    .lastName("Doktor")
                    .specialty(Specialty.INTERNAL_MEDICINE)
                    .licenseNumber("LIC-00001")
                    .build();
            doctorRepository.save(testDoctor);
            System.out.println(" ➔ Test doktor hesabı oluşturuldu: " + testEmail);
        } else {
            System.out.println(" ⚠️ Test doktor zaten mevcut, atlanıyor.");
        }
    }

    private void seedPatients() {
        long count = patientRepository.count();
        System.out.println(" 🔍 Hasta Tablosu Kayıt Sayısı: " + count);

        if (count > 0) {
            System.out.println(" ⚠️ Hasta tablosu zaten dolu, atlanıyor.");
            return;
        }

        // Sözlük kayıtlarını isimleriyle eşle (seed sırası garanti değil, isimle bul)
        List<Disease> diseases = diseaseRepository.findAll();
        List<Allergy> allergies = allergyRepository.findAll();
        List<Medication> medications = medicationRepository.findAll();

        Disease diyabet = findByName(diseases, "Tip 2 Diyabet", Disease::getName);
        Disease hipertansiyon = findByName(diseases, "Hipertansiyon", Disease::getName);
        Disease astim = findByName(diseases, "Astım", Disease::getName);
        Disease koah = findByName(diseases, "KOAH", Disease::getName);
        Disease kah = findByName(diseases, "Koroner Arter", Disease::getName);

        Allergy penisilin = findByName(allergies, "Penisilin", Allergy::getName);
        Allergy yerFistigi = findByName(allergies, "Yer Fıstığı", Allergy::getName);
        Allergy polen = findByName(allergies, "Polen", Allergy::getName);

        Medication metformin = findByName(medications, "Metformin", Medication::getName);
        Medication lisinopril = findByName(medications, "Lisinopril", Medication::getName);
        Medication albuterol = findByName(medications, "Albuterol", Medication::getName);
        Medication aspirin = findByName(medications, "Aspirin", Medication::getName);
        Medication atorvastatin = findByName(medications, "Atorvastatin", Medication::getName);

        List<Patient> patients = List.of(
                Patient.builder()
                        .nationalId("10000000001")
                        .firstName("Ahmet")
                        .lastName("Yılmaz")
                        .dateOfBirth(LocalDate.of(1958, 3, 12))
                        .gender(Gender.MALE)
                        .bloodType(BloodType.A_POSITIVE)
                        .chronicDiseases(nonNullList(diyabet, hipertansiyon))
                        .allergies(nonNullList(penisilin))
                        .currentMedications(nonNullList(metformin, lisinopril))
                        .build(),
                Patient.builder()
                        .nationalId("10000000002")
                        .firstName("Ayşe")
                        .lastName("Kaya")
                        .dateOfBirth(LocalDate.of(1985, 11, 4))
                        .gender(Gender.FEMALE)
                        .bloodType(BloodType.O_NEGATIVE)
                        .chronicDiseases(nonNullList(astim))
                        .allergies(nonNullList(polen, yerFistigi))
                        .currentMedications(nonNullList(albuterol))
                        .build(),
                Patient.builder()
                        .nationalId("10000000003")
                        .firstName("Mehmet")
                        .lastName("Demir")
                        .dateOfBirth(LocalDate.of(1949, 7, 23))
                        .gender(Gender.MALE)
                        .bloodType(BloodType.B_POSITIVE)
                        .chronicDiseases(nonNullList(kah, hipertansiyon, koah))
                        .allergies(nonNullList())
                        .currentMedications(nonNullList(aspirin, atorvastatin))
                        .build(),
                Patient.builder()
                        .nationalId("10000000004")
                        .firstName("Zeynep")
                        .lastName("Şahin")
                        .dateOfBirth(LocalDate.of(1996, 1, 30))
                        .gender(Gender.FEMALE)
                        .bloodType(BloodType.AB_POSITIVE)
                        .chronicDiseases(nonNullList())
                        .allergies(nonNullList(penisilin))
                        .currentMedications(nonNullList())
                        .build()
        );

        patientRepository.saveAll(patients);
        System.out.println(" ➔ Örnek hasta verileri oluşturuldu (" + patients.size() + " hasta).");
    }

    // Sözlük listesinde isim parçasına göre eşleşeni bul (bulunamazsa null)
    private <T> T findByName(List<T> items, String namePart, java.util.function.Function<T, String> nameGetter) {
        return items.stream()
                .filter(i -> nameGetter.apply(i) != null && nameGetter.apply(i).contains(namePart))
                .findFirst()
                .orElse(null);
    }

    // null elemanları eleyerek mutable bir liste oluştur (ManyToMany için)
    @SafeVarargs
    private <T> List<T> nonNullList(T... items) {
        return java.util.Arrays.stream(items)
                .filter(java.util.Objects::nonNull)
                .collect(java.util.stream.Collectors.toCollection(java.util.ArrayList::new));
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