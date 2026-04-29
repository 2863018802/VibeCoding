from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func
from pathlib import Path

from app.config import settings

Base = declarative_base()


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, default="新会话")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, nullable=False, index=True)
    role = Column(String(20), nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    sql_query = Column(Text, nullable=True)
    chart_data = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())


def get_metadata_engine():
    db_path = Path(settings.metadata_db_path).resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})


def get_business_engine():
    db_path = Path(settings.business_db_path).resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})


def get_session_factory(engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal


# Singleton engine/session
_metadata_engine = None
_business_engine = None


def get_db():
    global _metadata_engine
    if _metadata_engine is None:
        _metadata_engine = get_metadata_engine()
        Base.metadata.create_all(bind=_metadata_engine)
    SessionLocal = get_session_factory(_metadata_engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_business_db():
    global _business_engine
    if _business_engine is None:
        _business_engine = get_business_engine()
    SessionLocal = get_session_factory(_business_engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_metadata_db():
    global _metadata_engine
    _metadata_engine = get_metadata_engine()
    Base.metadata.create_all(bind=_metadata_engine)
