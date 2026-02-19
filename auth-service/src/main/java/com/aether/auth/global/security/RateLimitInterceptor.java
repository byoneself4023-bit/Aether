package com.aether.auth.global.security;

import com.aether.auth.global.common.ApiResponse;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

import java.util.Set;
import java.util.concurrent.TimeUnit;

@Slf4j
@Component
@RequiredArgsConstructor
public class RateLimitInterceptor implements HandlerInterceptor {

    private final RedisTemplate<String, String> redisTemplate;
    private final ObjectMapper objectMapper = new ObjectMapper();

    private static final String RATE_LIMIT_PREFIX = "rate_limit:";
    private static final int MAX_REQUESTS_PER_MINUTE = 10;
    private static final long WINDOW_SECONDS = 60;

    private static final Set<String> RATE_LIMITED_PATHS = Set.of(
            "/api/auth/login",
            "/api/auth/signup"
    );

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler)
            throws Exception {

        String path = request.getRequestURI();

        if (!RATE_LIMITED_PATHS.contains(path)) {
            return true;
        }

        String clientIp = getClientIp(request);
        String key = RATE_LIMIT_PREFIX + path + ":" + clientIp;

        Long currentCount = redisTemplate.opsForValue().increment(key);

        if (currentCount != null && currentCount == 1) {
            redisTemplate.expire(key, WINDOW_SECONDS, TimeUnit.SECONDS);
        }

        if (currentCount != null && currentCount > MAX_REQUESTS_PER_MINUTE) {
            log.warn("Rate limit exceeded: ip={}, path={}, count={}", clientIp, path, currentCount);

            Long ttl = redisTemplate.getExpire(key, TimeUnit.SECONDS);
            long retryAfter = (ttl != null && ttl > 0) ? ttl : WINDOW_SECONDS;

            response.setStatus(HttpStatus.TOO_MANY_REQUESTS.value());
            response.setContentType(MediaType.APPLICATION_JSON_VALUE);
            response.setCharacterEncoding("UTF-8");
            response.setHeader("Retry-After", String.valueOf(retryAfter));

            ApiResponse<Void> errorResponse = ApiResponse.<Void>builder()
                    .success(false)
                    .error(ApiResponse.ErrorInfo.builder()
                            .code("C003")
                            .message("요청 횟수를 초과했습니다. " + retryAfter + "초 후에 다시 시도해주세요.")
                            .build())
                    .build();

            response.getWriter().write(objectMapper.writeValueAsString(errorResponse));
            return false;
        }

        return true;
    }

    private String getClientIp(HttpServletRequest request) {
        String xForwardedFor = request.getHeader("X-Forwarded-For");
        if (xForwardedFor != null && !xForwardedFor.isEmpty()) {
            return xForwardedFor.split(",")[0].trim();
        }
        return request.getRemoteAddr();
    }
}
