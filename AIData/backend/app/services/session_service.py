"""
会话服务 - 包含上下文管理、自动标题、上下文裁剪
"""
import json
from datetime import datetime
from typing import TypedDict

from sqlalchemy.orm import Session as DBSession
from app.models import Session as SessionModel, Message
from app.services.db_service import (
    create_session as db_create_session,
    list_sessions as db_list_sessions,
    get_session_by_id as db_get_session,
    update_session_title as db_update_title,
    delete_session as db_delete_session,
    create_message as db_create_message,
    list_messages as db_list_messages,
)


# 最大 token 估算（简单按字符数估算，1 token ≈ 4 字符）
MAX_TOKENS = 32000  # Qwen3-32B 支持 32K
CHARS_PER_TOKEN = 4
MAX_CHARS = MAX_TOKENS * CHARS_PER_TOKEN


class MessageHistory(TypedDict):
    """消息历史结构"""
    role: str
    content: str
    sql: str | None


def generate_title_from_query(query: str) -> str:
    """
    从第一条用户消息生成会话标题
    
    Args:
        query: 用户的第一条消息
        
    Returns:
        标题（最多20个字符）
    """
    # 清理消息，去除换行和多余空白
    title = query.replace("\n", " ").strip()
    
    # 截取前20个字符
    if len(title) > 20:
        title = title[:20] + "..."
    
    return title or "新会话"


def build_context_history(messages: list[Message], max_chars: int = MAX_CHARS) -> list[MessageHistory]:
    """
    构建上下文历史（包含 schema 注入）
    
    Args:
        messages: 数据库中的消息列表
        max_chars: 最大字符数
        
    Returns:
        裁剪后的消息历史
    """
    context = []
    total_chars = 0
    
    # 从最新到最旧遍历
    for msg in reversed(messages):
        msg_dict = MessageHistory(
            role=msg.role,
            content=msg.content,
            sql=msg.sql_query,
        )
        
        # 估算这条消息的大小
        msg_size = len(json.dumps(msg_dict, ensure_ascii=False))
        
        # 如果加上这条消息会超过限制，从最旧的开始丢弃
        if total_chars + msg_size > max_chars:
            # 跳过这条消息和更旧的消息
            break
        
        context.insert(0, msg_dict)
        total_chars += msg_size
    
    return context


def trim_context_for_schema(messages: list[MessageHistory], schema: str, available_chars: int) -> list[MessageHistory]:
    """
    为 schema 腾出空间，裁剪消息历史
    
    Args:
        messages: 当前消息历史
        schema: schema 描述
        available_chars: 可用字符数
        
    Returns:
        裁剪后的消息历史
    """
    schema_chars = len(schema)
    budget = available_chars - schema_chars - 2000  # 留 2000 缓冲
    
    if budget < 0:
        return []
    
    result = []
    total_chars = 0
    
    for msg in messages:
        msg_str = json.dumps(msg, ensure_ascii=False)
        if total_chars + len(msg_str) > budget:
            break
        result.append(msg)
        total_chars += len(msg_str)
    
    return result


def get_session_with_context(db: DBSession, session_id: int) -> tuple[SessionModel | None, list[MessageHistory]]:
    """
    获取会话及其上下文历史
    
    Returns:
        (session, messages) - 如果会话不存在则 session 为 None
    """
    session = db_get_session(db, session_id)
    if not session:
        return None, []
    
    messages = db_list_messages(db, session_id)
    context = build_context_history(messages)
    
    return session, context


def create_session_with_auto_title(db: DBSession, first_query: str = None) -> SessionModel:
    """
    创建会话，自动生成标题
    
    Args:
        db: 数据库会话
        first_query: 第一条用户消息（用于生成标题）
        
    Returns:
        创建的会话
    """
    title = generate_title_from_query(first_query) if first_query else "新会话"
    return db_create_session(db, title=title)


def update_session_if_first_message(db: DBSession, session_id: int, user_query: str) -> SessionModel | None:
    """
    如果是第一条用户消息，更新会话标题
    
    Args:
        db: 数据库会话
        session_id: 会话 ID
        user_query: 用户消息
        
    Returns:
        更新后的会话
    """
    session = db_get_session(db, session_id)
    if not session:
        return None
    
    # 检查是否是第一条用户消息
    messages = db_list_messages(db, session_id)
    user_messages = [m for m in messages if m.role == "user"]
    
    if len(user_messages) == 0:
        # 第一条用户消息，更新标题
        new_title = generate_title_from_query(user_query)
        return db_update_title(db, session_id, new_title)
    
    return session


def save_assistant_message(
    db: DBSession,
    session_id: int,
    content: str,
    sql: str | None = None,
    chart_data: str | None = None,
) -> Message:
    """
    保存 AI 助手消息
    
    Args:
        db: 数据库会话
        session_id: 会话 ID
        content: 回答内容
        sql: 生成的 SQL
        chart_data: 图表数据（JSON）
        
    Returns:
        创建的消息
    """
    return db_create_message(
        db,
        session_id=session_id,
        role="assistant",
        content=content,
        sql_query=sql,
        chart_data=chart_data,
    )


def get_schema_string(db: DBSession) -> str:
    """
    获取数据库 schema 描述字符串
    
    Args:
        db: 业务数据库会话
        
    Returns:
        schema 描述字符串
    """
    from sqlalchemy import inspect, text
    
    try:
        # 获取业务数据库引擎
        from app.models import get_business_engine
        engine = get_business_engine()
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        schema_parts = []
        
        for table_name in tables:
            columns = inspector.get_columns(table_name)
            
            col_defs = []
            for col in columns:
                col_type = str(col["type"])
                col_defs.append(f"  - {col['name']}: {col_type}")
            
            schema_parts.append(f"表名: {table_name}")
            schema_parts.append("\n".join(col_defs))
            schema_parts.append("")
        
        return "\n".join(schema_parts).strip()
        
    except Exception as e:
        return f"无法获取 schema: {str(e)}"
