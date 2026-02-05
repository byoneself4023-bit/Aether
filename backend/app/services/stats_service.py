"""통계 서비스 — SQLite 집계 + 캐싱"""
import time
from loguru import logger
from app.core.config import settings
from app.db.database import get_db


class _StatsCache:
    """간단한 TTL 캐시"""

    def __init__(self, ttl: int = 60):
        self._ttl = ttl
        self._store: dict[str, tuple[float, object]] = {}

    def get(self, key: str):
        entry = self._store.get(key)
        if entry and (time.time() - entry[0]) < self._ttl:
            return entry[1]
        return None

    def set(self, key: str, value):
        self._store[key] = (time.time(), value)

    def invalidate(self, key: str = None):
        if key:
            self._store.pop(key, None)
        else:
            self._store.clear()


_cache = _StatsCache(ttl=settings.STATS_CACHE_TTL)


class StatsService:
    async def get_model_stats(self) -> list:
        """모델별 종합 통계 (쿼리 수, 평균 응답시간, 만족도)"""
        cached = _cache.get("model_stats")
        if cached is not None:
            return cached

        db = await get_db()
        try:
            cursor = await db.execute("""
                SELECT
                    q.model_name,
                    COUNT(q.id) AS total_queries,
                    COALESCE(AVG(q.response_time_ms), 0) AS avg_response_time_ms,
                    COALESCE(f.helpful_rate, 0) AS helpful_rate,
                    COALESCE(f.total_feedback, 0) AS total_feedback
                FROM query_log q
                LEFT JOIN (
                    SELECT
                        model_name,
                        AVG(CAST(rating AS REAL)) AS helpful_rate,
                        COUNT(*) AS total_feedback
                    FROM feedback
                    GROUP BY model_name
                ) f ON q.model_name = f.model_name
                GROUP BY q.model_name
                ORDER BY total_queries DESC
            """)
            rows = await cursor.fetchall()
            result = [
                {
                    "model_name": r[0],
                    "total_queries": r[1],
                    "avg_response_time_ms": round(r[2], 1),
                    "helpful_rate": round(r[3], 3) if r[3] else None,
                    "total_feedback": r[4],
                }
                for r in rows
            ]
            _cache.set("model_stats", result)
            return result
        finally:
            await db.close()

    async def get_daily_queries(self, days: int = 30) -> list:
        """일별 쿼리 수"""
        cache_key = f"daily_{days}"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        db = await get_db()
        try:
            cursor = await db.execute("""
                SELECT
                    DATE(created_at) AS date,
                    COUNT(*) AS count
                FROM query_log
                WHERE created_at >= DATE('now', ? || ' days')
                GROUP BY DATE(created_at)
                ORDER BY date
            """, (f"-{days}",))
            rows = await cursor.fetchall()
            result = [{"date": r[0], "count": r[1]} for r in rows]
            _cache.set(cache_key, result)
            return result
        finally:
            await db.close()

    async def get_domain_breakdown(self) -> list:
        """도메인별 분포"""
        cached = _cache.get("domains")
        if cached is not None:
            return cached

        db = await get_db()
        try:
            cursor = await db.execute("""
                SELECT
                    COALESCE(domain, '미분류') AS domain,
                    COUNT(*) AS count
                FROM query_log
                GROUP BY domain
                ORDER BY count DESC
            """)
            rows = await cursor.fetchall()
            result = [{"domain": r[0], "count": r[1]} for r in rows]
            _cache.set("domains", result)
            return result
        finally:
            await db.close()

    async def get_recent_feedback(self, limit: int = 20) -> list:
        """최근 피드백 목록"""
        db = await get_db()
        try:
            cursor = await db.execute("""
                SELECT id, query, answer, model_name, domain, rating, created_at
                FROM feedback
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            rows = await cursor.fetchall()
            return [
                {
                    "id": r[0],
                    "query": r[1],
                    "answer": r[2][:200],
                    "model_name": r[3],
                    "domain": r[4],
                    "rating": r[5],
                    "created_at": r[6],
                }
                for r in rows
            ]
        finally:
            await db.close()

    async def get_query_logs(
        self, search: str = "", domain: str = "", limit: int = 50, offset: int = 0
    ) -> dict:
        """쿼리 로그 목록 (히스토리 페이지용)"""
        db = await get_db()
        try:
            conditions = []
            params: list = []

            if search:
                conditions.append("query LIKE ?")
                params.append(f"%{search}%")
            if domain:
                conditions.append("domain = ?")
                params.append(domain)

            where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

            # 총 개수
            count_cursor = await db.execute(
                f"SELECT COUNT(*) FROM query_log {where}", params
            )
            total = (await count_cursor.fetchone())[0]

            # 목록
            cursor = await db.execute(
                f"""
                SELECT id, query, domain, category, domain_confidence,
                       model_name, response_time_ms, created_at
                FROM query_log
                {where}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
                """,
                params + [limit, offset],
            )
            rows = await cursor.fetchall()
            items = [
                {
                    "id": r[0],
                    "query": r[1],
                    "domain": r[2],
                    "category": r[3],
                    "domain_confidence": r[4],
                    "model_name": r[5],
                    "response_time_ms": r[6],
                    "created_at": r[7],
                }
                for r in rows
            ]
            return {"items": items, "total": total}
        finally:
            await db.close()
