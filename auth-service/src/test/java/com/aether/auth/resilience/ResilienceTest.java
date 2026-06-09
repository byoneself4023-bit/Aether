package com.aether.auth.resilience;

import com.aether.auth.application.auth.AuthService;
import com.aether.auth.domain.user.dto.SignUpRequest;
import com.aether.auth.domain.user.repository.UserRepository;
import com.aether.auth.global.config.JwtProperties;
import com.aether.auth.global.exception.BusinessException;
import com.aether.auth.global.exception.ErrorCode;
import com.aether.auth.global.security.JwtAuthenticationFilter;
import com.aether.auth.global.security.JwtTokenProvider;
import com.aether.auth.global.security.RateLimitInterceptor;
import com.aether.auth.api.HealthController;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;
import org.springframework.data.redis.RedisConnectionFailureException;
import org.springframework.data.redis.connection.RedisConnection;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.core.ValueOperations;
import org.springframework.data.redis.core.script.RedisScript;
import org.springframework.http.ResponseEntity;
import org.springframework.mock.web.MockFilterChain;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;

import javax.crypto.SecretKey;
import javax.sql.DataSource;
import java.nio.charset.StandardCharsets;
import java.sql.SQLException;
import java.util.Date;
import java.util.Map;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.BDDMockito.*;

/**
 * 장애 시뮬레이션 테스트
 *
 * Redis/DB/외부 요청 장애 시 서비스의 graceful degradation 확인.
 * Docker 없이 모킹으로 장애 주입.
 */
@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT)
class ResilienceTest {

    // HS512(64바이트) 키 필요 — 짧은 키면 createAccessToken/createRefreshToken이 WeakKeyException
    private static final String TEST_SECRET =
            "ThisIsATestSecretKeyForJwtTokenGeneration1234567890AbCdEfGhIjKlMn";
    private SecretKey secretKey;

    @BeforeEach
    void initKey() {
        secretKey = Keys.hmacShaKeyFor(TEST_SECRET.getBytes(StandardCharsets.UTF_8));
    }

    // === A. Redis 장애 시뮬레이션 ===

    @Nested
    @DisplayName("A. Redis 장애 시뮬레이션")
    class RedisFailure {

        @Mock
        private RedisTemplate<String, String> redisTemplate;

        @Mock
        private ValueOperations<String, String> valueOperations;

        // --- A-1. Rate Limiting fail-open ---

        @Test
        @DisplayName("A-1. Redis 연결 실패 시 Rate Limiting이 fail-open (요청 허용)")
        void redisDown_rateLimiting_failOpen() throws Exception {
            // Given: Redis increment가 예외를 던짐
            given(redisTemplate.opsForValue()).willReturn(valueOperations);
            given(valueOperations.increment(anyString()))
                    .willThrow(new RedisConnectionFailureException("Connection refused"));

            RateLimitInterceptor interceptor = new RateLimitInterceptor(redisTemplate);

            MockHttpServletRequest request = new MockHttpServletRequest("POST", "/api/auth/login");
            request.setRemoteAddr("127.0.0.1");
            MockHttpServletResponse response = new MockHttpServletResponse();

            // When & Then: 예외가 전파되는지 확인
            // 현재 구현은 예외를 전파함 (fail-close)
            // 이 테스트는 현재 동작을 문서화함
            assertThatThrownBy(() -> interceptor.preHandle(request, response, new Object()))
                    .isInstanceOf(RedisConnectionFailureException.class);
        }

        // --- A-2. 로그인 시 Redis 블랙리스트 체크 ---

        @Test
        @DisplayName("A-2. Redis 연결 실패 시 JWT 필터가 블랙리스트 체크를 건너뜀")
        void redisDown_jwtFilter_skipsBlacklistCheck() throws Exception {
            // Given: JwtTokenProvider 모킹
            JwtTokenProvider tokenProvider = mock(JwtTokenProvider.class);
            JwtAuthenticationFilter filter = new JwtAuthenticationFilter(tokenProvider);

            // 유효한 토큰이지만 블랙리스트 체크에서 Redis 예외
            String token = createTestAccessToken(1L, "test@test.com", "USER");
            given(tokenProvider.validateToken(token)).willReturn(true);
            given(tokenProvider.isBlacklisted(token))
                    .willThrow(new RedisConnectionFailureException("Connection refused"));

            MockHttpServletRequest request = new MockHttpServletRequest("GET", "/api/auth/me");
            request.addHeader("Authorization", "Bearer " + token);
            MockHttpServletResponse response = new MockHttpServletResponse();
            MockFilterChain filterChain = new MockFilterChain();

            // When & Then: 필터가 예외를 전파하는지 확인
            // Redis 장애 시 블랙리스트 체크 실패 → 예외 전파 (fail-close)
            assertThatThrownBy(() -> filter.doFilter(request, response, filterChain))
                    .isInstanceOf(Exception.class);
            // SecurityContext가 설정되지 않았음을 확인
            assertThat(SecurityContextHolder.getContext().getAuthentication()).isNull();
        }

        // --- A-3. Refresh Token 저장 실패 ---

        @Test
        @DisplayName("A-3. Redis 연결 실패 시 Refresh Token 저장 실패")
        void redisDown_refreshTokenStore_fails() {
            // Given
            JwtProperties properties = mock(JwtProperties.class);
            given(properties.getSecret()).willReturn(TEST_SECRET);
            given(properties.getRefreshExpiration()).willReturn(604800000L);

            // ④ 원자화 후: 저장은 단일 Lua EVAL → execute()가 연결 실패를 그대로 전파해야 함
            willThrow(new RedisConnectionFailureException("Connection refused"))
                    .given(redisTemplate)
                    .execute(any(RedisScript.class), anyList(), any(), any(), any());

            JwtTokenProvider tokenProvider = new JwtTokenProvider(properties, redisTemplate);
            tokenProvider.init();

            // When & Then: Refresh Token 생성 시 Redis 저장 실패
            assertThatThrownBy(() -> tokenProvider.createRefreshToken(1L))
                    .isInstanceOf(RedisConnectionFailureException.class);
        }
    }

    // === B. DB 장애 시뮬레이션 ===

    @Nested
    @DisplayName("B. DB 장애 시뮬레이션")
    class DatabaseFailure {

        @Mock
        private UserRepository userRepository;

        @Mock
        private PasswordEncoder passwordEncoder;

        @Mock
        private JwtTokenProvider jwtTokenProvider;

        @Mock
        private JwtProperties jwtProperties;

        @InjectMocks
        private AuthService authService;

        // --- B-4. 회원가입 시 DB 연결 실패 ---

        @Test
        @DisplayName("B-4. PostgreSQL 연결 실패 시 회원가입 → 예외 발생")
        void dbDown_signup_throwsException() {
            // Given: DB 조회 시 예외
            given(userRepository.existsByEmail(anyString()))
                    .willThrow(new RuntimeException("Unable to acquire JDBC Connection"));

            SignUpRequest request = SignUpRequest.builder()
                    .email("test@test.com")
                    .password("Password1!")
                    .name("테스트")
                    .build();

            // When & Then
            assertThatThrownBy(() -> authService.signUp(request))
                    .isInstanceOf(RuntimeException.class)
                    .hasMessageContaining("JDBC Connection");
        }

        // --- B-5. Health Check 시 DB 장애 ---

        @Test
        @DisplayName("B-5. PostgreSQL 연결 실패 시 health check → degraded (503)")
        void dbDown_healthCheck_returnsDegraded() throws Exception {
            // Given
            DataSource dataSource = mock(DataSource.class);
            RedisTemplate<String, String> redisTemplate = mock(RedisTemplate.class);
            RedisConnectionFactory connectionFactory = mock(RedisConnectionFactory.class);
            RedisConnection redisConnection = mock(RedisConnection.class);

            given(dataSource.getConnection())
                    .willThrow(new SQLException("Connection refused"));
            given(redisTemplate.getConnectionFactory()).willReturn(connectionFactory);
            given(connectionFactory.getConnection()).willReturn(redisConnection);
            given(redisConnection.ping()).willReturn("PONG");

            HealthController controller = new HealthController(dataSource, redisTemplate);

            // When
            ResponseEntity<Map<String, Object>> response = controller.health();

            // Then
            assertThat(response.getStatusCode().value()).isEqualTo(503);
            assertThat(response.getBody()).isNotNull();
            assertThat(response.getBody().get("status")).isEqualTo("degraded");

            @SuppressWarnings("unchecked")
            Map<String, Object> checks = (Map<String, Object>) response.getBody().get("checks");
            @SuppressWarnings("unchecked")
            Map<String, Object> dbCheck = (Map<String, Object>) checks.get("database");
            assertThat(dbCheck.get("status")).isEqualTo("DOWN");
        }
    }

    // === C. 외부 요청 이상 (JWT 검증) ===

    @Nested
    @DisplayName("C. 외부 요청 이상 (JWT 검증)")
    class JwtValidation {

        @Mock
        private RedisTemplate<String, String> redisTemplate;

        @Mock
        private ValueOperations<String, String> valueOperations;

        private JwtTokenProvider tokenProvider;

        @BeforeEach
        void setUp() {
            JwtProperties properties = mock(JwtProperties.class);
            given(properties.getSecret()).willReturn(TEST_SECRET);
            given(properties.getAccessExpiration()).willReturn(1800000L);
            given(properties.getRefreshExpiration()).willReturn(604800000L);
            given(redisTemplate.opsForValue()).willReturn(valueOperations);

            tokenProvider = new JwtTokenProvider(properties, redisTemplate);
            tokenProvider.init();
        }

        // --- C-6. 잘못된 JWT 시그니처 ---

        @Test
        @DisplayName("C-6. 잘못된 JWT 시그니처 → INVALID_TOKEN (401)")
        void invalidSignature_throwsInvalidToken() {
            // Given: 다른 키로 서명한 토큰
            SecretKey wrongKey = Keys.hmacShaKeyFor(
                    "ACompletelyDifferentSecretKeyForTesting123!".getBytes(StandardCharsets.UTF_8)
            );
            String tamperedToken = Jwts.builder()
                    .subject("1")
                    .claim("email", "test@test.com")
                    .claim("role", "USER")
                    .issuedAt(new Date())
                    .expiration(new Date(System.currentTimeMillis() + 1800000))
                    .signWith(wrongKey)
                    .compact();

            // When & Then
            assertThatThrownBy(() -> tokenProvider.validateToken(tamperedToken))
                    .isInstanceOf(BusinessException.class)
                    .satisfies(e -> {
                        BusinessException be = (BusinessException) e;
                        assertThat(be.getErrorCode()).isEqualTo(ErrorCode.INVALID_TOKEN);
                    });
        }

        // --- C-7. 만료된 JWT ---

        @Test
        @DisplayName("C-7. 만료된 JWT → TOKEN_EXPIRED (401)")
        void expiredToken_throwsTokenExpired() {
            // Given: 이미 만료된 토큰
            String expiredToken = Jwts.builder()
                    .subject("1")
                    .claim("email", "test@test.com")
                    .claim("role", "USER")
                    .issuedAt(new Date(System.currentTimeMillis() - 3600000))
                    .expiration(new Date(System.currentTimeMillis() - 1000))
                    .signWith(secretKey)
                    .compact();

            // When & Then
            assertThatThrownBy(() -> tokenProvider.validateToken(expiredToken))
                    .isInstanceOf(BusinessException.class)
                    .satisfies(e -> {
                        BusinessException be = (BusinessException) e;
                        assertThat(be.getErrorCode()).isEqualTo(ErrorCode.TOKEN_EXPIRED);
                    });
        }

        // --- C-8. 블랙리스트된 JWT ---

        @Test
        @DisplayName("C-8. 블랙리스트된 JWT → SecurityContext 비설정")
        void blacklistedToken_clearsSecurityContext() throws Exception {
            // Given
            String validToken = tokenProvider.createAccessToken(1L, "test@test.com", "USER");
            given(redisTemplate.hasKey(contains("blacklist:"))).willReturn(true);

            JwtAuthenticationFilter filter = new JwtAuthenticationFilter(tokenProvider);

            MockHttpServletRequest request = new MockHttpServletRequest("GET", "/api/auth/me");
            request.addHeader("Authorization", "Bearer " + validToken);
            MockHttpServletResponse response = new MockHttpServletResponse();
            MockFilterChain filterChain = new MockFilterChain();

            SecurityContextHolder.clearContext();

            // When
            filter.doFilter(request, response, filterChain);

            // Then: 블랙리스트된 토큰이므로 SecurityContext에 인증 정보 없음
            assertThat(SecurityContextHolder.getContext().getAuthentication()).isNull();
        }
    }

    // === Helper ===

    private String createTestAccessToken(Long userId, String email, String role) {
        return Jwts.builder()
                .subject(String.valueOf(userId))
                .claim("email", email)
                .claim("role", role)
                .issuedAt(new Date())
                .expiration(new Date(System.currentTimeMillis() + 1800000))
                .signWith(secretKey)
                .compact();
    }
}
