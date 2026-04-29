"""
LangGraph Agent 主模块
"""
import json
from typing import Iterator, AsyncIterator
from typing import TypedDict

from app.agents.nodes import AgentState, generate_sql, execute_sql, explain_result, recommend_chart
from app.agents.edges import route_next, route_after_execute, route_after_explain, handle_error


class AgentResult(TypedDict):
    """Agent 最终结果"""
    sql: str | None
    result: list | None
    explanation: str | None
    chart_type: str
    error: str | None


def create_agent_graph():
    """
    创建 LangGraph 工作流图（简化版，不依赖 langgraph 库）
    
    工作流:
    generate_sql -> route_next -> execute_sql -> route_after_execute -> explain_result -> route_after_explain -> recommend_chart -> END
                                       |
                                       v
                                  handle_error -> END
    """
    # 这里使用简化的状态机实现
    # 完整实现可参考 LangGraph 文档
    pass


def run_agent(query: str, schema: str) -> AgentResult:
    """
    运行 Agent（同步版本）
    
    Args:
        query: 用户自然语言查询
        schema: 数据库 schema 描述
        
    Returns:
        AgentResult: 包含 sql, result, explanation, chart_type, error
    """
    # 初始化状态
    state: AgentState = {
        "query": query,
        "schema": schema,
        "sql": None,
        "sql_error": None,
        "result": None,
        "explanation": None,
        "chart_type": "table",
        "messages": [],
        "error": None,
    }
    
    # Step 1: 生成 SQL
    state = generate_sql(state)
    
    if state.get("error"):
        return AgentResult(
            sql=state.get("sql"),
            result=None,
            explanation=state.get("error"),
            chart_type="table",
            error=state.get("error"),
        )
    
    # Step 2: 执行 SQL
    state = execute_sql(state)
    
    if state.get("error"):
        return AgentResult(
            sql=state.get("sql"),
            result=None,
            explanation=state.get("error"),
            chart_type="table",
            error=state.get("error"),
        )
    
    # Step 3: 解释结果
    state = explain_result(state)
    
    # Step 4: 推荐图表
    state = recommend_chart(state)
    
    return AgentResult(
        sql=state.get("sql"),
        result=state.get("result"),
        explanation=state.get("explanation"),
        chart_type=state.get("chart_type", "table"),
        error=None,
    )


async def run_agent_stream(query: str, schema: str) -> AsyncIterator[dict]:
    """
    运行 Agent（异步流式版本）
    
    Yields:
        dict: 包含不同阶段的数据
        - {"type": "sql", "content": "..."}
        - {"type": "result", "content": [...]}
        - {"type": "explanation", "content": "..."}
        - {"type": "chart", "content": "..."}
        - {"type": "error", "content": "..."}
    """
    from app.core.llm import get_qwen_client
    from app.core.prompts import build_nl2sql_prompt, build_explanation_prompt, build_chart_recommendation_prompt
    from app.core.safety import extract_sql_from_response, sanitize_sql, validate_sql
    
    client = get_qwen_client()
    
    # Step 1: 生成 SQL
    try:
        messages = build_nl2sql_prompt(query, schema)
        sql_response = ""
        
        async for chunk in client.chat(messages, stream=True, temperature=0.3):
            sql_response += chunk
            yield {"type": "sql_partial", "content": chunk}
        
        # 提取并校验 SQL
        sql = extract_sql_from_response(sql_response)
        
        if not sql:
            yield {"type": "error", "content": "无法生成 SQL 语句"}
            return
        
        sql = sanitize_sql(sql)
        is_safe, error_msg = validate_sql(sql)
        
        if not is_safe:
            yield {"type": "error", "content": f"SQL 校验失败: {error_msg}"}
            return
        
        yield {"type": "sql", "content": sql}
        
    except Exception as e:
        yield {"type": "error", "content": f"生成 SQL 出错: {str(e)}"}
        return
    
    # Step 2: 执行 SQL
    try:
        result = execute_business_sql(sql)
        yield {"type": "result", "content": result}
    except Exception as e:
        yield {"type": "error", "content": f"SQL 执行失败: {str(e)}"}
        return
    
    # Step 3: 生成解释
    try:
        if result:
            explanation_messages = build_explanation_prompt(sql, result)
            explanation = ""
            
            async for chunk in client.chat(explanation_messages, stream=True, temperature=0.3):
                explanation += chunk
                yield {"type": "explanation_partial", "content": chunk}
            
            yield {"type": "explanation", "content": explanation}
        else:
            yield {"type": "explanation", "content": "查询结果为空"}
    except Exception as e:
        yield {"type": "explanation", "content": f"生成解释出错: {str(e)}"}
    
    # Step 4: 推荐图表
    try:
        if result:
            chart_messages = build_chart_recommendation_prompt(sql, result)
            chart_response = ""
            
            for chunk in client.chat(chart_messages, stream=False, temperature=0.3):
                chart_response += chunk
            
            # 提取图表类型
            chart_lower = chart_response.lower().strip()
            
            if "bar" in chart_lower:
                chart_type = "bar"
            elif "line" in chart_lower:
                chart_type = "line"
            elif "pie" in chart_lower:
                chart_type = "pie"
            else:
                chart_type = "table"
        else:
            chart_type = "table"
        
        yield {"type": "chart", "content": chart_type}
        
    except Exception:
        yield {"type": "chart", "content": "table"}
