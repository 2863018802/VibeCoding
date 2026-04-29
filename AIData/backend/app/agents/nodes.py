"""
LangGraph Agent Nodes 定义
"""
import json
import re
from typing import TypedDict

from app.core.llm import get_qwen_client
from app.core.prompts import build_nl2sql_prompt, build_explanation_prompt, build_chart_recommendation_prompt
from app.core.safety import validate_sql, sanitize_sql, extract_sql_from_response
from app.services.db_service import execute_business_sql


class AgentState(TypedDict):
    """Agent 状态"""
    query: str                      # 用户原始问题
    schema: str                     # 数据库 schema
    sql: str | None                 # 生成的 SQL
    sql_error: str | None           # SQL 执行错误
    result: list | None             # 查询结果
    explanation: str | None         # 自然语言解释
    chart_type: str | None          # 推荐的图表类型
    messages: list[dict]           # 消息历史（用于流式）
    error: str | None               # 整体错误


def generate_sql(state: AgentState) -> AgentState:
    """
    Node: 生成 SQL 语句
    """
    try:
        # 构建提示词
        messages = build_nl2sql_prompt(state["query"], state["schema"])
        
        # 调用 LLM
        client = get_qwen_client()
        response = ""
        
        for chunk in client.chat(messages, stream=False, temperature=0.3):
            response += chunk
        
        # 提取 SQL
        sql = extract_sql_from_response(response)
        
        if not sql:
            state["error"] = "无法从响应中提取 SQL 语句"
            return state
        
        # 清理 SQL
        sql = sanitize_sql(sql)
        
        # 校验 SQL
        is_safe, error_msg = validate_sql(sql)
        if not is_safe:
            state["error"] = f"SQL 校验失败: {error_msg}"
            return state
        
        state["sql"] = sql
        state["messages"] = messages
        
    except Exception as e:
        state["error"] = f"生成 SQL 时出错: {str(e)}"
    
    return state


def execute_sql(state: AgentState) -> AgentState:
    """
    Node: 执行 SQL 语句
    """
    if state.get("error"):
        return state
    
    if not state.get("sql"):
        state["error"] = "没有可执行的 SQL 语句"
        return state
    
    try:
        result = execute_business_sql(state["sql"])
        state["result"] = result
        
        if not result:
            state["error"] = "查询结果为空"
        
    except Exception as e:
        state["sql_error"] = str(e)
        state["error"] = f"SQL 执行失败: {str(e)}"
    
    return state


def explain_result(state: AgentState) -> AgentState:
    """
    Node: 解释查询结果
    """
    if state.get("error") and not state.get("result"):
        return state
    
    if not state.get("result"):
        state["explanation"] = "查询结果为空"
        return state
    
    try:
        messages = build_explanation_prompt(state["sql"], state["result"])
        client = get_qwen_client()
        
        response = ""
        for chunk in client.chat(messages, stream=False, temperature=0.3):
            response += chunk
        
        state["explanation"] = response.strip()
        
    except Exception as e:
        state["explanation"] = f"无法生成解释: {str(e)}"
    
    return state


def recommend_chart(state: AgentState) -> AgentState:
    """
    Node: 推荐图表类型
    """
    if state.get("error") and not state.get("result"):
        state["chart_type"] = "table"
        return state
    
    if not state.get("result"):
        state["chart_type"] = "table"
        return state
    
    try:
        messages = build_chart_recommendation_prompt(state["sql"], state["result"])
        client = get_qwen_client()
        
        response = ""
        for chunk in client.chat(messages, stream=False, temperature=0.3):
            response += chunk
        
        # 提取图表类型
        response_lower = response.lower().strip()
        
        if "bar" in response_lower:
            state["chart_type"] = "bar"
        elif "line" in response_lower:
            state["chart_type"] = "line"
        elif "pie" in response_lower:
            state["chart_type"] = "pie"
        else:
            state["chart_type"] = "table"
        
    except Exception:
        state["chart_type"] = "table"
    
    return state
