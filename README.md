# LangChain Qwen3 Integration Examples

> Connect Qwen3 (and all Qwen series models) to LangChain in Python — via Alibaba Cloud DashScope API, local Ollama, or OpenRouter.

## What's in here

| File | Description |
|---|---|
| `requirements.txt` | Python dependencies |
| `qwen3_example.py` | Standalone usage demos (DashScope + Ollama + OpenRouter) |
| `qwen3_agent_example.py` | Tool-calling agent built on `create_agent` |
| `qwen3_local_ollama.py` | Local Qwen3 with Ollama (no API key needed) |
| `config_template.env` | Environment variable template |

## Installation

```bash
# 1. Create & activate a virtual environment
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate      # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt
```

## Quick Start

### 1. Set your API key

**Option A — Alibaba Cloud DashScope (recommended for Qwen3):**

Sign up at [Alibaba Cloud BaiLian](https://bailian.console.aliyuncs.com), get an API key, then:

```bash
# Windows
set DASHSCOPE_API_KEY=sk-your-key-here

# macOS / Linux
export DASHSCOPE_API_KEY=sk-your-key-here
```

Or edit `config_template.env` and rename it to `.env`.

**Option B — Local Ollama (no API key):**

```bash
ollama pull qwen3:32b
```

**Option C — OpenRouter (any Qwen3 variant):**

```bash
set OPENAI_API_KEY=sk-or-v1-your-key-here
set OPENAI_API_BASE=https://openrouter.ai/api/v1
```

### 2. Run examples

```bash
# Basic chat + tool calling
python qwen3_example.py

# Agent with tool calling
python qwen3_agent_example.py

# Local Ollama
python qwen3_local_ollama.py
```

## Model Guide

| Model | Provider | Best For | API Key Needed? |
|---|---|---|---|
| Qwen3-235B-A22B (instruct) | DashScope | Full power, hosted | Yes |
| Qwen3-235B-A22B (thinking) | DashScope | Qwen3 with reasoning | Yes |
| Qwen3-32B / 8B | Ollama | Local, private | No |
| Qwen3-397B-A22B | OpenRouter | Fast routing, many variants | Yes |
| Qwen2.5-Max | DashScope | Production, stable | Yes |
| Qwen-VL-Max | DashScope | Vision / image understanding | Yes |

## DashScope Models

| Model | Type | Thinking | Tool Calling | Vision |
|---|---|---|---|---|
| `qwen3-235b-a22b-instruct-2507` | Chat | ❌ | ✅ | ❌ |
| `qwen3-235b-a22b-thinking-2507` | Chat + Reason | ✅ | ✅ | ❌ |
| `qwq-plus` | Reasoner | ✅ | ✅ | ❌ |
| `qvq-max` | Reasoner + Vision | ✅ | ✅ | ✅ |
| `qwen-plus-latest` | Chat | ✅ (opt-in) | ✅ | ❌ |
| `qwen-max-latest` | Chat | ❌ | ✅ | ❌ |
| `qwen-vl-max-latest` | Vision | ❌ | ✅ | ✅ |
| `qwen2.5-72b-instruct` | Chat | ❌ | ✅ | ❌ |

> **Thinking Control (Qwen3 only):** `enable_thinking=True/False` and `thinking_budget=N` tokens.

## Architecture

```
qwen3_example.py
├── ChatQwen (langchain-qwq)      ← Alibaba Cloud DashScope API
│   ├── Qwen3, QwQ, QvQ, Qwen2.5, Qwen-VL
│   └── Tool calling, vision, streaming, structured output
│
├── ChatOllama (langchain-ollama) ← Local Ollama
│   └── Qwen3-32B/8B, no API key needed
│
└── ChatOpenRouter (langchain-openrouter) ← OpenRouter routing
    └── qwen3-397B-A22B, fast routing
```

## Troubleshooting

**"Module not found" errors**
```bash
pip install -r requirements.txt
```

**Ollama connection refused**
```bash
ollama serve   # in a separate terminal
```

**DashScope auth error**
Make sure `DASHSCOPE_API_KEY` is set. Chinese users should also set:
```bash
set DASHSCOPE_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
```

**OpenRouter rate limits**
Switch to DashScope for production use.
