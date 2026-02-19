package com.aether.auth.api;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.sql.DataSource;
import java.sql.Connection;
import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;

@Slf4j
@RestController
@RequiredArgsConstructor
public class HealthController {

    private final DataSource dataSource;
    private final RedisTemplate<String, String> redisTemplate;

    @Value("${spring.application.name:auth-service}")
    private String serviceName;

    @Value("${app.version:${project.version:0.0.1-SNAPSHOT}}")
    private String version;

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> result = new LinkedHashMap<>();
        Map<String, Object> checks = new LinkedHashMap<>();

        boolean allHealthy = true;

        // DB check
        try (Connection conn = dataSource.getConnection()) {
            conn.isValid(2);
            checks.put("database", Map.of("status", "UP"));
        } catch (Exception e) {
            log.warn("Database health check failed: {}", e.getMessage());
            checks.put("database", Map.of("status", "DOWN", "error", e.getMessage()));
            allHealthy = false;
        }

        // Redis check
        try {
            String pong = redisTemplate.getConnectionFactory().getConnection().ping();
            checks.put("redis", Map.of("status", pong != null ? "UP" : "DOWN"));
            if (pong == null) allHealthy = false;
        } catch (Exception e) {
            log.warn("Redis health check failed: {}", e.getMessage());
            checks.put("redis", Map.of("status", "DOWN", "error", e.getMessage()));
            allHealthy = false;
        }

        result.put("status", allHealthy ? "healthy" : "degraded");
        result.put("service", serviceName);
        result.put("version", version);
        result.put("checks", checks);
        result.put("timestamp", Instant.now().toString());

        int statusCode = allHealthy ? 200 : 503;
        return ResponseEntity.status(statusCode).body(result);
    }
}
