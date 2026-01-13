from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Complaint(Base):
    """민원 테이블"""
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    category = Column(String(100))
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)


class Embedding(Base):
    """임베딩 테이블"""
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, index=True)
    vector = Column(Text)  # JSON string of embedding vector
    created_at = Column(DateTime, default=datetime.utcnow)
