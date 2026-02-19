package com.aether.auth.global.security;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.core.ValueOperations;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;

import java.util.concurrent.TimeUnit;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.BDDMockito.*;

@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT)
class RateLimitInterceptorTest {

    @Mock
    private RedisTemplate<String, String> redisTemplate;

    @Mock
    private ValueOperations<String, String> valueOperations;

    private RateLimitInterceptor interceptor;

    @BeforeEach
    void setUp() {
        given(redisTemplate.opsForValue()).willReturn(valueOperations);
        interceptor = new RateLimitInterceptor(redisTemplate);
    }

    @Nested
    @DisplayName("Rate Limiting")
    class RateLimiting {

        @Test
        @DisplayName("제한 이내 요청 통과")
        void withinLimit_RequestPasses() throws Exception {
            MockHttpServletRequest request = new MockHttpServletRequest("POST", "/api/auth/login");
            request.setRemoteAddr("127.0.0.1");
            MockHttpServletResponse response = new MockHttpServletResponse();

            given(valueOperations.increment(anyString())).willReturn(1L);

            boolean result = interceptor.preHandle(request, response, new Object());

            assertThat(result).isTrue();
            assertThat(response.getStatus()).isEqualTo(200);
        }

        @Test
        @DisplayName("제한 초과 시 429 반환")
        void exceedsLimit_Returns429() throws Exception {
            MockHttpServletRequest request = new MockHttpServletRequest("POST", "/api/auth/login");
            request.setRemoteAddr("127.0.0.1");
            MockHttpServletResponse response = new MockHttpServletResponse();

            // 11번째 요청 (limit = 10)
            given(valueOperations.increment(anyString())).willReturn(11L);
            given(redisTemplate.getExpire(anyString(), eq(TimeUnit.SECONDS))).willReturn(45L);

            boolean result = interceptor.preHandle(request, response, new Object());

            assertThat(result).isFalse();
            assertThat(response.getStatus()).isEqualTo(429);
            assertThat(response.getHeader("Retry-After")).isEqualTo("45");
            assertThat(response.getContentAsString()).contains("요청 횟수를 초과");
        }

        @Test
        @DisplayName("다른 IP는 독립 카운트")
        void differentIp_IndependentCount() throws Exception {
            MockHttpServletRequest request1 = new MockHttpServletRequest("POST", "/api/auth/login");
            request1.setRemoteAddr("10.0.0.1");

            MockHttpServletRequest request2 = new MockHttpServletRequest("POST", "/api/auth/login");
            request2.setRemoteAddr("10.0.0.2");

            // 첫 IP: 10회 (limit 이내), 두 번째 IP: 1회
            given(valueOperations.increment(contains("10.0.0.1"))).willReturn(10L);
            given(valueOperations.increment(contains("10.0.0.2"))).willReturn(1L);

            MockHttpServletResponse response1 = new MockHttpServletResponse();
            MockHttpServletResponse response2 = new MockHttpServletResponse();

            boolean result1 = interceptor.preHandle(request1, response1, new Object());
            boolean result2 = interceptor.preHandle(request2, response2, new Object());

            assertThat(result1).isTrue(); // 10 <= 10, passes
            assertThat(result2).isTrue(); // 1 <= 10, passes
        }

        @Test
        @DisplayName("Rate limit 대상이 아닌 경로는 통과")
        void nonLimitedPath_AlwaysPasses() throws Exception {
            MockHttpServletRequest request = new MockHttpServletRequest("GET", "/health");
            request.setRemoteAddr("127.0.0.1");
            MockHttpServletResponse response = new MockHttpServletResponse();

            boolean result = interceptor.preHandle(request, response, new Object());

            assertThat(result).isTrue();
            // Redis 호출 없음
            verify(valueOperations, never()).increment(anyString());
        }

        @Test
        @DisplayName("X-Forwarded-For 헤더로 IP 추출")
        void xForwardedFor_ExtractsIp() throws Exception {
            MockHttpServletRequest request = new MockHttpServletRequest("POST", "/api/auth/login");
            request.addHeader("X-Forwarded-For", "203.0.113.50, 70.41.3.18");
            MockHttpServletResponse response = new MockHttpServletResponse();

            given(valueOperations.increment(contains("203.0.113.50"))).willReturn(1L);

            boolean result = interceptor.preHandle(request, response, new Object());

            assertThat(result).isTrue();
            verify(valueOperations).increment(contains("203.0.113.50"));
        }

        @Test
        @DisplayName("signup 경로도 rate limit 적용")
        void signupPath_RateLimited() throws Exception {
            MockHttpServletRequest request = new MockHttpServletRequest("POST", "/api/auth/signup");
            request.setRemoteAddr("127.0.0.1");
            MockHttpServletResponse response = new MockHttpServletResponse();

            given(valueOperations.increment(anyString())).willReturn(11L);
            given(redisTemplate.getExpire(anyString(), eq(TimeUnit.SECONDS))).willReturn(30L);

            boolean result = interceptor.preHandle(request, response, new Object());

            assertThat(result).isFalse();
            assertThat(response.getStatus()).isEqualTo(429);
        }
    }
}
