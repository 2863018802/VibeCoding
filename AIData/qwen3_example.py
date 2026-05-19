"""
LangChain + Qwen3 Integration Examples
======================================
Three ways to connect Qwen3 to LangChain:

  1. ChatQwen   →  Alibaba Cloud DashScope API  (recommended: full Qwen3 power)
  2. ChatOllama →  Local Ollama                 (free, private, runs on your machine)
  3. ChatOpenRouter → OpenRouter routing        (alternative hosted endpoint)

Run each section independently by commenting out the others.
"""

import os
import sys
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_qwq import ChatQwen, ChatQwQ
from langchain_ollama import ChatOllama
from langchain_openrouter import ChatOpenRouter

# ---------------------------------------------------------------------------
# 0. Environment setup
# ---------------------------------------------------------------------------

def _load_env():
    """Load .env file if present (no-op in CI / prod)."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

_load_env()

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def print_msg(label: str, msg) -> None:
    content = getattr(msg, "content", str(msg))
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    print(content)
    if hasattr(msg, "usage_metadata") and msg.usage_metadata:
        print(f"\n[Tokens] {msg.usage_metadata}")
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        print(f"[Tool calls] {msg.tool_calls}")


# ===========================================================================
# PART 1 — ChatQwen via Alibaba Cloud DashScope
#    Package : langchain-qwq
#    Models  : qwen3-235b, qwq-plus, qwen2.5-max, qwen-vl-max, …
#    Docs    : https://docs.langchain.com/oss/python/integrations/chat/qwen
# ===========================================================================

def demo_chat_qwen():
    print("\n" + "=" * 70)
    print("  PART 1 · ChatQwen (DashScope API)")
    print("=" * 70)

    # ------------------------------------------------------------------
    # 1a. Basic chat — Qwen3 instruct
    # ------------------------------------------------------------------
    print("\n--- 1a. Basic chat (qwen3-235b-a22b-instruct) ---")

    qwen = ChatQwen(
        model="qwen3-235b-a22b-instruct-2507",
        temperature=0.7,
        max_tokens=512,
    )

    messages = [
        SystemMessage(content="You are a helpful assistant that answers in Chinese."),
        HumanMessage(content="Hello, who are you?"),
    ]
    response = qwen.invoke(messages)
    print_msg("1a Response", response)

    # ------------------------------------------------------------------
    # 1b. Tool calling — bind a Python function as a tool
    # ------------------------------------------------------------------
    print("\n--- 1b. Tool calling (bind_tools) ---")

    @tool
    def get_weather(city: str) -> str:
        """Get the current weather for a city.

        Args:
            city: Name of the city (e.g. 'Beijing', 'Shanghai').
        """
        return f"The weather in {city} is sunny, 22°C."

    @tool
    def calculator(expression: str) -> str:
        """Evaluate a simple math expression.

        Args:
            expression: A mathematical expression, e.g. '2 + 2 * 3'.
        """
        try:
            result = eval(expression)  # safe for simple arithmetic only
            return str(result)
        except Exception as e:
            return f"Error: {e}"

    qwen_with_tools = qwen.bind_tools([get_weather, calculator])

    tool_response = qwen_with_tools.invoke(
        "What's the weather in Beijing? Also calculate 15 * 4 + 7."
    )
    print_msg("1b Tool-call response", tool_response)

    # ------------------------------------------------------------------
    # 1c. Thinking / reasoning mode — Qwen3-235B thinking variant
    #     Only available on the DashScope platform.
    # ------------------------------------------------------------------
    print("\n--- 1c. Thinking mode (qwen3-235b-a22b-thinking) ---")

    thinking_model = ChatQwen(
        model="qwen3-235b-a22b-thinking-2507",
        enable_thinking=True,   # activate internal reasoning
        # thinking_budget=2048,  # cap reasoning tokens (optional)
        temperature=0.7,
        max_tokens=512,
    )

    thinking_response = thinking_model.invoke(
        "Why is the sky blue? Think step by step."
    )
    print_msg("1c Thinking response", thinking_response)

    # Access the reasoning trace separately
    reasoning = thinking_response.additional_kwargs.get("reasoning_content", "")
    final_answer = thinking_response.content
    print(f"\n[Reasoning trace]\n{reasoning}")
    print(f"\n[Final answer] {final_answer}")

    # ------------------------------------------------------------------
    # 1d. Streaming — token-level output
    # ------------------------------------------------------------------
    print("\n--- 1d. Streaming (sync) ---")

    stream_model = ChatQwen(model="qwen3-235b-a22b-instruct-2507", max_tokens=256)

    collected = []
    print("Streaming: ", end="", flush=True)
    for token in stream_model.stream("Tell me a short joke."):
        print(token.content, end="", flush=True)
        collected.append(token.content)
    print("\n")

    # ------------------------------------------------------------------
    # 1e. Async streaming
    # ------------------------------------------------------------------
    print("\n--- 1e. Streaming (async) ---")

    async def async_stream_demo():
        import asyncio
        async for token in stream_model.astream("Explain AI in one sentence."):
            print(token.content, end="", flush=True)
        print()

    asyncio.run(async_stream_demo())

    # ------------------------------------------------------------------
    # 1f. Structured output — JSON via Pydantic model
    # ------------------------------------------------------------------
    print("\n--- 1f. Structured output (Pydantic) ---")

    from pydantic import BaseModel, Field

    class CityInfo(BaseModel):
        city: str = Field(description="Name of the city")
        population: int = Field(description="Approximate population in millions")
        country: str = Field(description="Country the city belongs to")
        fun_fact: str = Field(description="One interesting fact about the city")

    struct_model = qwen.with_structured_output(CityInfo, method="json_mode")

    structured_response = struct_model.invoke(
        "Tell me about Tokyo in a structured format."
    )
    print(f"\n[Structured output — CityInfo]\n{structured_response}")

    # ------------------------------------------------------------------
    # 1g. Vision — image understanding with Qwen-VL
    # ------------------------------------------------------------------
    print("\n--- 1g. Vision (qwen-vl-max-latest) ---")

    from langchain_core.messages import HumanMessage

    vision_model = ChatQwen(model="qwen-vl-max-latest")

    vision_messages = [
        HumanMessage(content=[
            {
                "type": "image_url",
                "image_url": {
                    "url": "https://example.com/sample.jpg"
                },
            },
            {"type": "text", "text": "What do you see in this image?"},
        ])
    ]

    vision_response = vision_model.invoke(vision_messages)
    print_msg("1g Vision response", vision_response)

    # ------------------------------------------------------------------
    # 1h. QwQ — reasoning model with built-in chain-of-thought
    # ------------------------------------------------------------------
    print("\n--- 1h. QwQ reasoning model (qwq-plus) ---")

    qwq = ChatQwQ(model="qwq-plus", max_tokens=512)

    qwq_response = qwq.invoke(
        "If a train travels 120 km in 1.5 hours, what is its average speed?"
    )
    print_msg("1h QwQ response", qwq_response)

    # Access QwQ reasoning content
    qwq_reasoning = qwq_response.additional_kwargs.get("reasoning_content", "")
    print(f"\n[QwQ Reasoning trace]\n{qwq_reasoning}")

    # ------------------------------------------------------------------
    # 1i. Using init_chat_model factory (provider:model format)
    #     Same as ChatQwen but accessed through LangChain's unified API.
    # ------------------------------------------------------------------
    print("\n--- 1i. init_chat_model factory (DashScope provider) ---")

    from langchain.chat_models import init_chat_model

    # Provider string must match a langchain-<provider> package.
    # The langchain-qwq package registers itself as a provider.
    factory_model = init_chat_model(
        "qwen3-235b-a22b-instruct-2507",
        model_provider="qwen",   # uses langchain-qwq internally
        temperature=0.5,
        max_tokens=256,
    )

    factory_response = factory_model.invoke("What is 2+2?")
    print_msg("1i Factory model response", factory_response)


# ===========================================================================
# PART 2 — ChatOllama (local, no API key needed)
#    Package : langchain-ollama
#    Models  : qwen3:32b, qwen3:8b, qwen3:14b, …
#    Setup   : ollama pull qwen3:32b
# ===========================================================================

def demo_chat_ollama():
    print("\n" + "=" * 70)
    print("  PART 2 · ChatOllama (local Ollama — no API key)")
    print("=" * 70)

    # ------------------------------------------------------------------
    # 2a. Basic chat — local Qwen3
    # ------------------------------------------------------------------
    print("\n--- 2a. Basic chat (ollama:qwen3:32b) ---")

    ollama_model = ChatOllama(
        model="qwen3:32b",       # make sure you ran: ollama pull qwen3:32b
        base_url="http://localhost:11434",
        temperature=0.7,
        num_ctx=8192,            # context window
    )

    ollama_response = ollama_model.invoke(
        "Explain quantum entanglement in simple terms."
    )
    print_msg("2a Ollama response", ollama_response)

    # ------------------------------------------------------------------
    # 2b. Tool calling — local tool use
    # ------------------------------------------------------------------
    print("\n--- 2b. Tool calling (Ollama) ---")

    @tool
    def celsius_to_fahrenheit(celsius: float) -> str:
        """Convert Celsius temperature to Fahrenheit."""
        fahrenheit = celsius * 9 / 5 + 32
        return f"{celsius}°C = {fahrenheit:.1f}°F"

    ollama_with_tools = ollama_model.bind_tools([celsius_to_fahrenheit])

    ollama_tool_response = ollama_with_tools.invoke(
        "Convert 25 degrees Celsius to Fahrenheit."
    )
    print_msg("2b Ollama tool-call response", ollama_tool_response)

    # ------------------------------------------------------------------
    # 2c. Streaming
    # ------------------------------------------------------------------
    print("\n--- 2c. Streaming (Ollama) ---")

    print("Streaming: ", end="", flush=True)
    for token in ollama_model.stream("Tell me a short fact about space."):
        print(token.content, end="", flush=True)
    print()

    # ------------------------------------------------------------------
    # 2d. Async
    # ------------------------------------------------------------------
    print("\n--- 2d. Async (Ollama) ---")

    async def async_ollama():
        import asyncio
        result = await ollama_model.ainvoke("What is LangChain?")
        print_msg("2d Ollama async response", result)

    asyncio.run(async_ollama())

    # ------------------------------------------------------------------
    # 2e. init_chat_model factory (ollama provider)
    # ------------------------------------------------------------------
    print("\n--- 2e. init_chat_model factory (ollama provider) ---")

    from langchain.chat_models import init_chat_model

    ollama_factory = init_chat_model(
        "qwen3:32b",
        model_provider="ollama",
        temperature=0.5,
    )

    factory_resp = ollama_factory.invoke("What is 1+1?")
    print_msg("2e Factory model response", factory_resp)


# ===========================================================================
# PART 3 — ChatOpenRouter (routing layer, supports Qwen3-397B)
#    Package : langchain-openrouter
#    Models  : qwen/qwen3-397b-a22b, fireworks/qwen3p5-397b-a17b, …
#    Docs    : https://docs.langchain.com/oss/python/integrations/chat/openrouter
# ===========================================================================

def demo_chat_openrouter():
    print("\n" + "=" * 70)
    print("  PART 3 · ChatOpenRouter (Qwen3 via routing)")
    print("=" * 70)

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("\n[SKIPPED] Set OPENAI_API_KEY to run OpenRouter examples.")
        print("  Windows : set OPENAI_API_KEY=sk-or-v1-...")
        print("  Linux   : export OPENAI_API_KEY=sk-or-v1-...")
        return

    # ------------------------------------------------------------------
    # 3a. Basic chat — Qwen3-397B via OpenRouter
    # ------------------------------------------------------------------
    print("\n--- 3a. Basic chat (openrouter:qwen/qwen3-397b-a22b) ---")

    from langchain_openrouter import ChatOpenRouter

    openrouter_model = ChatOpenRouter(
        model="qwen/qwen3-397b-a22b",
        openai_api_key=openai_api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        max_tokens=512,
        temperature=0.7,
    )

    or_response = openrouter_model.invoke(
        "What are three key benefits of using LangChain?"
    )
    print_msg("3a OpenRouter response", or_response)

    # ------------------------------------------------------------------
    # 3b. Tool calling
    # ------------------------------------------------------------------
    print("\n--- 3b. Tool calling (OpenRouter) ---")

    @tool
    def get_capital(country: str) -> str:
        """Return the capital city of a country."""
        capitals = {
            "France": "Paris",
            "Japan": "Tokyo",
            "Brazil": "Brasília",
            "Canada": "Ottawa",
        }
        return capitals.get(country, f"Unknown capital for {country}")

    or_with_tools = openrouter_model.bind_tools([get_capital])

    or_tool_response = or_with_tools.invoke(
        "What is the capital of France?"
    )
    print_msg("3b OpenRouter tool-call response", or_tool_response)

    # ------------------------------------------------------------------
    # 3c. Streaming
    # ------------------------------------------------------------------
    print("\n--- 3c. Streaming (OpenRouter) ---")

    print("Streaming: ", end="", flush=True)
    for token in openrouter_model.stream("Give me a fun fact about dogs."):
        print(token.content, end="", flush=True)
    print()

    # ------------------------------------------------------------------
    # 3d. init_chat_model factory (openrouter provider)
    # ------------------------------------------------------------------
    print("\n--- 3d. init_chat_model factory (openrouter provider) ---")

    from langchain.chat_models import init_chat_model

    or_factory = init_chat_model(
        "qwen/qwen3-397b-a22b",
        model_provider="openrouter",
        openai_api_key=openai_api_key,
        openai_api_base="https://openrouter.ai/api/v1",
    )

    factory_resp = or_factory.invoke("What is 1+1?")
    print_msg("3d Factory model response", factory_resp)


# ===========================================================================
# ENTRY POINT
# ===========================================================================

if __name__ == "__main__":
    demos = {
        "1": (demo_chat_qwen,       "ChatQwen — DashScope API (recommended)"),
        "2": (demo_chat_ollama,     "ChatOllama — Local Ollama"),
        "3": (demo_chat_openrouter, "ChatOpenRouter — OpenRouter routing"),
        "a": (demo_chat_qwen,       "ChatQwen — DashScope API (recommended)"),
        "b": (demo_chat_ollama,     "ChatOllama — Local Ollama"),
        "c": (demo_chat_openrouter, "ChatOpenRouter — OpenRouter routing"),
        "all": (None,               "Run all demos (requires DashScope API key)"),
    }

    print("""
╔══════════════════════════════════════════════════════════════╗
║    LangChain + Qwen3 Integration Examples  ·  main runner   ║
╠══════════════════════════════════════════════════════════════╣
║  Run a specific demo:                                        ║
║    python qwen3_example.py 1    ← ChatQwen  (DashScope)      ║
║    python qwen3_example.py 2    ← ChatOllama (local)         ║
║    python qwen3_example.py 3    ← ChatOpenRouter             ║
║                                                              ║
║  Run all demos:                                              ║
║    python qwen3_example.py all                               ║
╚══════════════════════════════════════════════════════════════╝
""")

    choice = sys.argv[1].lower() if len(sys.argv) > 1 else "1"

    if choice == "all":
        print("\n>> Running ALL demos...\n")
        try:
            demo_chat_qwen()
        except Exception as e:
            print(f"[ERROR in ChatQwen] {e}")
            print(">> Skipping ChatQwen and continuing...\n")

        try:
            demo_chat_ollama()
        except Exception as e:
            print(f"[ERROR in ChatOllama] {e}")
            print(">> Skipping ChatOllama and continuing...\n")

        try:
            demo_chat_openrouter()
        except Exception as e:
            print(f"[ERROR in ChatOpenRouter] {e}")
            print(">> Skipping ChatOpenRouter.\n")

    elif choice in demos:
        fn, desc = demos[choice]
        print(f">> Running: {desc}\n")
        fn()
    else:
        print(f"Unknown choice: {choice!r}")
        print("Valid choices: 1, 2, 3, all")
        sys.exit(1)

    print("\n✔ Done.")
