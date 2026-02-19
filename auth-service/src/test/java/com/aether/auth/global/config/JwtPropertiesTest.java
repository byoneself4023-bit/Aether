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
        @DisplayName("짧은 시크릿(32바이트 미만) 시 시작 실패")
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
            props.setSecret("aether-jwt-secret-key-minimum-32-characters-long-for-hmac-sha256");
            props.setAccessExpiration(1800000L);
            props.setRefreshExpiration(604800000L);

            assertThatCode(props::validate).doesNotThrowAnyException();
        }

        @Test
        @DisplayName("정확히 32바이트 시크릿 통과")
        void validate_Exactly32Bytes_Success() {
            JwtProperties props = new JwtProperties();
            props.setSecret("abcdefghijklmnopqrstuvwxyz123456"); // 32 chars
            props.setAccessExpiration(1800000L);
            props.setRefreshExpiration(604800000L);

            assertThatCode(props::validate).doesNotThrowAnyException();
        }
    }
}
