"""
답변 후처리 유틸리티
- LLM 답변에서 placeholder (010-xxxx, www.xx 등) 제거
- 도메인 정보를 활용해 구체적인 안내로 대체
"""
import re
from typing import Optional


def clean_answer(answer: str, domain: Optional[str] = None) -> str:
    """
    LLM 답변에서 placeholder를 검출하고 도메인 기반으로 대체
    
    Args:
        answer: LLM이 생성한 원본 답변
        domain: 분류된 도메인 (예: "K쇼핑", "금융/보험")
    
    Returns:
        정리된 답변
    
    예시:
        변경 전: "전화로 (010-xxxx) 또는 우리 웹사이트(www.xx)에서 문의를..."
        변경 후: "전화로 K쇼핑 고객센터 또는 K쇼핑 공식 홈페이지에서 문의를..."
    """
    if not answer:
        return answer
    
    # 도메인이 없으면 일반적 표현 사용
    org_name = domain if domain else "해당 기관"
    
    # placeholder 패턴 및 대체 문자열
    replacements = [
        # 전화번호 패턴
        (r'\(?\d{2,4}-[xX]{2,4}\)?', f'{org_name} 고객센터'),
        (r'\(?\d{2,4}-[xX]{2,4}-[xX]{2,4}\)?', f'{org_name} 고객센터'),
        (r'0\d{1,2}-\d{3,4}-\d{4}', f'{org_name} 고객센터'),  # 실제 번호처럼 보이는 가짜
        (r'1\d{3}-\d{4}', f'{org_name} 고객센터'),  # 1588-xxxx 형태
        (r'1\d{3}-[xX]{4}', f'{org_name} 고객센터'),
        
        # 웹사이트 패턴
        (r'www\.[xX]+\.?[xX]*', f'{org_name} 공식 홈페이지'),
        (r'www\.\S*example\S*', f'{org_name} 공식 홈페이지'),
        (r'http[s]?://[xX]+\S*', f'{org_name} 공식 홈페이지'),
        (r'\[웹사이트\s*주소\]', f'{org_name} 공식 홈페이지'),
        (r'\[홈페이지\]', f'{org_name} 공식 홈페이지'),
        
        # 이메일 패턴
        (r'\S+@[xX]+\.\S+', f'{org_name} 공식 이메일'),
        (r'\[이메일\s*주소\]', f'{org_name} 공식 이메일'),
        
        # 기타 placeholder
        (r'\[전화번호\]', f'{org_name} 고객센터'),
        (r'\[연락처\]', f'{org_name} 고객센터'),
        (r'\[담당\s*부서\s*번호\]', f'{org_name} 고객센터'),
        (r'\*\*\[.*?주소\]\*\*', f'{org_name} 공식 홈페이지'),
    ]
    
    cleaned = answer
    for pattern, replacement in replacements:
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    
    # 중복 제거 (예: "K쇼핑 고객센터 고객센터" → "K쇼핑 고객센터")
    cleaned = re.sub(rf'({org_name}\s+고객센터)\s+고객센터', r'\1', cleaned)
    cleaned = re.sub(rf'({org_name}\s+공식\s+홈페이지)\s+공식\s+홈페이지', r'\1', cleaned)
    
    return cleaned


def validate_answer(answer: str) -> dict:
    """
    답변 품질 검증 - placeholder가 남아있는지 확인
    
    Returns:
        {
            "is_valid": bool,
            "issues": list of detected issues
        }
    """
    issues = []
    
    # 의심스러운 패턴 검사
    suspicious_patterns = [
        (r'\d{2,4}-[xX]{2,4}', '전화번호 placeholder'),
        (r'www\.[xX]+', '웹사이트 placeholder'),
        (r'\[.*?번호.*?\]', '대괄호 placeholder'),
        (r'\[.*?주소.*?\]', '대괄호 placeholder'),
        (r'xxxx', '일반 placeholder'),
    ]
    
    for pattern, issue_type in suspicious_patterns:
        if re.search(pattern, answer, re.IGNORECASE):
            issues.append(issue_type)
    
    return {
        "is_valid": len(issues) == 0,
        "issues": issues
    }


# 테스트
if __name__ == "__main__":
    test_cases = [
        ("전화로 (010-xxxx) 또는 우리 웹사이트(www.xx)에서 문의를 해주시기 바랍니다.", "K쇼핑"),
        ("고객센터 1588-XXXX로 연락하시면 됩니다.", "금융/보험"),
        ("[카드사 고객센터 전화번호] 또는 **[카드사 웹사이트 주소]**를 방문해 주세요.", "금융/보험"),
        ("정상적인 답변입니다. 은행에 방문하시면 됩니다.", "금융/보험"),
    ]
    
    print("=" * 60)
    print("답변 후처리 테스트")
    print("=" * 60)
    
    for original, domain in test_cases:
        cleaned = clean_answer(original, domain)
        validation = validate_answer(cleaned)
        
        print(f"\n도메인: {domain}")
        print(f"원본: {original}")
        print(f"정리: {cleaned}")
        print(f"검증: {'✅ 통과' if validation['is_valid'] else '❌ 문제: ' + ', '.join(validation['issues'])}")
