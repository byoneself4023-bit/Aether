package com.aether.auth.global.security;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.slf4j.MDC;
import org.springframework.mock.web.MockFilterChain;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;

import static org.assertj.core.api.Assertions.*;

class MdcLoggingFilterTest {

    private final MdcLoggingFilter filter = new MdcLoggingFilter();

    @Test
    @DisplayName("요청 시 MDC에 requestId, clientIp 설정")
    void shouldSetMdcFields() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest("GET", "/api/auth/me");
        request.setRemoteAddr("192.168.1.1");
        MockHttpServletResponse response = new MockHttpServletResponse();

        // MDC 값을 캡처하기 위한 chain
        String[] capturedRequestId = new String[1];
        String[] capturedClientIp = new String[1];

        MockFilterChain chain = new MockFilterChain() {
            @Override
            public void doFilter(jakarta.servlet.ServletRequest req, jakarta.servlet.ServletResponse res) {
                capturedRequestId[0] = MDC.get("requestId");
                capturedClientIp[0] = MDC.get("clientIp");
            }
        };

        filter.doFilterInternal(request, response, chain);

        assertThat(capturedRequestId[0]).isNotNull().isNotEmpty();
        assertThat(capturedClientIp[0]).isEqualTo("192.168.1.1");
        // 필터 완료 후 MDC 클리어 확인
        assertThat(MDC.get("requestId")).isNull();
    }

    @Test
    @DisplayName("X-Request-ID 헤더가 있으면 해당 값 사용")
    void shouldUseExistingRequestId() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest("GET", "/health");
        request.addHeader("X-Request-ID", "custom-id-123");
        request.setRemoteAddr("10.0.0.1");
        MockHttpServletResponse response = new MockHttpServletResponse();

        String[] capturedRequestId = new String[1];

        MockFilterChain chain = new MockFilterChain() {
            @Override
            public void doFilter(jakarta.servlet.ServletRequest req, jakarta.servlet.ServletResponse res) {
                capturedRequestId[0] = MDC.get("requestId");
            }
        };

        filter.doFilterInternal(request, response, chain);

        assertThat(capturedRequestId[0]).isEqualTo("custom-id-123");
        assertThat(response.getHeader("X-Request-ID")).isEqualTo("custom-id-123");
    }

    @Test
    @DisplayName("X-Forwarded-For 헤더에서 IP 추출")
    void shouldExtractIpFromXForwardedFor() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest("POST", "/api/auth/login");
        request.addHeader("X-Forwarded-For", "203.0.113.50, 70.41.3.18");
        request.setRemoteAddr("127.0.0.1");
        MockHttpServletResponse response = new MockHttpServletResponse();

        String[] capturedIp = new String[1];

        MockFilterChain chain = new MockFilterChain() {
            @Override
            public void doFilter(jakarta.servlet.ServletRequest req, jakarta.servlet.ServletResponse res) {
                capturedIp[0] = MDC.get("clientIp");
            }
        };

        filter.doFilterInternal(request, response, chain);

        assertThat(capturedIp[0]).isEqualTo("203.0.113.50");
    }
}
