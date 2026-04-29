# AIData Backend

智能数据分析系统后端，基于 FastAPI + LangChain + Qwen3-32B。

## 环境要求

- Python 3.10+
- [阿里云百炼 DashScope API Key](https://dashscope.console.aliyun.com/)

## 快速启动

### Windows

双击运行 `setup.bat`，或手动执行：

```bash
cd backend
python -m pip install -r requirements.txt
python scripts\init_db.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### macOS / Linux

```bash
cd backend
python3 -m pip install -r requirements.txt
python3 scripts/init_db.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 配置

复制 `.env.template` 为 `.env`，填入以下变量：

```env
DASHSCOPE_API_KEY=your_api_key_here
```

## API 文档

启动后访问：http://localhost:8000/docs

## 数据库

- `data/metadata.db` - 元数据库（会话、消息）
- `data/business.db` - 业务数据库（产品、订单、客户）

## 目录结构

```
backend/
├── app/
│   ├── main.py          # FastAPI 入口
│   ├── config/           # 配置管理
│   ├── models/           # SQLAlchemy 模型
│   ├── routers/         # API 路由
│   └── services/        # 业务逻辑
├── scripts/
│   └── init_db.py       # 业务数据库初始化
├── .env                  # 环境变量（请勿提交）
├── requirements.txt
└── setup.bat            # Windows 快速安装脚本
```
