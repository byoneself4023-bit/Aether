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

    // HS512 명시 통일: 512비트(64바이트) 키 강제. 32~63B면 Java가 HS256/384로 다운그레이드 → Python(HS512)과 불일치
    private static final int MINIMUM_SECRET_LENGTH = 64;

    private String secret;
    private long accessExpiration;
    private long refreshExpiration;

    @PostConstruct
    public void validate() {
        if (secret == null || secret.isBlank()) {
            throw new IllegalStateException(
                    "JWT_SECRET is not set. "
                    + "Please set the JWT_SECRET environment variable. "
                    + "The secret must be at least " + MINIMUM_SECRET_LENGTH + " bytes long."
            );
        }
        if (secret.getBytes(StandardCharsets.UTF_8).length < MINIMUM_SECRET_LENGTH) {
            throw new IllegalStateException(
                    "JWT_SECRET is too short. "
                    + "The secret must be at least " + MINIMUM_SECRET_LENGTH + " bytes for HMAC-SHA512."
            );
        }
        log.info("JWT properties validated: accessExpiration={}ms, refreshExpiration={}ms",
                accessExpiration, refreshExpiration);
    }
}
