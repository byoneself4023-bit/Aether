package com.aether.auth.global.security;

import com.aether.auth.global.config.JwtProperties;
import com.aether.auth.global.exception.BusinessException;
import com.aether.auth.global.exception.ErrorCode;
import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.Date;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

@Slf4j
@Component
@RequiredArgsConstructor
public class JwtTokenProvider {

    private final JwtProperties jwtProperties;
    private final RedisTemplate<String, String> redisTemplate;

    private SecretKey secretKey;

    private static final String REFRESH_TOKEN_PREFIX = "refresh:";
    private static final String REFRESH_JTI_PREFIX = "refresh_jti:";
    private static final String BLACKLIST_PREFIX = "blacklist:";

    @PostConstruct
    public void init() {
        this.secretKey = Keys.hmacShaKeyFor(
                jwtProperties.getSecret().getBytes(StandardCharsets.UTF_8)
        );
    }

    public String createAccessToken(Long userId, String email, String role) {
        Date now = new Date();
        Date expiry = new Date(now.getTime() + jwtProperties.getAccessExpiration());

        return Jwts.builder()
                .subject(String.valueOf(userId))
                .claim("email", email)
                .claim("role", role)
                .issuedAt(now)
                .expiration(expiry)
                .signWith(secretKey)
                .compact();
    }

    public String createRefreshToken(Long userId) {
        Date now = new Date();
        Date expiry = new Date(now.getTime() + jwtProperties.getRefreshExpiration());

        String jti = UUID.randomUUID().toString();

        String refreshToken = Jwts.builder()
                .subject(String.valueOf(userId))
                .id(jti)
                .issuedAt(now)
                .expiration(expiry)
                .signWith(secretKey)
                .compact();

        // Redis에 refresh token 저장
        String tokenKey = REFRESH_TOKEN_PREFIX + userId;
        redisTemplate.opsForValue().set(
                tokenKey,
                refreshToken,
                jwtProperties.getRefreshExpiration(),
                TimeUnit.MILLISECONDS
        );

        // Redis에 jti 저장 (reuse detection용)
        String jtiKey = REFRESH_JTI_PREFIX + userId;
        redisTemplate.opsForValue().set(
                jtiKey,
                jti,
                jwtProperties.getRefreshExpiration(),
                TimeUnit.MILLISECONDS
        );

        return refreshToken;
    }

    public boolean validateToken(String token) {
        try {
            Jwts.parser()
                    .verifyWith(secretKey)
                    .build()
                    .parseSignedClaims(token);
            return true;
        } catch (ExpiredJwtException e) {
            log.warn("Token expired: {}", e.getMessage());
            throw new BusinessException(ErrorCode.TOKEN_EXPIRED);
        } catch (JwtException e) {
            log.warn("Invalid token: {}", e.getMessage());
            throw new BusinessException(ErrorCode.INVALID_TOKEN);
        }
    }

    public boolean isBlacklisted(String token) {
        String key = BLACKLIST_PREFIX + token;
        return Boolean.TRUE.equals(redisTemplate.hasKey(key));
    }

    public void blacklistAccessToken(String token) {
        try {
            Claims claims = getClaims(token);
            Date expiration = claims.getExpiration();
            long remainingMs = expiration.getTime() - System.currentTimeMillis();

            if (remainingMs > 0) {
                String key = BLACKLIST_PREFIX + token;
                redisTemplate.opsForValue().set(key, "1", remainingMs, TimeUnit.MILLISECONDS);
                log.debug("Access token blacklisted, TTL={}ms", remainingMs);
            }
        } catch (Exception e) {
            log.warn("Failed to blacklist access token: {}", e.getMessage());
        }
    }

    public Authentication getAuthentication(String token) {
        Claims claims = getClaims(token);

        String email = claims.get("email", String.class);
        String role = claims.get("role", String.class);

        UserDetails userDetails = org.springframework.security.core.userdetails.User.builder()
                .username(email)
                .password("")
                .authorities(Collections.singletonList(new SimpleGrantedAuthority("ROLE_" + role)))
                .build();

        return new UsernamePasswordAuthenticationToken(userDetails, token, userDetails.getAuthorities());
    }

    public Long getUserIdFromToken(String token) {
        Claims claims = getClaims(token);
        return Long.parseLong(claims.getSubject());
    }

    public String getEmailFromToken(String token) {
        Claims claims = getClaims(token);
        return claims.get("email", String.class);
    }

    public boolean validateRefreshToken(Long userId, String refreshToken) {
        String tokenKey = REFRESH_TOKEN_PREFIX + userId;
        String storedToken = redisTemplate.opsForValue().get(tokenKey);

        if (storedToken == null) {
            throw new BusinessException(ErrorCode.REFRESH_TOKEN_NOT_FOUND);
        }

        // Reuse detection: 저장된 토큰과 불일치하면 탈취로 판단
        if (!storedToken.equals(refreshToken)) {
            log.warn("Refresh token reuse detected for userId={}. Invalidating all sessions.", userId);
            invalidateAllTokens(userId);
            throw new BusinessException(ErrorCode.INVALID_TOKEN);
        }

        // jti 일치 확인
        Claims claims = getClaims(refreshToken);
        String jti = claims.getId();
        String jtiKey = REFRESH_JTI_PREFIX + userId;
        String storedJti = redisTemplate.opsForValue().get(jtiKey);

        if (jti == null || !jti.equals(storedJti)) {
            log.warn("Refresh token jti mismatch for userId={}. Invalidating all sessions.", userId);
            invalidateAllTokens(userId);
            throw new BusinessException(ErrorCode.INVALID_TOKEN);
        }

        return validateToken(refreshToken);
    }

    public void invalidateAllTokens(Long userId) {
        redisTemplate.delete(REFRESH_TOKEN_PREFIX + userId);
        redisTemplate.delete(REFRESH_JTI_PREFIX + userId);
        log.info("All tokens invalidated for userId={}", userId);
    }

    public void deleteRefreshToken(Long userId) {
        redisTemplate.delete(REFRESH_TOKEN_PREFIX + userId);
        redisTemplate.delete(REFRESH_JTI_PREFIX + userId);
    }

    private Claims getClaims(String token) {
        return Jwts.parser()
                .verifyWith(secretKey)
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }
}
