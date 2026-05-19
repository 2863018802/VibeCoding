"""
LangChain Agents with Qwen3
===========================
Build tool-calling agents powered by Qwen3 through LangChain's
`create_agent` API. This file demonstrates three variants:

  1. ChatQwen  (DashScope API)
  2. ChatOllama (local)
  3. ChatOpenRouter (routing)

Usage:
    python qwen3_agent_example.py [1|2|3]
"""

import os
import sys
import asyncio
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_qwq import ChatQwen

# ---------------------------------------------------------------------------
# 0. Env bootstrap
# ---------------------------------------------------------------------------

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ---------------------------------------------------------------------------
# 1. Tool definitions
# ---------------------------------------------------------------------------

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city.

    Args:
        city: Name of the city, e.g. 'Beijing', 'Shanghai'.
    Returns:
        A short weather description.
    """
    # Replace this with a real weather API in production.
    return f"The weather in {city} is sunny, 24°C."


@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression.

    Args:
        expression: A simple math expression, e.g. '2 + 2 * 3'.
    Returns:
        The result as a string.
    """
    try:
        result = eval(expression)  # safe for arithmetic only
        return str(result)
    except Exception as e:
        return f"Error: {e}"


@tool
def search_wikipedia(query: str) -> str:
    """Search Wikipedia and return a short summary.

    Args:
        query: The search query.
    Returns:
        A brief summary from Wikipedia.
    """
    # Replace with real Wikipedia API in production.
    summaries = {
        "langchain": (
            "LangChain is an open-source framework for developing "
            "applications powered by large language models (LLMs)."
        ),
        "qwen": (
            "Qwen is a series of large language models developed by "
            "Alibaba Cloud, covering sizes from 0.5B to 72B parameters."
        ),
    }
    key = query.lower().split()[0] if query else ""
    return summaries.get(key, f"No Wikipedia entry found for: {query}")


# ---------------------------------------------------------------------------
# 2. Agent factories
# ---------------------------------------------------------------------------

def build_agent_dashscope(model_name: str = "qwen3-235b-a22b-instruct-2507"):
    """Build an agent using ChatQwen (DashScope)."""
    print(f"[DashScope] Building agent with model: {model_name}")

    model = ChatQwen(model=model_name, temperature=0.7, max_tokens=1024)

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are a helpful research assistant. "
            "Use the provided tools to answer the user's question. "
            "Be concise and accurate."
        )),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_agent(
        model,
        tools=[get_weather, calculator, search_wikipedia],
        prompt=prompt,
    )
    return agent


def build_agent_ollama(model_name: str = "qwen3:32b"):
    """Build an agent using ChatOllama (local)."""
    print(f"[Ollama] Building agent with model: {model_name}")

    from langchain_ollama import ChatOllama

    model = ChatOllama(
        model=model_name,
        base_url="http://localhost:11434",
        temperature=0.7,
        num_ctx=8192,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Use tools to answer the user's question."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_agent(
        model,
        tools=[get_weather, calculator, search_wikipedia],
        prompt=prompt,
    )
    return agent


def build_agent_openrouter(model_name: str = "qwen/qwen3-397b-a22b"):
    """Build an agent using ChatOpenRouter."""
    print(f"[OpenRouter] Building agent with model: {model_name}")

    from langchain_openrouter import ChatOpenRouter

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    model = ChatOpenRouter(
        model=model_name,
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.7,
        max_tokens=1024,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Use tools to answer the user's question."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_agent(
        model,
        tools=[get_weather, calculator, search_wikipedia],
        prompt=prompt,
    )
    return agent


# ---------------------------------------------------------------------------
# 3. Run helpers
# ---------------------------------------------------------------------------

def run_agent(agent, question: str) -> None:
    """Synchronously invoke an agent with a single question."""
    print(f"\n{'─' * 60}")
    print(f"  Q: {question}")
    print(f"{'─' * 60}")

    result = agent.invoke({"messages": [("human", question)]})

    # Extract the last assistant message
    messages = result.get("messages", [])
    last = messages[-1] if messages else None
    answer = getattr(last, "content", str(result)) if last else str(result)

    print(f"\n  A: {answer}\n")


async def run_agent_async(agent, question: str) -> None:
    """Asynchronously invoke an agent."""
    print(f"\n{'─' * 60}")
    print(f"  Q (async): {question}")
    print(f"{'─' * 60}")

    result = await agent.ainvoke({"messages": [("human", question)]})

    messages = result.get("messages", [])
    last = messages[-1] if messages else None
    answer = getattr(last, "content", str(result)) if last else str(result)

    print(f"\n  A: {answer}\n")


# ---------------------------------------------------------------------------
# 4. Demos
# ---------------------------------------------------------------------------

def demo_dashscope():
    print("\n" + "=" * 70)
    print("  DEMO 1 — LangChain Agent powered by ChatQwen (DashScope)")
    print("=" * 70)

    agent = build_agent_dashscope()

    run_agent(agent, "What is the weather in Beijing?")
    run_agent(agent, "Calculate (15 + 7) * 3 - 10.")
    run_agent(agent, "Tell me about LangChain in one sentence.")

    # Async demo
    asyncio.run(run_agent_async(agent, "What is the weather in Shanghai?"))


def demo_ollama():
    print("\n" + "=" * 70)
    print("  DEMO 2 — LangChain Agent powered by ChatOllama (local)")
    print("=" * 70)

    agent = build_agent_ollama()

    run_agent(agent, "What is the weather in Tokyo?")
    run_agent(agent, "Calculate 100 / 4 + 25.")
    run_agent(agent, "What is Qwen?")


def demo_openrouter():
    print("\n" + "=" * 70)
    print("  DEMO 3 — LangChain Agent via OpenRouter (Qwen3-397B)")
    print("=" * 70)

    agent = build_agent_openrouter()

    run_agent(agent, "What is the weather in Paris?")
    run_agent(agent, "Calculate 50 * 2 + 100 / 5.")


# ---------------------------------------------------------------------------
# 5. Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    demos = {
        "1": (demo_dashscope,  "ChatQwen  (DashScope API — recommended)"),
        "2": (demo_ollama,     "ChatOllama (local Ollama)"),
        "3": (demo_openrouter, "ChatOpenRouter"),
        "all": None,
    }

    print("""
╔══════════════════════════════════════════════════════════════╗
║   LangChain Agents with Qwen3  ·  agent demo runner         ║
╠══════════════════════════════════════════════════════════════╣
║  python qwen3_agent_example.py 1    ← ChatQwen (DashScope)  ║
║  python qwen3_agent_example.py 2    ← ChatOllama (local)     ║
║  python qwen3_agent_example.py 3    ← OpenRouter            ║
║  python qwen3_agent_example.py all  ← All demos             ║
╚══════════════════════════════════════════════════════════════╝
""")

    choice = sys.argv[1].lower() if len(sys.argv) > 1 else "1"

    if choice == "all":
        for name, fn in [("DashScope", demo_dashscope),
                          ("Ollama", demo_ollama),
                          ("OpenRouter", demo_openrouter)]:
            try:
                fn()
            except Exception as e:
                print(f"[ERROR in {name}] {e}\n[Skipping to next demo]\n")

    elif choice in demos and demos[choice]:
        fn, desc = demos[choice]
        print(f">> Running: {desc}\n")
        fn()

    else:
        print(f"Unknown choice: {choice!r}")
        print("Valid: 1, 2, 3, all")
        sys.exit(1)

    print("\n✔ Done.")
