from sqlalchemy.orm import Session as DBSession
from sqlalchemy import text
from app.models import Session as SessionModel, Message, init_metadata_db, get_metadata_engine, get_business_engine
from app.config import settings


def init_db():
    init_metadata_db()


def create_session(db: DBSession, title: str = "新会话") -> SessionModel:
    session = SessionModel(title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def list_sessions(db: DBSession) -> list[SessionModel]:
    return db.query(SessionModel).order_by(SessionModel.updated_at.desc()).all()


def get_session_by_id(db: DBSession, session_id: int) -> SessionModel | None:
    return db.query(SessionModel).filter(SessionModel.id == session_id).first()


def update_session_title(db: DBSession, session_id: int, title: str) -> SessionModel | None:
    session = get_session_by_id(db, session_id)
    if session:
        session.title = title
        db.commit()
        db.refresh(session)
    return session


def delete_session(db: DBSession, session_id: int) -> bool:
    session = get_session_by_id(db, session_id)
    if session:
        db.query(Message).filter(Message.session_id == session_id).delete()
        db.delete(session)
        db.commit()
        return True
    return False


def create_message(
    db: DBSession,
    session_id: int,
    role: str,
    content: str,
    sql_query: str | None = None,
    chart_data: str | None = None,
) -> Message:
    msg = Message(
        session_id=session_id,
        role=role,
        content=content,
        sql_query=sql_query,
        chart_data=chart_data,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def list_messages(db: DBSession, session_id: int) -> list[Message]:
    return db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at.asc()).all()


def execute_business_sql(sql: str) -> list[dict]:
    engine = get_business_engine()
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        columns = result.keys()
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
        return rows
