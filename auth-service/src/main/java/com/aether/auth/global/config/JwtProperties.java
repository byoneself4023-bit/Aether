package com.aether.auth.global.config;

import jakarta.annotation.PostConstruct;
import lombok.Getter;
import lombok.Setter;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.context.properties.ConfigurationProperties;

import java.nio.charset.StandardCharsets;

@Slf4j
@ConfigurationProperties(prefix = "jwt")
@Getter
@Setter
public class JwtProperties {

    private static final int MINIMUM_SECRET_LENGTH = 32;

    private String secret;
    private long accessExpiration;
    private long refreshExpiration;

    @PostConstruct
    public void validate() {
        if (secret == null || secret.isBlank()) {
            throw new IllegalStateException(
                    "JWT_SECRET is not set. "
                    + "Please set the JWT_SECRET environment variable. "
                    + "The secret must be at least " + MINIMUM_SECRET_LENGTH + " characters long."
            );
        }
        if (secret.getBytes(StandardCharsets.UTF_8).length < MINIMUM_SECRET_LENGTH) {
            throw new IllegalStateException(
                    "JWT_SECRET is too short. "
                    + "The secret must be at least " + MINIMUM_SECRET_LENGTH + " bytes for HMAC-SHA256."
            );
        }
        log.info("JWT properties validated: accessExpiration={}ms, refreshExpiration={}ms",
                accessExpiration, refreshExpiration);
    }
}
