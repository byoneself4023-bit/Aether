package com.aether.auth.api;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.redis.connection.RedisConnection;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.SQLException;

import static org.mockito.BDDMockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@ExtendWith(MockitoExtension.class)
class HealthControllerTest {

    private MockMvc mockMvc;

    @Mock
    private DataSource dataSource;

    @Mock
    private Connection dbConnection;

    @Mock
    private RedisTemplate<String, String> redisTemplate;

    @Mock
    private RedisConnectionFactory redisConnectionFactory;

    @Mock
    private RedisConnection redisConnection;

    @BeforeEach
    void setUp() {
        HealthController healthController = new HealthController(dataSource, redisTemplate);
        mockMvc = MockMvcBuilders.standaloneSetup(healthController).build();
    }

    @Test
    @DisplayName("DB/Redis 정상 → healthy 200")
    void health_AllUp() throws Exception {
        given(dataSource.getConnection()).willReturn(dbConnection);
        given(dbConnection.isValid(2)).willReturn(true);
        given(redisTemplate.getConnectionFactory()).willReturn(redisConnectionFactory);
        given(redisConnectionFactory.getConnection()).willReturn(redisConnection);
        given(redisConnection.ping()).willReturn("PONG");

        mockMvc.perform(get("/health"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("healthy"))
                .andExpect(jsonPath("$.checks.database.status").value("UP"))
                .andExpect(jsonPath("$.checks.redis.status").value("UP"))
                .andExpect(jsonPath("$.timestamp").exists());
    }

    @Test
    @DisplayName("DB 실패 → degraded 503")
    void health_DbDown() throws Exception {
        given(dataSource.getConnection()).willThrow(new SQLException("Connection refused"));
        given(redisTemplate.getConnectionFactory()).willReturn(redisConnectionFactory);
        given(redisConnectionFactory.getConnection()).willReturn(redisConnection);
        given(redisConnection.ping()).willReturn("PONG");

        mockMvc.perform(get("/health"))
                .andExpect(status().isServiceUnavailable())
                .andExpect(jsonPath("$.status").value("degraded"))
                .andExpect(jsonPath("$.checks.database.status").value("DOWN"))
                .andExpect(jsonPath("$.checks.redis.status").value("UP"));
    }

    @Test
    @DisplayName("Redis 실패 → degraded 503")
    void health_RedisDown() throws Exception {
        given(dataSource.getConnection()).willReturn(dbConnection);
        given(dbConnection.isValid(2)).willReturn(true);
        given(redisTemplate.getConnectionFactory()).willReturn(redisConnectionFactory);
        given(redisConnectionFactory.getConnection()).willThrow(new RuntimeException("Redis unavailable"));

        mockMvc.perform(get("/health"))
                .andExpect(status().isServiceUnavailable())
                .andExpect(jsonPath("$.status").value("degraded"))
                .andExpect(jsonPath("$.checks.database.status").value("UP"))
                .andExpect(jsonPath("$.checks.redis.status").value("DOWN"));
    }
}
