package com.medicalai.corebackend.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                .csrf(AbstractHttpConfigurer::disable) // Postman ile POST/PUT yapabilmek için şart
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/api/**").permitAll() // Tüm API endpointlerini dışarıya açar
                        .anyRequest().authenticated()
                );

        return http.build();
    }
}