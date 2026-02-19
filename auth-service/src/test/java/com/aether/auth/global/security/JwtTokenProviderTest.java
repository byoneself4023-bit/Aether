package com.aether.auth.global.security;

import com.aether.auth.global.config.JwtProperties;
import com.aether.auth.global.exception.BusinessException;
import com.aether.auth.global.exception.ErrorCode;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;

import java.nio.charset.StandardCharsets;
import java.util.Date;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.core.ValueOperations;
import org.springframework.security.core.Authentication;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.BDDMockito.*;

@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT)
class JwtTokenProviderTest {

    @Mock
    private JwtProperties jwtProperties;

    @Mock
    private RedisTemplate<String, String> redisTemplate;

    @Mock
    private ValueOperations<String, String> valueOperations;

    private JwtTokenProvider jwtTokenProvider;

    @BeforeEach
    void setUp() {
        given(jwtProperties.getSecret())
                .willReturn("aether-jwt-secret-key-minimum-32-characters-long-for-hmac-sha256");
        given(jwtProperties.getAccessExpiration()).willReturn(1800000L);
        given(jwtProperties.getRefreshExpiration()).willReturn(604800000L);
        given(redisTemplate.opsForValue()).willReturn(valueOperations);

        jwtTokenProvider = new JwtTokenProvider(jwtProperties, redisTemplate);
        jwtTokenProvider.init();
    }

    @Nested
    @DisplayName("Access Token")
    class AccessToken {

        @Test
        @DisplayName("생성 성공")
        void createAccessToken_Success() {
            String token = jwtTokenProvider.createAccessToken(1L, "test@example.com", "USER");
            assertThat(token).isNotNull().isNotEmpty();
        }

        @Test
        @DisplayName("검증 성공")
        void validateToken_Success() {
            String token = jwtTokenProvider.createAccessToken(1L, "test@example.com", "USER");
            boolean isValid = jwtTokenProvider.validateToken(token);
            assertThat(isValid).isTrue();
        }

        @Test
        @DisplayName("검증 실패 - 잘못된 토큰")
        void validateToken_InvalidToken() {
            String invalidToken = "invalid.token.here";

            assertThatThrownBy(() -> jwtTokenProvider.validateToken(invalidToken))
                    .isInstanceOf(BusinessException.class)
                    .satisfies(e -> {
                        BusinessException be = (BusinessException) e;
                        assertThat(be.getErrorCode()).isEqualTo(ErrorCode.INVALID_TOKEN);
                    });
        }

        @Test
        @DisplayName("사용자 ID 추출")
        void getUserIdFromToken_Success() {
            String token = jwtTokenProvider.createAccessToken(1L, "test@example.com", "USER");
            Long userId = jwtTokenProvider.getUserIdFromToken(token);
            assertThat(userId).isEqualTo(1L);
        }

        @Test
        @DisplayName("이메일 추출")
        void getEmailFromToken_Success() {
            String token = jwtTokenProvider.createAccessToken(1L, "test@example.com", "USER");
            String email = jwtTokenProvider.getEmailFromToken(token);
            assertThat(email).isEqualTo("test@example.com");
        }

        @Test
        @DisplayName("검증 실패 - 만료된 토큰")
        void validateToken_Expired() {
            // 이미 만료된 토큰 직접 생성
            String secret = "aether-jwt-secret-key-minimum-32-characters-long-for-hmac-sha256";
            Date now = new Date();
            Date pastExpiry = new Date(now.getTime() - 1000); // 1초 전에 만료

            String expiredToken = Jwts.builder()
                    .subject("1")
                    .claim("email", "test@example.com")
                    .claim("role", "USER")
                    .issuedAt(new Date(now.getTime() - 60000))
                    .expiration(pastExpiry)
                    .signWith(Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8)))
                    .compact();

            assertThatThrownBy(() -> jwtTokenProvider.validateToken(expiredToken))
                    .isInstanceOf(BusinessException.class)
                    .satisfies(e -> {
                        BusinessException be = (BusinessException) e;
                        assertThat(be.getErrorCode()).isEqualTo(ErrorCode.TOKEN_EXPIRED);
                    });
        }

        @Test
        @DisplayName("Authentication 객체 생성")
        void getAuthentication_Success() {
            String token = jwtTokenProvider.createAccessToken(1L, "test@example.com", "USER");
            Authentication authentication = jwtTokenProvider.getAuthentication(token);

            assertThat(authentication).isNotNull();
            assertThat(authentication.getName()).isEqualTo("test@example.com");
            assertThat(authentication.getAuthorities())
                    .anyMatch(a -> a.getAuthority().equals("ROLE_USER"));
        }
    }

    @Nested
    @DisplayName("Refresh Token")
    class RefreshToken {

        @Test
        @DisplayName("생성 성공 - jti 포함")
        void createRefreshToken_Success() {
            String token = jwtTokenProvider.createRefreshToken(1L);

            assertThat(token).isNotNull().isNotEmpty();
            // refresh token 저장 + jti 저장 = 2회 호출
            verify(valueOperations, times(2)).set(anyString(), anyString(), anyLong(), any());
        }

        @Test
        @DisplayName("검증 성공")
        void validateRefreshToken_Success() {
            // createRefreshToken에서 jti 캡처
            ArgumentCaptor<String> jtiCaptor = ArgumentCaptor.forClass(String.class);

            String refreshToken = jwtTokenProvider.createRefreshToken(1L);

            // refresh_jti:1 에 저장된 jti 값을 캡처
            verify(valueOperations, times(2)).set(anyString(), jtiCaptor.capture(), anyLong(), any());
            // 첫 번째 호출: refresh:1 → token, 두 번째 호출: refresh_jti:1 → jti
            String storedJti = jtiCaptor.getAllValues().get(1);

            // Redis에서 토큰과 jti를 반환하도록 설정
            given(valueOperations.get("refresh:1")).willReturn(refreshToken);
            given(valueOperations.get("refresh_jti:1")).willReturn(storedJti);

            boolean isValid = jwtTokenProvider.validateRefreshToken(1L, refreshToken);
            assertThat(isValid).isTrue();
        }

        @Test
        @DisplayName("검증 실패 - Redis에 토큰 없음")
        void validateRefreshToken_NotFound() {
            given(valueOperations.get("refresh:1")).willReturn(null);

            assertThatThrownBy(() -> jwtTokenProvider.validateRefreshToken(1L, "someToken"))
                    .isInstanceOf(BusinessException.class)
                    .satisfies(e -> {
                        BusinessException be = (BusinessException) e;
                        assertThat(be.getErrorCode()).isEqualTo(ErrorCode.REFRESH_TOKEN_NOT_FOUND);
                    });
        }

        @Test
        @DisplayName("삭제 성공 - refresh token + jti 삭제")
        void deleteRefreshToken_Success() {
            given(redisTemplate.delete(anyString())).willReturn(true);

            jwtTokenProvider.deleteRefreshToken(1L);

            verify(redisTemplate).delete("refresh:1");
            verify(redisTemplate).delete("refresh_jti:1");
        }
    }

    @Nested
    @DisplayName("Refresh Token Reuse Detection")
    class ReuseDetection {

        @Test
        @DisplayName("다른 토큰으로 요청 시 전체 세션 무효화")
        void validateRefreshToken_ReusedToken_InvalidatesAll() {
            // 정상 토큰 생성
            jwtTokenProvider.createRefreshToken(1L);

            // Redis에 현재 저장된 토큰은 다른 값
            given(valueOperations.get("refresh:1")).willReturn("different-stored-token");
            given(redisTemplate.delete(anyString())).willReturn(true);

            // 이전 토큰으로 요청 → reuse detection
            assertThatThrownBy(() ->
                    jwtTokenProvider.validateRefreshToken(1L, "old-reused-token"))
                    .isInstanceOf(BusinessException.class)
                    .satisfies(e -> {
                        BusinessException be = (BusinessException) e;
                        assertThat(be.getErrorCode()).isEqualTo(ErrorCode.INVALID_TOKEN);
                    });

            // 전체 세션 무효화 확인
            verify(redisTemplate).delete("refresh:1");
            verify(redisTemplate).delete("refresh_jti:1");
        }

        @Test
        @DisplayName("jti 불일치 시 전체 세션 무효화")
        void validateRefreshToken_JtiMismatch_InvalidatesAll() {
            String refreshToken = jwtTokenProvider.createRefreshToken(1L);

            // 토큰은 일치하지만 jti가 다름
            given(valueOperations.get("refresh:1")).willReturn(refreshToken);
            given(valueOperations.get("refresh_jti:1")).willReturn("wrong-jti");
            given(redisTemplate.delete(anyString())).willReturn(true);

            assertThatThrownBy(() ->
                    jwtTokenProvider.validateRefreshToken(1L, refreshToken))
                    .isInstanceOf(BusinessException.class)
                    .satisfies(e -> {
                        BusinessException be = (BusinessException) e;
                        assertThat(be.getErrorCode()).isEqualTo(ErrorCode.INVALID_TOKEN);
                    });

            verify(redisTemplate).delete("refresh:1");
            verify(redisTemplate).delete("refresh_jti:1");
        }
    }

    @Nested
    @DisplayName("Access Token Blacklist")
    class Blacklist {

        @Test
        @DisplayName("블랙리스트 등록")
        void blacklistAccessToken_Success() {
            String token = jwtTokenProvider.createAccessToken(1L, "test@example.com", "USER");

            jwtTokenProvider.blacklistAccessToken(token);

            verify(valueOperations).set(startsWith("blacklist:"), eq("1"), anyLong(), any());
        }

        @Test
        @DisplayName("블랙리스트 확인 - 있음")
        void isBlacklisted_True() {
            given(redisTemplate.hasKey(anyString())).willReturn(true);

            boolean result = jwtTokenProvider.isBlacklisted("some.token");
            assertThat(result).isTrue();
        }

        @Test
        @DisplayName("블랙리스트 확인 - 없음")
        void isBlacklisted_False() {
            given(redisTemplate.hasKey(anyString())).willReturn(false);

            boolean result = jwtTokenProvider.isBlacklisted("some.token");
            assertThat(result).isFalse();
        }
    }
}
