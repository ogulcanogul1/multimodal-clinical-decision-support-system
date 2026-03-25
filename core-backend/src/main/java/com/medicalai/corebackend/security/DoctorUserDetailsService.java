package com.medicalai.corebackend.security;

import com.medicalai.corebackend.entity.Doctor;
import com.medicalai.corebackend.repository.DoctorRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class DoctorUserDetailsService implements UserDetailsService {

    private final DoctorRepository doctorRepository;

    @Override
    public UserDetails loadUserByUsername(String email) throws UsernameNotFoundException {
        Doctor doctor = doctorRepository.findByEmail(email)
                .orElseThrow(() -> new UsernameNotFoundException("Doktor bulunamadı: " + email));

        return User.builder()
                .username(doctor.getEmail())
                .password(doctor.getPasswordHash())
                .roles("DOCTOR")
                .build();
    }
}
