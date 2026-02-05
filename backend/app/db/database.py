"""
SQLite 데이터베이스 연결 및 초기화
"""
import aiosqlite
from pathlib import Path
from loguru import logger

from app.db.models import SCHEMA_SQL

# Docker: /app/data/claro.db, 로컬: ./data/claro.db
DB_PATH = Path("/app/data/claro.db") if Path("/app").exists() else Path("data/claro.db")


async def get_db() -> aiosqlite.Connection:
    """DB 연결 반환"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = await aiosqlite.connect(str(DB_PATH))
    db.row_factory = aiosqlite.Row
    return db


async def init_db():
    """테이블 생성 (앱 시작 시 호출)"""
    db = await get_db()
    try:
        await db.executescript(SCHEMA_SQL)
        await db.commit()
        logger.info(f"DB 초기화 완료: {DB_PATH}")
    finally:
        await db.close()
