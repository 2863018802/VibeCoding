"""
直接执行 SQL 接口（调试用）
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.models import get_business_db
from app.core.safety import validate_sql, sanitize_sql

router = APIRouter()


class SQLExecuteRequest(BaseModel):
    sql: str
    params: Optional[dict] = None


class SQLExecuteResponse(BaseModel):
    success: bool
    sql: str
    columns: list[str]
    rows: list[dict]
    count: int
    error: Optional[str] = None


@router.post("/query/execute", response_model=SQLExecuteResponse)
async def execute_sql(
    request: SQLExecuteRequest,
    db: Session = Depends(get_business_db),
):
    """
    直接执行 SQL 查询（调试用）
    
    注意：此接口仅用于调试，生产环境应使用流式对话接口
    
    Args:
        request: 包含 SQL 语句的请求
        
    Returns:
        查询结果
    """
    # 清理和校验 SQL
    sql = sanitize_sql(request.sql)
    
    is_safe, error_msg = validate_sql(sql)
    if not is_safe:
        return SQLExecuteResponse(
            success=False,
            sql=sql,
            columns=[],
            rows=[],
            count=0,
            error=f"SQL 校验失败: {error_msg}",
        )
    
    try:
        from sqlalchemy import text
        result = db.execute(text(sql))
        columns = list(result.keys())
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
        
        return SQLExecuteResponse(
            success=True,
            sql=sql,
            columns=columns,
            rows=rows,
            count=len(rows),
        )
        
    except Exception as e:
        return SQLExecuteResponse(
            success=False,
            sql=sql,
            columns=[],
            rows=[],
            count=0,
            error=str(e),
        )


@router.get("/query/preview")
async def preview_table(
    table: str,
    limit: int = 10,
    db: Session = Depends(get_business_db),
):
    """
    预览表数据（快捷查询）
    
    Args:
        table: 表名
        limit: 返回行数限制
        
    Returns:
        表数据预览
    """
    # 校验表名（只允许字母数字下划线）
    import re
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table):
        raise HTTPException(status_code=400, detail="无效的表名")
    
    # 限制行数
    limit = min(limit, 100)
    
    sql = f"SELECT * FROM {table} LIMIT {limit}"
    
    try:
        from sqlalchemy import text
        result = db.execute(text(sql))
        columns = list(result.keys())
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
        
        # 获取表结构
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        table_columns = inspector.get_columns(table)
        
        return {
            "success": True,
            "table": table,
            "columns": columns,
            "column_types": {col["name"]: str(col["type"]) for col in table_columns},
            "rows": rows,
            "count": len(rows),
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/query/tables")
async def list_tables(db: Session = Depends(get_business_db)):
    """
    列出所有表
    
    Returns:
        表列表
    """
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        
        # 获取每个表的行数
        table_info = []
        for table in tables:
            try:
                result = db.execute(text(f"SELECT COUNT(*) as cnt FROM {table}"))
                count = result.scalar()
                table_info.append({
                    "name": table,
                    "row_count": count,
                })
            except Exception:
                table_info.append({
                    "name": table,
                    "row_count": None,
                })
        
        return {
            "success": True,
            "tables": table_info,
            "count": len(table_info),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from sqlalchemy import text
