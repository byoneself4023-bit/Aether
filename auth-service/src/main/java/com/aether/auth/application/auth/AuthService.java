package com.aether.auth.application.auth;

import com.aether.auth.domain.user.dto.*;
import com.aether.auth.domain.user.entity.User;
import com.aether.auth.domain.user.repository.UserRepository;
import com.aether.auth.global.config.JwtProperties;
import com.aether.auth.global.exception.BusinessException;
import com.aether.auth.global.exception.ErrorCode;
import com.aether.auth.global.security.JwtTokenProvider;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.MDC;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider jwtTokenProvider;
    private final JwtProperties jwtProperties;

    @Transactional
    public UserResponse signUp(SignUpRequest request) {
        // 이메일 중복 확인
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new BusinessException(ErrorCode.DUPLICATE_EMAIL);
        }

        // 비밀번호 암호화
        String encodedPassword = passwordEncoder.encode(request.getPassword());

        // 사용자 생성
        User user = User.builder()
                .email(request.getEmail())
                .password(encodedPassword)
                .name(request.getName())
                .build();

        User savedUser = userRepository.save(user);
        log.info("User registered: {}", savedUser.getEmail());

        return UserResponse.from(savedUser);
    }

    public TokenResponse login(LoginRequest request) {
        // 사용자 조회
        User user = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new BusinessException(ErrorCode.INVALID_CREDENTIALS));

        // 비밀번호 검증
        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            log.warn("login_failed: reason=invalid_password, email={}", request.getEmail());
            throw new BusinessException(ErrorCode.INVALID_CREDENTIALS);
        }

        // 계정 활성화 확인
        if (!user.isEnabled()) {
            log.warn("login_failed: reason=disabled_account, email={}", request.getEmail());
            throw new BusinessException(ErrorCode.INVALID_CREDENTIALS, "비활성화된 계정입니다");
        }

        // 토큰 생성
        String accessToken = jwtTokenProvider.createAccessToken(
                user.getId(),
                user.getEmail(),
                user.getRole().name()
        );
        String refreshToken = jwtTokenProvider.createRefreshToken(user.getId());

        MDC.put("userId", String.valueOf(user.getId()));
        log.info("login_success: email={}", user.getEmail());

        return TokenResponse.of(
                accessToken,
                refreshToken,
                jwtProperties.getAccessExpiration() / 1000
        );
    }

    public TokenResponse refresh(RefreshTokenRequest request) {
        String refreshToken = request.getRefreshToken();

        // 리프레시 토큰에서 userId 추출
        Long userId = jwtTokenProvider.getUserIdFromToken(refreshToken);

        // 리프레시 토큰 검증 (Redis 확인 포함)
        jwtTokenProvider.validateRefreshToken(userId, refreshToken);

        // 사용자 조회
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));

        // 새 토큰 발급
        String newAccessToken = jwtTokenProvider.createAccessToken(
                user.getId(),
                user.getEmail(),
                user.getRole().name()
        );
        String newRefreshToken = jwtTokenProvider.createRefreshToken(user.getId());

        log.info("Token refreshed for user: {}", user.getEmail());

        return TokenResponse.of(
                newAccessToken,
                newRefreshToken,
                jwtProperties.getAccessExpiration() / 1000
        );
    }

    public void logout(Long userId, String accessToken) {
        jwtTokenProvider.deleteRefreshToken(userId);
        jwtTokenProvider.blacklistAccessToken(accessToken);
        log.info("User logged out: userId={}", userId);
    }

    public UserResponse getMyInfo(String email) {
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new BusinessException(ErrorCode.USER_NOT_FOUND));
        return UserResponse.from(user);
    }
}
