"""
데이터베이스 테이블 정의
"""

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    answer TEXT NOT NULL,
    model_name TEXT NOT NULL DEFAULT 'ollama',
    domain TEXT,
    category TEXT,
    rating INTEGER NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS query_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    domain TEXT,
    category TEXT,
    domain_confidence REAL,
    model_name TEXT NOT NULL DEFAULT 'ollama',
    response_time_ms INTEGER,
    compare_mode BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
