package com.aether.auth.global.config;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.*;

class JwtPropertiesTest {

    @Nested
    @DisplayName("JWT Secret 검증")
    class SecretValidation {

        @Test
        @DisplayName("시크릿 미설정 시 시작 실패")
        void validate_NullSecret_ThrowsException() {
            JwtProperties props = new JwtProperties();
            props.setSecret(null);
            props.setAccessExpiration(1800000L);
            props.setRefreshExpiration(604800000L);

            assertThatThrownBy(props::validate)
                    .isInstanceOf(IllegalStateException.class)
                    .hasMessageContaining("JWT_SECRET is not set");
        }

        @Test
        @DisplayName("빈 시크릿 시 시작 실패")
        void validate_BlankSecret_ThrowsException() {
            JwtProperties props = new JwtProperties();
            props.setSecret("   ");
            props.setAccessExpiration(1800000L);
            props.setRefreshExpiration(604800000L);

            assertThatThrownBy(props::validate)
                    .isInstanceOf(IllegalStateException.class)
                    .hasMessageContaining("JWT_SECRET is not set");
        }

        @Test
        @DisplayName("짧은 시크릿(64바이트 미만) 시 시작 실패")
        void validate_ShortSecret_ThrowsException() {
            JwtProperties props = new JwtProperties();
            props.setSecret("too-short-key");
            props.setAccessExpiration(1800000L);
            props.setRefreshExpiration(604800000L);

            assertThatThrownBy(props::validate)
                    .isInstanceOf(IllegalStateException.class)
                    .hasMessageContaining("too short");
        }

        @Test
        @DisplayName("정상 시크릿으로 검증 통과")
        void validate_ValidSecret_Success() {
            JwtProperties props = new JwtProperties();
            props.setSecret("aether-jwt-test-secret-key-64-bytes-minimum-for-hmac-sha512-algo!");
            props.setAccessExpiration(1800000L);
            props.setRefreshExpiration(604800000L);

            assertThatCode(props::validate).doesNotThrowAnyException();
        }

        @Test
        @DisplayName("정확히 64바이트 시크릿 통과 (HS512 경계)")
        void validate_Exactly64Bytes_Success() {
            JwtProperties props = new JwtProperties();
            props.setSecret("a".repeat(64)); // 64 bytes — HS512 최소 길이
            props.setAccessExpiration(1800000L);
            props.setRefreshExpiration(604800000L);

            assertThatCode(props::validate).doesNotThrowAnyException();
        }

        @Test
        @DisplayName("63바이트 시크릿 거부 (HS512 경계 바로 아래 — 알고리즘 다운그레이드 차단)")
        void validate_63Bytes_ThrowsException() {
            JwtProperties props = new JwtProperties();
            props.setSecret("a".repeat(63)); // 63 bytes — 64 미만이므로 거부되어야 함
            props.setAccessExpiration(1800000L);
            props.setRefreshExpiration(604800000L);

            assertThatThrownBy(props::validate)
                    .isInstanceOf(IllegalStateException.class)
                    .hasMessageContaining("too short");
        }
    }
}
