package com.aether.auth.application;

import com.aether.auth.application.auth.AuthService;
import com.aether.auth.domain.user.dto.*;
import com.aether.auth.domain.user.entity.Role;
import com.aether.auth.domain.user.entity.User;
import com.aether.auth.domain.user.repository.UserRepository;
import com.aether.auth.global.config.JwtProperties;
import com.aether.auth.global.exception.BusinessException;
import com.aether.auth.global.exception.ErrorCode;
import com.aether.auth.global.security.JwtTokenProvider;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.BDDMockito.*;

@ExtendWith(MockitoExtension.class)
class AuthServiceTest {

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

    private User testUser;

    @BeforeEach
    void setUp() {
        testUser = User.builder()
                .id(1L)
                .email("test@example.com")
                .password("encodedPassword")
                .name("Test User")
                .role(Role.USER)
                .enabled(true)
                .build();
    }

    @Nested
    @DisplayName("회원가입")
    class SignUp {

        @Test
        @DisplayName("성공")
        void signUp_Success() {
            // given
            SignUpRequest request = SignUpRequest.builder()
                    .email("new@example.com")
                    .password("password123")
                    .name("New User")
                    .build();

            given(userRepository.existsByEmail(anyString())).willReturn(false);
            given(passwordEncoder.encode(anyString())).willReturn("encodedPassword");
            given(userRepository.save(any(User.class))).willAnswer(invocation -> {
                User user = invocation.getArgument(0);
                return User.builder()
                        .id(1L)
                        .email(user.getEmail())
                        .password(user.getPassword())
                        .name(user.getName())
                        .role(Role.USER)
                        .enabled(true)
                        .build();
            });

            // when
            UserResponse response = authService.signUp(request);

            // then
            assertThat(response).isNotNull();
            assertThat(response.getEmail()).isEqualTo("new@example.com");
            assertThat(response.getName()).isEqualTo("New User");
            verify(userRepository).save(any(User.class));
        }

        @Test
        @DisplayName("실패 - 이메일 중복")
        void signUp_DuplicateEmail() {
            // given
            SignUpRequest request = SignUpRequest.builder()
                    .email("existing@example.com")
                    .password("password123")
                    .name("User")
                    .build();

            given(userRepository.existsByEmail(anyString())).willReturn(true);

            // when & then
            assertThatThrownBy(() -> authService.signUp(request))
                    .isInstanceOf(BusinessException.class)
                    .satisfies(e -> {
                        BusinessException be = (BusinessException) e;
                        assertThat(be.getErrorCode()).isEqualTo(ErrorCode.DUPLICATE_EMAIL);
                    });
        }
    }

    @Nested
    @DisplayName("로그인")
    class Login {

        @Test
        @DisplayName("성공")
        void login_Success() {
            // given
            LoginRequest request = LoginRequest.builder()
                    .email("test@example.com")
                    .password("password123")
                    .build();

            given(userRepository.findByEmail(anyString())).willReturn(Optional.of(testUser));
            given(passwordEncoder.matches(anyString(), anyString())).willReturn(true);
            given(jwtTokenProvider.createAccessToken(anyLong(), anyString(), anyString()))
                    .willReturn("accessToken");
            given(jwtTokenProvider.createRefreshToken(anyLong())).willReturn("refreshToken");
            given(jwtProperties.getAccessExpiration()).willReturn(1800000L);

            // when
            TokenResponse response = authService.login(request);

            // then
            assertThat(response).isNotNull();
            assertThat(response.getAccessToken()).isEqualTo("accessToken");
            assertThat(response.getRefreshToken()).isEqualTo("refreshToken");
            assertThat(response.getTokenType()).isEqualTo("Bearer");
        }

        @Test
        @DisplayName("실패 - 사용자 없음")
        void login_UserNotFound() {
            // given
            LoginRequest request = LoginRequest.builder()
                    .email("notfound@example.com")
                    .password("password123")
                    .build();

            given(userRepository.findByEmail(anyString())).willReturn(Optional.empty());

            // when & then
            assertThatThrownBy(() -> authService.login(request))
                    .isInstanceOf(BusinessException.class)
                    .satisfies(e -> {
                        BusinessException be = (BusinessException) e;
                        assertThat(be.getErrorCode()).isEqualTo(ErrorCode.INVALID_CREDENTIALS);
                    });
        }

        @Test
        @DisplayName("실패 - 비활성화된 계정")
        void login_DisabledAccount() {
            // given
            User disabledUser = User.builder()
                    .id(2L)
                    .email("disabled@example.com")
                    .password("encodedPassword")
                    .name("Disabled User")
                    .role(Role.USER)
                    .enabled(false)
                    .build();

            LoginRequest request = LoginRequest.builder()
                    .email("disabled@example.com")
                    .password("password123")
                    .build();

            given(userRepository.findByEmail(anyString())).willReturn(Optional.of(disabledUser));
            given(passwordEncoder.matches(anyString(), anyString())).willReturn(true);

            // when & then
            assertThatThrownBy(() -> authService.login(request))
                    .isInstanceOf(BusinessException.class)
                    .satisfies(e -> {
                        BusinessException be = (BusinessException) e;
                        assertThat(be.getErrorCode()).isEqualTo(ErrorCode.INVALID_CREDENTIALS);
                    });
        }

        @Test
        @DisplayName("실패 - 비밀번호 불일치")
        void login_WrongPassword() {
            // given
            LoginRequest request = LoginRequest.builder()
                    .email("test@example.com")
                    .password("wrongPassword")
                    .build();

            given(userRepository.findByEmail(anyString())).willReturn(Optional.of(testUser));
            given(passwordEncoder.matches(anyString(), anyString())).willReturn(false);

            // when & then
            assertThatThrownBy(() -> authService.login(request))
                    .isInstanceOf(BusinessException.class)
                    .satisfies(e -> {
                        BusinessException be = (BusinessException) e;
                        assertThat(be.getErrorCode()).isEqualTo(ErrorCode.INVALID_CREDENTIALS);
                    });
        }
    }

    @Nested
    @DisplayName("토큰 갱신")
    class Refresh {

        @Test
        @DisplayName("성공")
        void refresh_Success() {
            // given
            RefreshTokenRequest request = new RefreshTokenRequest("validRefreshToken");

            given(jwtTokenProvider.getUserIdFromToken(anyString())).willReturn(1L);
            given(jwtTokenProvider.validateRefreshToken(anyLong(), anyString())).willReturn(true);
            given(userRepository.findById(anyLong())).willReturn(Optional.of(testUser));
            given(jwtTokenProvider.createAccessToken(anyLong(), anyString(), anyString()))
                    .willReturn("newAccessToken");
            given(jwtTokenProvider.createRefreshToken(anyLong())).willReturn("newRefreshToken");
            given(jwtProperties.getAccessExpiration()).willReturn(1800000L);

            // when
            TokenResponse response = authService.refresh(request);

            // then
            assertThat(response).isNotNull();
            assertThat(response.getAccessToken()).isEqualTo("newAccessToken");
            assertThat(response.getRefreshToken()).isEqualTo("newRefreshToken");
        }

        @Test
        @DisplayName("실패 - 리프레시 토큰 없음")
        void refresh_TokenNotFound() {
            // given
            RefreshTokenRequest request = new RefreshTokenRequest("invalidToken");

            given(jwtTokenProvider.getUserIdFromToken(anyString())).willReturn(1L);
            given(jwtTokenProvider.validateRefreshToken(anyLong(), anyString()))
                    .willThrow(new BusinessException(ErrorCode.REFRESH_TOKEN_NOT_FOUND));

            // when & then
            assertThatThrownBy(() -> authService.refresh(request))
                    .isInstanceOf(BusinessException.class)
                    .satisfies(e -> {
                        BusinessException be = (BusinessException) e;
                        assertThat(be.getErrorCode()).isEqualTo(ErrorCode.REFRESH_TOKEN_NOT_FOUND);
                    });
        }

        @Test
        @DisplayName("실패 - 사용자 없음")
        void refresh_UserNotFound() {
            // given
            RefreshTokenRequest request = new RefreshTokenRequest("validRefreshToken");

            given(jwtTokenProvider.getUserIdFromToken(anyString())).willReturn(999L);
            given(jwtTokenProvider.validateRefreshToken(anyLong(), anyString())).willReturn(true);
            given(userRepository.findById(999L)).willReturn(Optional.empty());

            // when & then
            assertThatThrownBy(() -> authService.refresh(request))
                    .isInstanceOf(BusinessException.class)
                    .satisfies(e -> {
                        BusinessException be = (BusinessException) e;
                        assertThat(be.getErrorCode()).isEqualTo(ErrorCode.USER_NOT_FOUND);
                    });
        }
    }

    @Nested
    @DisplayName("로그아웃")
    class Logout {

        @Test
        @DisplayName("성공")
        void logout_Success() {
            // given
            Long userId = 1L;
            String accessToken = "some.access.token";
            willDoNothing().given(jwtTokenProvider).deleteRefreshToken(anyLong());
            willDoNothing().given(jwtTokenProvider).blacklistAccessToken(anyString());

            // when & then
            assertThatCode(() -> authService.logout(userId, accessToken)).doesNotThrowAnyException();
            verify(jwtTokenProvider).deleteRefreshToken(userId);
            verify(jwtTokenProvider).blacklistAccessToken(accessToken);
        }
    }
}
