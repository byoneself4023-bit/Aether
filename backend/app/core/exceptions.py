"""
커스텀 예외 정의
"""


class ClaroError(Exception):
    """Claro 기본 예외"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ResourceNotReadyError(ClaroError):
    """리소스 미준비 예외"""
    def __init__(self, resource_name: str):
        super().__init__(
            message=f"{resource_name}이(가) 아직 준비되지 않았습니다.",
            status_code=503,
        )


class ClassificationError(ClaroError):
    """분류 실패 예외"""
    def __init__(self, detail: str = "분류 중 오류가 발생했습니다."):
        super().__init__(message=detail, status_code=500)


class SearchError(ClaroError):
    """검색 실패 예외"""
    def __init__(self, detail: str = "검색 중 오류가 발생했습니다."):
        super().__init__(message=detail, status_code=500)


class GenerationError(ClaroError):
    """생성 실패 예외"""
    def __init__(self, detail: str = "답변 생성 중 오류가 발생했습니다."):
        super().__init__(message=detail, status_code=500)
