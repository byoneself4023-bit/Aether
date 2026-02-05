"""
피드백 서비스 — 피드백 저장/조회 + 쿼리 이력 로깅
"""
from typing import Optional
from loguru import logger

from app.db.database import get_db


class FeedbackService:
    async def save_feedback(
        self,
        query: str,
        answer: str,
        rating: int,
        model_name: str = "ollama",
        domain: Optional[str] = None,
        category: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> int:
        """피드백 저장 → ID 반환"""
        db = await get_db()
        try:
            cursor = await db.execute(
                """INSERT INTO feedback (query, answer, model_name, domain, category, rating, comment)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (query, answer, model_name, domain, category, rating, comment),
            )
            await db.commit()
            feedback_id = cursor.lastrowid
            logger.info(f"피드백 저장: id={feedback_id}, rating={rating}, model={model_name}")
            return feedback_id
        finally:
            await db.close()

    async def get_recent(self, limit: int = 20) -> list[dict]:
        """최근 피드백 조회"""
        db = await get_db()
        try:
            cursor = await db.execute(
                "SELECT * FROM feedback ORDER BY created_at DESC LIMIT ?",
                (limit,),
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            await db.close()

    async def log_query(
        self,
        query: str,
        domain: Optional[str] = None,
        category: Optional[str] = None,
        domain_confidence: Optional[float] = None,
        model_name: str = "ollama",
        response_time_ms: Optional[int] = None,
        compare_mode: bool = False,
    ):
        """쿼리 이력 저장 (대시보드용)"""
        db = await get_db()
        try:
            await db.execute(
                """INSERT INTO query_log (query, domain, category, domain_confidence, model_name, response_time_ms, compare_mode)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (query, domain, category, domain_confidence, model_name, response_time_ms, compare_mode),
            )
            await db.commit()
        except Exception as e:
            logger.warning(f"쿼리 로깅 실패: {e}")
        finally:
            await db.close()
