"""프롬프트 인젝션 방어 및 입력 정제"""

import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# 프롬프트 인젝션 패턴 (대소문자 무시)
INJECTION_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions?|prompts?)", re.IGNORECASE),
     "Instruction override attempt"),
    (re.compile(r"ignore\s+(all\s+)?instructions?", re.IGNORECASE),
     "Instruction override attempt"),
    (re.compile(r"(disregard|forget)\s+(all\s+)?(previous|prior|above|your)(\s+(previous|prior))?\s+(instructions?|rules?|prompts?)", re.IGNORECASE),
     "Instruction override attempt"),
    (re.compile(r"you\s+are\s+now\s+(?:a|an)\s+", re.IGNORECASE),
     "Role hijacking attempt"),
    (re.compile(r"(act|pretend|behave)\s+as\s+(if\s+you\s+are|a|an)\s+", re.IGNORECASE),
     "Role hijacking attempt"),
    (re.compile(r"(reveal|show|display|print|output)\s+(your\s+)?(system\s+prompt|instructions?|rules?|hidden)", re.IGNORECASE),
     "System prompt extraction attempt"),
    (re.compile(r"what\s+(are|is)\s+your\s+(system\s+)?(prompt|instructions?|rules?)", re.IGNORECASE),
     "System prompt extraction attempt"),
    (re.compile(r"\[SYSTEM\]|\[INST\]|\<\|system\|?\>|<<SYS>>", re.IGNORECASE),
     "Prompt format injection"),
    (re.compile(r"(do\s+not|don'?t)\s+follow\s+(your\s+)?(previous|original|system)\s+(instructions?|rules?|prompts?)", re.IGNORECASE),
     "Instruction override attempt"),
    (re.compile(r"new\s+(instructions?|rules?|prompt)\s*:", re.IGNORECASE),
     "Instruction injection attempt"),
]

# 금융 조언 유도 패턴
FINANCIAL_ADVICE_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"(100|백)\s*%\s*(수익|이익|보장|확실)", re.IGNORECASE),
     "Unrealistic return guarantee request"),
    (re.compile(r"(guaranteed|확실한|무조건)\s*(수익|이익|profit|return)", re.IGNORECASE),
     "Guaranteed profit request"),
    (re.compile(r"(절대|반드시)\s*(오른다|수익|이익|돈)", re.IGNORECASE),
     "Absolute prediction request"),
    (re.compile(r"(insider|내부\s*정보|미공개\s*정보)", re.IGNORECASE),
     "Insider information request"),
]


def sanitize_user_input(message: str) -> Tuple[str, list[str]]:
    """
    사용자 입력을 검증하고 정제합니다.

    Args:
        message: 원본 사용자 입력

    Returns:
        (정제된 메시지, 경고 리스트)
        인젝션 패턴이 감지되면 해당 부분을 제거하고 경고를 반환합니다.
    """
    warnings = []
    sanitized = message

    # 인젝션 패턴 검사
    for pattern, description in INJECTION_PATTERNS:
        if pattern.search(sanitized):
            logger.warning(f"Injection pattern detected: {description} in input: {message[:100]}...")
            sanitized = pattern.sub("[FILTERED]", sanitized)
            warnings.append(description)

    # 금융 조언 유도 패턴 검사
    for pattern, description in FINANCIAL_ADVICE_PATTERNS:
        if pattern.search(sanitized):
            logger.warning(f"Financial advice pattern detected: {description} in input: {message[:100]}...")
            warnings.append(description)

    return sanitized, warnings


def wrap_user_input(message: str) -> str:
    """
    사용자 입력을 태그로 감싸서 시스템/사용자 입력을 분리합니다.

    Args:
        message: 사용자 입력 (이미 sanitize된 상태)

    Returns:
        <user_input> 태그로 감싼 메시지
    """
    return f"<user_input>{message}</user_input>"
