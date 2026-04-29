"""
SSE 流式对话 API
"""
import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.models import get_db, get_business_db
from app.services.db_service import get_session_by_id, create_message
from app.services.session_service import (
    get_schema_string,
    update_session_if_first_message,
    save_assistant_message,
)
from app.agents.graph import run_agent_stream
from app.core.llm import get_qwen_client
from app.core.prompts import build_nl2sql_prompt, build_explanation_prompt
from app.core.safety import extract_sql_from_response, sanitize_sql, validate_sql
from app.services.db_service import execute_business_sql

router = APIRouter()


async def generate_stream_response(
    session_id: int,
    query: str,
    db: Session,
):
    """
    生成 SSE 流式响应
    """
    try:
        # 1. 首先发送用户消息到前端（作为确认）
        yield f"event: user_message\ndata: {json.dumps({'content': query}, ensure_ascii=False)}\n\n"
        
        # 2. 获取 schema
        schema = get_schema_string(db)
        
        if not schema:
            yield f"event: error\ndata: {json.dumps({'content': '无法获取数据库 schema'}, ensure_ascii=False)}\n\n"
            return
        
        # 3. 生成 SQL（流式）
        messages = build_nl2sql_prompt(query, schema)
        client = get_qwen_client()
        
        sql_content = ""
        sql_partial = ""
        
        async for chunk in client.chat(messages, stream=True, temperature=0.3):
            sql_partial += chunk
            yield f"event: sql_partial\ndata: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
        
        # 4. 提取并校验 SQL
        sql = extract_sql_from_response(sql_partial)
        
        if not sql:
            error_msg = "无法从 AI 响应中提取有效的 SQL 语句"
            yield f"event: error\ndata: {json.dumps({'content': error_msg}, ensure_ascii=False)}\n\n"
            return
        
        sql = sanitize_sql(sql)
        is_safe, error_msg = validate_sql(sql)
        
        if not is_safe:
            yield f"event: error\ndata: {json.dumps({'content': f'SQL 校验失败: {error_msg}'}, ensure_ascii=False)}\n\n"
            return
        
        # 发送完整 SQL
        yield f"event: sql\ndata: {json.dumps({'sql': sql}, ensure_ascii=False)}\n\n"
        
        # 5. 执行 SQL
        try:
            result = execute_business_sql(sql)
            yield f"event: result\ndata: {json.dumps({'result': result}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'content': f'SQL 执行失败: {str(e)}'}, ensure_ascii=False)}\n\n"
            return
        
        # 6. 生成解释（流式）
        explanation_partial = ""
        
        if result:
            explanation_messages = build_explanation_prompt(sql, result)
            
            async for chunk in client.chat(explanation_messages, stream=True, temperature=0.3):
                explanation_partial += chunk
                yield f"event: explanation_partial\ndata: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
            
            explanation = explanation_partial.strip()
        else:
            explanation = "查询结果为空"
        
        yield f"event: explanation\ndata: {json.dumps({'content': explanation}, ensure_ascii=False)}\n\n"
        
        # 7. 推荐图表类型
        chart_type = recommend_chart_type(sql, result)
        yield f"event: chart\ndata: {json.dumps({'chart_type': chart_type}, ensure_ascii=False)}\n\n"
        
        # 8. 完成
        yield f"event: done\ndata: {json.dumps({'session_id': session_id}, ensure_ascii=False)}\n\n"
        
        # 9. 保存消息到数据库
        chart_data_json = json.dumps({
            "chart_type": chart_type,
            "data": result,
        })
        
        # 保存 AI 响应
        save_assistant_message(
            db,
            session_id=session_id,
            content=explanation,
            sql=sql,
            chart_data=chart_data_json,
        )
        
        # 更新会话标题（如果是第一条消息）
        update_session_if_first_message(db, session_id, query)
        
    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'content': f'服务器错误: {str(e)}'}, ensure_ascii=False)}\n\n"


def recommend_chart_type(sql: str, result: list) -> str:
    """
    根据 SQL 和结果推荐图表类型（简单规则版）
    """
    sql_upper = sql.upper()
    
    # 如果有 ORDER BY 或 LIMIT，适合柱状图
    if "ORDER BY" in sql_upper or "LIMIT" in sql_upper:
        return "bar"
    
    # 如果是统计类（COUNT, SUM, AVG），检查是否有分组
    if "GROUP BY" in sql_upper:
        return "bar"
    
    # 如果结果只有一行一列，适合显示数字
    if len(result) == 1 and len(result[0]) == 1:
        return "table"
    
    # 默认返回表格
    return "table"


@router.post("/sessions/{session_id}/stream")
async def chat_stream(
    session_id: int,
    query: str,
    db: Session = Depends(get_db),
):
    """
    SSE 流式对话接口
    
    Args:
        session_id: 会话 ID
        query: 用户问题
        
    Returns:
        SSE 流式响应
    """
    # 验证会话存在
    session = get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # 先保存用户消息
    create_message(
        db,
        session_id=session_id,
        role="user",
        content=query,
    )
    
    return StreamingResponse(
        generate_stream_response(session_id, query, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


class ChatRequest(BaseException if False else object):
    """请求模型"""
    def __init__(self, query: str):
        self.query = query


from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
