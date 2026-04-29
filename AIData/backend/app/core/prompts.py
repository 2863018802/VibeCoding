"""
NL2SQL 提示词模板
"""

# 关闭思考模式的标准提示词（用于 NL2SQL）
SYSTEM_PROMPT = """你是一个专业的 SQL 专家，擅长将自然语言转换为准确的 SQL 查询。

数据库信息:
{schema}

重要规则:
1. 只生成 SELECT 语句，禁止 INSERT、UPDATE、DELETE、DROP、TRUNCATE 等操作
2. 使用 SQLite 语法
3. 字段名、表名必须与数据库 schema 一致
4. 如果无法回答用户的问题，直接说明原因，不要生成 SQL

输出格式:
请只返回 SQL 查询语句，不要有其他解释。如果无法回答，请说明原因。"""

# Few-shot 示例
FEW_SHOT_EXAMPLES = """

示例 1:
用户: 查找所有订单
SQL: SELECT * FROM orders

示例 2:
用户: 查看2024年1月的销售额
SQL: SELECT SUM(total_amount) as sales FROM orders WHERE order_date >= '2024-01-01' AND order_date < '2024-02-01'

示例 3:
用户: 统计每个地区的订单数量
SQL: SELECT customer_region, COUNT(*) as order_count FROM orders GROUP BY customer_region

示例 4:
用户: 查看最贵的5个产品
SQL: SELECT * FROM products ORDER BY price DESC LIMIT 5
"""

# 结果解释提示词
EXPLANATION_PROMPT = """基于以下 SQL 查询结果，用自然语言解释给用户：

SQL: {sql}
结果: {result}

请给出简洁明了的解释，包括:
1. 查询到的关键数据
2. 数据的含义
3. 任何有趣的发现

如果结果为空，说明查询没有返回任何数据。"""

# 图表推荐提示词
CHART_RECOMMENDATION_PROMPT = """基于以下查询结果，推荐最合适的图表类型：

SQL: {sql}
结果: {result}

图表类型选项:
- bar: 柱状图，适合比较不同类别的数值
- line: 折线图，适合展示趋势变化
- pie: 饼图，适合展示占比关系
- table: 表格，适合展示详细数据

请根据数据特征推荐最合适的图表类型，只返回一个选项（bar/line/pie/table）。
如果数据不适合可视化，请返回 "table"。"""


def build_nl2sql_prompt(user_query: str, schema: str) -> list[dict]:
    """构建 NL2SQL 的完整提示词"""
    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT.format(schema=schema) + FEW_SHOT_EXAMPLES,
        },
        {
            "role": "user",
            "content": user_query,
        },
    ]


def build_explanation_prompt(sql: str, result: list) -> list[dict]:
    """构建结果解释的提示词"""
    result_str = "\n".join([str(row) for row in result[:10]])
    if len(result) > 10:
        result_str += f"\n... 共 {len(result)} 条记录"
    
    return [
        {
            "role": "system",
            "content": "你是一个数据分析助手，负责解释 SQL 查询结果。",
        },
        {
            "role": "user",
            "content": EXPLANATION_PROMPT.format(sql=sql, result=result_str),
        },
    ]


def build_chart_recommendation_prompt(sql: str, result: list) -> list[dict]:
    """构建图表推荐的提示词"""
    result_str = "\n".join([str(row) for row in result[:20]])
    
    return [
        {
            "role": "user",
            "content": CHART_RECOMMENDATION_PROMPT.format(sql=sql, result=result_str),
        },
    ]
