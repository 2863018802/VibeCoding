"""
SQL 安全校验模块
防止 SQL 注入，只允许 SELECT 语句
"""

import re
from typing import Tuple


class SQLSafetyError(Exception):
    """SQL 安全校验异常"""
    pass


# 禁止的 SQL 关键字（不区分大小写）
FORBIDDEN_KEYWORDS = [
    "INSERT",
    "UPDATE", 
    "DELETE",
    "DROP",
    "TRUNCATE",
    "ALTER",
    "CREATE",
    "GRANT",
    "REVOKE",
    "EXEC",
    "EXECUTE",
    "UNION",
    "INTO",
    "--",      # SQL 注释
    ";",       # 多语句分隔
    "/*",      # 块注释开始
    "*/",      # 块注释结束
]


def validate_sql(sql: str) -> Tuple[bool, str]:
    """
    校验 SQL 语句是否安全
    
    Args:
        sql: 待校验的 SQL 语句
        
    Returns:
        (is_safe, error_message)
    """
    if not sql or not sql.strip():
        return False, "SQL 语句为空"
    
    sql_upper = sql.upper()
    
    # 检查是否以 SELECT 开头（允许 WITH ... SELECT  CTE）
    sql_stripped = sql_upper.strip()
    if not (sql_stripped.startswith("SELECT") or sql_stripped.startswith("WITH")):
        return False, "只允许 SELECT 语句"
    
    # 检查禁止关键字
    for keyword in FORBIDDEN_KEYWORDS:
        # 避免误判 INTO 作为表名的一部分（如 someinto 列名）
        pattern = rf"\b{keyword}\b"
        if re.search(pattern, sql_upper):
            return False, f"禁止使用关键字: {keyword}"
    
    # 检查危险函数
    dangerous_functions = ["load_extension", "sqlite_compileoption_get", "sqlite_compileoption_set"]
    sql_lower = sql.lower()
    for func in dangerous_functions:
        if func.lower() in sql_lower:
            return False, f"禁止使用函数: {func}"
    
    return True, ""


def sanitize_sql(sql: str) -> str:
    """
    清理和规范化 SQL 语句
    """
    # 移除首尾空白
    sql = sql.strip()
    
    # 移除末尾的分号（如果有）
    if sql.endswith(";"):
        sql = sql[:-1]
    
    return sql


def extract_sql_from_response(response: str) -> str | None:
    """
    从 LLM 响应中提取 SQL 语句
    支持多种格式:
    - 纯 SQL
    - ```sql ... ```
    - SELECT ... (无标记)
    """
    if not response:
        return None
    
    # 尝试提取 ```sql ... ``` 块
    sql_block_pattern = r"```sql\s*(.*?)\s*```"
    match = re.search(sql_block_pattern, response, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # 尝试提取 ``` ... ``` 块（无语言标记）
    generic_block_pattern = r"```\s*(.*?)\s*```"
    match = re.search(generic_block_pattern, response, re.DOTALL)
    if match:
        potential_sql = match.group(1).strip()
        if potential_sql.upper().startswith("SELECT") or potential_sql.upper().startswith("WITH"):
            return potential_sql
    
    # 尝试直接提取 SELECT 语句
    select_pattern = r"(WITH\s+.*?|SELECT\s+.*?)(?:\s*;?\s*$|$)"
    match = re.search(select_pattern, response, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # 如果整个响应就是 SQL
    response_stripped = response.strip()
    if response_stripped.upper().startswith("SELECT") or response_stripped.upper().startswith("WITH"):
        return response_stripped
    
    return None
