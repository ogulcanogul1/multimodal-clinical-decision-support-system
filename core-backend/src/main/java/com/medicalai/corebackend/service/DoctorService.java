package com.medicalai.corebackend.service;

import com.medicalai.corebackend.dto.request.DoctorRequest;
import com.medicalai.corebackend.dto.response.DoctorResponse;
import com.medicalai.corebackend.entity.Doctor;
import com.medicalai.corebackend.entity.enums.Specialty;
import com.medicalai.corebackend.exception.BusinessException;
import com.medicalai.corebackend.exception.ErrorCode;
import com.medicalai.corebackend.repository.DoctorRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class DoctorService {

    private final DoctorRepository doctorRepository;
    private final PasswordEncoder passwordEncoder;

    /**
     * Yeni bir doktor kaydı oluşturur.
     * Kayıttan önce email ve lisans numarası benzersizliği kontrol edilir.
     */
    @Transactional
    public DoctorResponse createDoctor(DoctorRequest request) {
        if (doctorRepository.existsByEmail(request.email())) {
            throw new BusinessException(ErrorCode.EMAIL_ALREADY_EXISTS, "Bu email adresi zaten kullanımda: " + request.email());
        }
        if (doctorRepository.existsByLicenseNumber(request.licenseNumber())) {
            throw new BusinessException(ErrorCode.LICENSE_ALREADY_EXISTS, "Bu lisans numarası sistemde zaten kayıtlı: " + request.licenseNumber());
        }

        Doctor doctor = Doctor.builder()
                .firstName(request.firstName())
                .lastName(request.lastName())
                .email(request.email())
                .licenseNumber(request.licenseNumber())
                .specialty(request.specialty())
                .passwordHash(passwordEncoder.encode(request.password()))
                .build();

        Doctor savedDoctor = doctorRepository.save(doctor);
        return mapToResponse(savedDoctor);
    }

    /**
     * Veritabanı ID'si (UUID) ile doktor getirir.
     */
    @Transactional(readOnly = true)
    public DoctorResponse getDoctorById(String id) {
        return doctorRepository.findById(id)
                .map(this::mapToResponse)
                .orElseThrow(() -> new BusinessException(ErrorCode.DOCTOR_NOT_FOUND, "ID ile doktor bulunamadı: " + id));
    }

    /**
     * Email adresi üzerinden doktor sorgular.
     */
    @Transactional(readOnly = true)
    public DoctorResponse getDoctorByEmail(String email) {
        return doctorRepository.findByEmail(email)
                .map(this::mapToResponse)
                .orElseThrow(() -> new BusinessException(ErrorCode.DOCTOR_NOT_FOUND, "Bu email adresine sahip bir doktor bulunamadı: " + email));
    }

    /**
     * Diploma/Lisans numarası üzerinden doktor sorgular.
     */
    @Transactional(readOnly = true)
    public DoctorResponse getDoctorByLicense(String license) {
        return doctorRepository.findByLicenseNumber(license)
                .map(this::mapToResponse)
                .orElseThrow(() -> new BusinessException(ErrorCode.DOCTOR_NOT_FOUND, "Bu lisans numarasına sahip bir doktor bulunamadı: " + license));
    }

    /**
     * Belirli bir uzmanlık alanındaki tüm doktorları listeler.
     */
    @Transactional(readOnly = true)
    public List<DoctorResponse> getDoctorsBySpecialty(Specialty specialty) {
        List<Doctor> doctors = doctorRepository.findAllBySpecialty(specialty);
        return doctors.stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    /**
     * Sistemdeki tüm doktorları listeler.
     */
    @Transactional(readOnly = true)
    public List<DoctorResponse> getAllDoctors() {
        return doctorRepository.findAll().stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    /**
     * Entity nesnesini Response DTO'ya dönüştüren yardımcı metod.
     */
    private DoctorResponse mapToResponse(Doctor doctor) {
        return new DoctorResponse(
                doctor.getId(),
                doctor.getFirstName(),
                doctor.getLastName(),
                doctor.getEmail(),
                doctor.getLicenseNumber(),
                doctor.getSpecialty(),
                doctor.getCreatedAt()
        );
    }

    @Transactional
    public DoctorResponse updateDoctor(String id, DoctorRequest request) {
        Doctor existingDoctor = doctorRepository.findById(id)
                .orElseThrow(() -> new BusinessException(ErrorCode.DOCTOR_NOT_FOUND, "Güncellenecek doktor bulunamadı. ID: " + id));

        // Email değişiyorsa, yeni emailin başkasında olup olmadığını kontrol et
        if (!existingDoctor.getEmail().equals(request.email()) &&
                doctorRepository.existsByEmail(request.email())) {
            throw new BusinessException(ErrorCode.EMAIL_ALREADY_EXISTS, "Bu email adresi zaten başka bir doktor tarafından kullanılıyor!");
        }

        // Lisans numarası değişiyorsa kontrol et
        if (!existingDoctor.getLicenseNumber().equals(request.licenseNumber()) &&
                doctorRepository.existsByLicenseNumber(request.licenseNumber())) {
            throw new BusinessException(ErrorCode.LICENSE_ALREADY_EXISTS, "Bu lisans numarası zaten başka bir doktora kayıtlı!");
        }

        // Alanları güncelle
        existingDoctor.setFirstName(request.firstName());
        existingDoctor.setLastName(request.lastName());
        existingDoctor.setEmail(request.email());
        existingDoctor.setLicenseNumber(request.licenseNumber());
        existingDoctor.setSpecialty(request.specialty());

        // Şifre boş değilse güncelle (Opsiyonel: Boş gelirse eski şifre kalsın denebilir)
        if (request.password() != null && !request.password().isBlank()) {
            existingDoctor.setPasswordHash(passwordEncoder.encode(request.password()));
        }

        Doctor updated = doctorRepository.save(existingDoctor);
        return mapToResponse(updated);
    }
}
