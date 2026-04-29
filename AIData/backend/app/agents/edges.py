"""
LangGraph Agent Edges 定义
"""
from typing import Literal

from app.agents.nodes import AgentState


def route_next(state: AgentState) -> Literal["execute_sql", "handle_error", "__end__"]:
    """
    路由决策：决定下一步走哪个节点
    """
    # 如果有错误，跳转到错误处理
    if state.get("error"):
        return "handle_error"
    
    # 如果成功生成了 SQL，继续执行
    if state.get("sql"):
        return "execute_sql"
    
    # 默认结束
    return "__end__"


def route_after_execute(state: AgentState) -> Literal["explain_result", "handle_error", "__end__"]:
    """
    SQL 执行后的路由决策
    """
    if state.get("error") or state.get("sql_error"):
        return "handle_error"
    
    if state.get("result") is not None:
        return "explain_result"
    
    return "__end__"


def route_after_explain(state: AgentState) -> Literal["recommend_chart", "__end__"]:
    """
    解释完成后的路由决策
    """
    if state.get("explanation"):
        return "recommend_chart"
    return "__end__"


def handle_error(state: AgentState) -> AgentState:
    """
    错误处理节点
    """
    # 错误已经设置在 state 中，这里可以添加额外的错误处理逻辑
    return state
