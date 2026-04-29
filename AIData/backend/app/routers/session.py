from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.models import get_db
from app.services import (
    create_session,
    list_sessions,
    get_session_by_id,
    update_session_title,
    delete_session,
    create_message,
    list_messages,
    init_db,
)

router = APIRouter()


# --- Pydantic Schemas ---

class SessionCreate(BaseModel):
    title: Optional[str] = None


class SessionUpdateTitle(BaseModel):
    title: str


class MessageCreate(BaseModel):
    session_id: int
    role: str
    content: str
    sql_query: Optional[str] = None
    chart_data: Optional[str] = None


class SessionResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    sql_query: Optional[str]
    chart_data: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# --- Endpoints ---

@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def api_create_session(body: SessionCreate, db: Session = Depends(get_db)):
    init_db()
    title = body.title or "新会话"
    session = create_session(db, title=title)
    return session


@router.get("/sessions", response_model=list[SessionResponse])
def api_list_sessions(db: Session = Depends(get_db)):
    init_db()
    return list_sessions(db)


@router.get("/sessions/{session_id}", response_model=SessionResponse)
def api_get_session(session_id: int, db: Session = Depends(get_db)):
    session = get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.patch("/sessions/{session_id}/title", response_model=SessionResponse)
def api_update_title(session_id: int, body: SessionUpdateTitle, db: Session = Depends(get_db)):
    session = update_session_title(db, session_id, body.title)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_delete_session(session_id: int, db: Session = Depends(get_db)):
    success = delete_session(db, session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")


@router.get("/sessions/{session_id}/messages", response_model=list[MessageResponse])
def api_get_messages(session_id: int, db: Session = Depends(get_db)):
    if not get_session_by_id(db, session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return list_messages(db, session_id)


@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def api_create_message(body: MessageCreate, db: Session = Depends(get_db)):
    if not get_session_by_id(db, body.session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    msg = create_message(
        db,
        session_id=body.session_id,
        role=body.role,
        content=body.content,
        sql_query=body.sql_query,
        chart_data=body.chart_data,
    )
    return msg
