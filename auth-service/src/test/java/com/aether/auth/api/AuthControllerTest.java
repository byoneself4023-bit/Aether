package com.aether.auth.api;

import com.aether.auth.api.auth.AuthController;
import com.aether.auth.application.auth.AuthService;
import com.aether.auth.domain.user.dto.*;
import com.aether.auth.domain.user.entity.Role;
import com.aether.auth.global.error.GlobalExceptionHandler;
import com.aether.auth.global.exception.BusinessException;
import com.aether.auth.global.exception.ErrorCode;
import com.aether.auth.global.security.JwtTokenProvider;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.MediaType;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.method.annotation.AuthenticationPrincipalArgumentResolver;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import java.util.List;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.BDDMockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@ExtendWith(MockitoExtension.class)
class AuthControllerTest {

    private MockMvc mockMvc;

    private ObjectMapper objectMapper;

    @Mock
    private AuthService authService;

    @Mock
    private JwtTokenProvider jwtTokenProvider;

    @InjectMocks
    private AuthController authController;

    @BeforeEach
    void setUp() {
        objectMapper = new ObjectMapper();
        mockMvc = MockMvcBuilders.standaloneSetup(authController)
                .setControllerAdvice(new GlobalExceptionHandler())
                .setCustomArgumentResolvers(new AuthenticationPrincipalArgumentResolver())
                .build();
    }

    @Nested
    @DisplayName("POST /api/auth/signup")
    class SignUp {

        @Test
        @DisplayName("성공 - 201 Created")
        void signUp_Success() throws Exception {
            SignUpRequest request = SignUpRequest.builder()
                    .email("test@example.com")
                    .password("Password1!")
                    .name("Test User")
                    .build();

            UserResponse response = UserResponse.builder()
                    .id(1L)
                    .email("test@example.com")
                    .name("Test User")
                    .role(Role.USER)
                    .enabled(true)
                    .build();

            given(authService.signUp(any(SignUpRequest.class))).willReturn(response);

            mockMvc.perform(post("/api/auth/signup")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isCreated())
                    .andExpect(jsonPath("$.success").value(true))
                    .andExpect(jsonPath("$.data.email").value("test@example.com"))
                    .andExpect(jsonPath("$.data.name").value("Test User"));
        }

        @Test
        @DisplayName("실패 - 이메일 중복 409")
        void signUp_DuplicateEmail() throws Exception {
            SignUpRequest request = SignUpRequest.builder()
                    .email("existing@example.com")
                    .password("Password1!")
                    .name("User")
                    .build();

            given(authService.signUp(any(SignUpRequest.class)))
                    .willThrow(new BusinessException(ErrorCode.DUPLICATE_EMAIL));

            mockMvc.perform(post("/api/auth/signup")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isConflict())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.error.code").value("U002"));
        }

        @Test
        @DisplayName("실패 - 유효성 검증 400")
        void signUp_ValidationFailed() throws Exception {
            SignUpRequest request = SignUpRequest.builder()
                    .email("invalid-email")
                    .password("short")
                    .name("")
                    .build();

            mockMvc.perform(post("/api/auth/signup")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isBadRequest());
        }

        @Test
        @DisplayName("실패 - 비밀번호 소문자만 400")
        void signUp_PasswordLowercaseOnly() throws Exception {
            SignUpRequest request = SignUpRequest.builder()
                    .email("test@example.com")
                    .password("abcdefgh")
                    .name("User")
                    .build();

            mockMvc.perform(post("/api/auth/signup")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isBadRequest())
                    .andExpect(jsonPath("$.error.code").value("C002"));
        }

        @Test
        @DisplayName("실패 - 비밀번호 숫자만 400")
        void signUp_PasswordDigitsOnly() throws Exception {
            SignUpRequest request = SignUpRequest.builder()
                    .email("test@example.com")
                    .password("12345678")
                    .name("User")
                    .build();

            mockMvc.perform(post("/api/auth/signup")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isBadRequest())
                    .andExpect(jsonPath("$.error.code").value("C002"));
        }

        @Test
        @DisplayName("실패 - 비밀번호 특수문자 없음 400")
        void signUp_PasswordNoSpecialChar() throws Exception {
            SignUpRequest request = SignUpRequest.builder()
                    .email("test@example.com")
                    .password("Password1")
                    .name("User")
                    .build();

            mockMvc.perform(post("/api/auth/signup")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isBadRequest())
                    .andExpect(jsonPath("$.error.code").value("C002"));
        }

        @Test
        @DisplayName("성공 - 강한 비밀번호")
        void signUp_StrongPassword() throws Exception {
            SignUpRequest request = SignUpRequest.builder()
                    .email("strong@example.com")
                    .password("StrongP@ss1")
                    .name("Strong User")
                    .build();

            UserResponse response = UserResponse.builder()
                    .id(2L)
                    .email("strong@example.com")
                    .name("Strong User")
                    .role(Role.USER)
                    .enabled(true)
                    .build();

            given(authService.signUp(any(SignUpRequest.class))).willReturn(response);

            mockMvc.perform(post("/api/auth/signup")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isCreated())
                    .andExpect(jsonPath("$.success").value(true));
        }
    }

    @Nested
    @DisplayName("POST /api/auth/login")
    class Login {

        @Test
        @DisplayName("성공 - 200 OK")
        void login_Success() throws Exception {
            LoginRequest request = LoginRequest.builder()
                    .email("test@example.com")
                    .password("Password1!")
                    .build();

            TokenResponse response = TokenResponse.of("accessToken", "refreshToken", 1800L);

            given(authService.login(any(LoginRequest.class))).willReturn(response);

            mockMvc.perform(post("/api/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.success").value(true))
                    .andExpect(jsonPath("$.data.accessToken").value("accessToken"))
                    .andExpect(jsonPath("$.data.refreshToken").value("refreshToken"))
                    .andExpect(jsonPath("$.data.tokenType").value("Bearer"));
        }

        @Test
        @DisplayName("실패 - 잘못된 자격 증명 401")
        void login_InvalidCredentials() throws Exception {
            LoginRequest request = LoginRequest.builder()
                    .email("test@example.com")
                    .password("wrongPassword")
                    .build();

            given(authService.login(any(LoginRequest.class)))
                    .willThrow(new BusinessException(ErrorCode.INVALID_CREDENTIALS));

            mockMvc.perform(post("/api/auth/login")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isUnauthorized())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.error.code").value("A001"));
        }
    }

    @Nested
    @DisplayName("POST /api/auth/refresh")
    class Refresh {

        @Test
        @DisplayName("성공 - 200 OK")
        void refresh_Success() throws Exception {
            RefreshTokenRequest request = new RefreshTokenRequest("validRefreshToken");

            TokenResponse response = TokenResponse.of("newAccessToken", "newRefreshToken", 1800L);

            given(authService.refresh(any(RefreshTokenRequest.class))).willReturn(response);

            mockMvc.perform(post("/api/auth/refresh")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.success").value(true))
                    .andExpect(jsonPath("$.data.accessToken").value("newAccessToken"));
        }

        @Test
        @DisplayName("실패 - 만료된 리프레시 토큰 401")
        void refresh_ExpiredToken() throws Exception {
            RefreshTokenRequest request = new RefreshTokenRequest("expiredRefreshToken");

            given(authService.refresh(any(RefreshTokenRequest.class)))
                    .willThrow(new BusinessException(ErrorCode.TOKEN_EXPIRED));

            mockMvc.perform(post("/api/auth/refresh")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isUnauthorized())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.error.code").value("A002"));
        }

        @Test
        @DisplayName("실패 - 불일치 리프레시 토큰 401")
        void refresh_MismatchToken() throws Exception {
            RefreshTokenRequest request = new RefreshTokenRequest("mismatchRefreshToken");

            given(authService.refresh(any(RefreshTokenRequest.class)))
                    .willThrow(new BusinessException(ErrorCode.INVALID_TOKEN));

            mockMvc.perform(post("/api/auth/refresh")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isUnauthorized())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.error.code").value("A003"));
        }
    }

    @Nested
    @DisplayName("POST /api/auth/logout")
    class Logout {

        @Test
        @DisplayName("성공 - 정상 Bearer 토큰")
        void logout_Success() throws Exception {
            given(jwtTokenProvider.getUserIdFromToken(anyString())).willReturn(1L);
            willDoNothing().given(authService).logout(anyLong(), anyString());

            mockMvc.perform(post("/api/auth/logout")
                            .header("Authorization", "Bearer valid.access.token"))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.success").value(true));

            verify(jwtTokenProvider).getUserIdFromToken("valid.access.token");
            verify(authService).logout(eq(1L), eq("valid.access.token"));
        }

        @Test
        @DisplayName("실패 - Bearer 접두사 없는 토큰 → 401")
        void logout_NoBearerPrefix() throws Exception {
            mockMvc.perform(post("/api/auth/logout")
                            .header("Authorization", "invalid-token-without-bearer"))
                    .andExpect(status().isUnauthorized())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.error.code").value("A003"));
        }

        @Test
        @DisplayName("실패 - 소문자 bearer → 401")
        void logout_LowercaseBearer() throws Exception {
            mockMvc.perform(post("/api/auth/logout")
                            .header("Authorization", "bearer some.token"))
                    .andExpect(status().isUnauthorized())
                    .andExpect(jsonPath("$.success").value(false))
                    .andExpect(jsonPath("$.error.code").value("A003"));
        }

        @Test
        @DisplayName("실패 - Authorization 헤더 없음 → 400")
        void logout_NoAuthorizationHeader() throws Exception {
            mockMvc.perform(post("/api/auth/logout"))
                    .andExpect(status().isBadRequest());
        }
    }

    @Nested
    @DisplayName("GET /api/auth/me")
    class Me {

        @Test
        @DisplayName("성공 - 내 정보 조회")
        void getMyInfo_Success() throws Exception {
            UserResponse response = UserResponse.builder()
                    .id(1L)
                    .email("test@example.com")
                    .name("Test User")
                    .role(Role.USER)
                    .enabled(true)
                    .build();

            given(authService.getMyInfo(anyString())).willReturn(response);

            org.springframework.security.core.userdetails.UserDetails userDetails =
                    org.springframework.security.core.userdetails.User.builder()
                            .username("test@example.com")
                            .password("")
                            .authorities("ROLE_USER")
                            .build();

            SecurityContextHolder.getContext().setAuthentication(
                    new UsernamePasswordAuthenticationToken(userDetails, null, userDetails.getAuthorities())
            );

            try {
                mockMvc.perform(get("/api/auth/me"))
                        .andExpect(status().isOk())
                        .andExpect(jsonPath("$.success").value(true))
                        .andExpect(jsonPath("$.data.email").value("test@example.com"))
                        .andExpect(jsonPath("$.data.name").value("Test User"));
            } finally {
                SecurityContextHolder.clearContext();
            }
        }

        @Test
        @DisplayName("실패 - 사용자 없음 404")
        void getMyInfo_UserNotFound() throws Exception {
            given(authService.getMyInfo(anyString()))
                    .willThrow(new BusinessException(ErrorCode.USER_NOT_FOUND));

            org.springframework.security.core.userdetails.UserDetails userDetails =
                    org.springframework.security.core.userdetails.User.builder()
                            .username("deleted@example.com")
                            .password("")
                            .authorities("ROLE_USER")
                            .build();

            SecurityContextHolder.getContext().setAuthentication(
                    new UsernamePasswordAuthenticationToken(userDetails, null, userDetails.getAuthorities())
            );

            try {
                mockMvc.perform(get("/api/auth/me"))
                        .andExpect(status().isNotFound())
                        .andExpect(jsonPath("$.success").value(false))
                        .andExpect(jsonPath("$.error.code").value("U001"));
            } finally {
                SecurityContextHolder.clearContext();
            }
        }
    }
}
