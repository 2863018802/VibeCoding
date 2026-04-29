"""
数据库 Schema 查询 API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import inspect

from app.models import get_business_db

router = APIRouter()


@router.get("/schema")
def get_schema(db: Session = Depends(get_business_db)):
    """
    获取数据库 schema 信息
    
    Returns:
        {
            "tables": [
                {
                    "name": "表名",
                    "columns": [
                        {"name": "列名", "type": "类型", "nullable": bool, "primary_key": bool}
                    ]
                }
            ]
        }
    """
    try:
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        
        result = []
        
        for table_name in tables:
            columns = inspector.get_columns(table_name)
            pk_columns = inspector.get_pk_constraint(table_name)
            pk_names = pk_columns.get("constrained_columns", []) if pk_columns else []
            
            col_list = []
            for col in columns:
                col_list.append({
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"],
                    "primary_key": col["name"] in pk_names,
                    "default": str(col.get("default", "")),
                })
            
            # 获取外键信息
            fk_list = []
            try:
                fk_constraints = inspector.get_foreign_keys(table_name)
                for fk in fk_constraints:
                    fk_list.append({
                        "column": fk["constrained_columns"],
                        "referred_table": fk["referred_table"],
                        "referred_columns": fk["referred_columns"],
                    })
            except Exception:
                pass
            
            result.append({
                "name": table_name,
                "columns": col_list,
                "foreign_keys": fk_list,
            })
        
        return {
            "tables": result,
            "count": len(result),
        }
        
    except Exception as e:
        return {
            "tables": [],
            "count": 0,
            "error": str(e),
        }


@router.get("/schema/table/{table_name}")
def get_table_schema(table_name: str, db: Session = Depends(get_business_db)):
    """
    获取指定表的 schema
    
    Args:
        table_name: 表名
        
    Returns:
        表的详细信息
    """
    try:
        inspector = inspect(db.bind)
        
        # 检查表是否存在
        tables = inspector.get_table_names()
        if table_name not in tables:
            return {"error": f"表 {table_name} 不存在"}
        
        # 获取列信息
        columns = inspector.get_columns(table_name)
        pk_constraint = inspector.get_pk_constraint(table_name)
        pk_names = pk_constraint.get("constrained_columns", []) if pk_constraint else []
        
        # 获取外键
        foreign_keys = inspector.get_foreign_keys(table_name)
        
        # 获取索引
        indexes = inspector.get_indexes(table_name)
        
        return {
            "name": table_name,
            "columns": [
                {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"],
                    "primary_key": col["name"] in pk_names,
                    "default": str(col.get("default", "")),
                }
                for col in columns
            ],
            "foreign_keys": foreign_keys,
            "indexes": indexes,
        }
        
    except Exception as e:
        return {"error": str(e)}


@router.get("/schema/sql")
def execute_raw_sql(sql: str, db: Session = Depends(get_business_db)):
    """
    执行原始 SQL 查询（仅 SELECT，仅调试用）
    
    Args:
        sql: SQL 语句
        
    Returns:
        查询结果
    """
    from app.core.safety import validate_sql
    
    # 校验 SQL
    is_safe, error_msg = validate_sql(sql)
    if not is_safe:
        return {"error": error_msg, "success": False}
    
    try:
        from sqlalchemy import text
        result = db.execute(text(sql))
        columns = result.keys()
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
        
        return {
            "success": True,
            "columns": list(columns),
            "rows": rows,
            "count": len(rows),
        }
        
    except Exception as e:
        return {"error": str(e), "success": False}
