"""
LangChain + Local Qwen3 via Ollama
===================================
Run Qwen3 entirely on your own machine using Ollama — no API key needed.

Prerequisites:
  1. Install Ollama: https://ollama.com/download
  2. Pull a Qwen3 variant:
       ollama pull qwen3:32b        # 32B parameters  (~20 GB VRAM)
       ollama pull qwen3:8b        #  8B parameters  (~5 GB VRAM, fast on CPU)
       ollama pull qwen3:14b       #  14B parameters (~9 GB VRAM)
  3. Keep `ollama serve` running in a terminal.

Usage:
    python qwen3_local_ollama.py
"""

import asyncio
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama, OllamaEmbeddings

# ===========================================================================
# SECTION 1 — Model setup
# ===========================================================================

# Ollama listens on localhost:11434 by default.
# If you changed the port, update base_url accordingly.
OLLAMA_BASE_URL = "http://localhost:11434"

# Available Qwen3 variants on Ollama.
# The "thinking" suffix variants have chain-of-thought capabilities.
# Source: https://ollama.com/library?qwen3
QWEN3_VARIANTS = {
    "qwen3:8b":      "8B params  — CPU-friendly, ~5 GB RAM",
    "qwen3:14b":     "14B params — ~9 GB VRAM",
    "qwen3:32b":     "32B params — ~20 GB VRAM, best quality",
    "qwen3:30b-a3b": "30B params, 3B expert — efficient MoE",
}

# Pick the model to use.
MODEL_NAME = "qwen3:32b"

# ===========================================================================
# SECTION 2 — LLM setup
# ===========================================================================

llm = ChatOllama(
    model=MODEL_NAME,
    base_url=OLLAMA_BASE_URL,
    temperature=0.7,
    num_ctx=8192,       # context window (increase for longer conversations)
    top_k=40,
    top_p=0.95,
)


# ===========================================================================
# SECTION 3 — Basic chat
# ===========================================================================

def basic_chat():
    print("\n" + "=" * 60)
    print("  1. Basic chat")
    print("=" * 60)

    messages = [
        SystemMessage(content="You are a knowledgeable assistant."),
        HumanMessage(content="Explain what a Large Language Model is."),
    ]

    print("\nPrompt: Explain what a Large Language Model is.\n")
    print("Response:")
    response = llm.invoke(messages)
    print(response.content)


# ===========================================================================
# SECTION 4 — Tool calling (function calling)
# ===========================================================================

@tool
def celsius_to_fahrenheit(celsius: float) -> str:
    """Convert a temperature from Celsius to Fahrenheit.

    Args:
        celsius: Temperature in degrees Celsius.
    Returns:
        Temperature in degrees Fahrenheit (rounded to 1 decimal).
    """
    fahrenheit = celsius * 9 / 5 + 32
    return f"{celsius}°C = {fahrenheit:.1f}°F"


@tool
def word_count(text: str) -> int:
    """Count the number of words in a text string.

    Args:
        text: The input text string.
    Returns:
        The number of words.
    """
    return len(text.split())


def tool_calling():
    print("\n" + "=" * 60)
    print("  2. Tool calling (bind_tools)")
    print("=" * 60)

    llm_with_tools = llm.bind_tools([celsius_to_fahrenheit, word_count])

    # Tool call 1 — temperature conversion
    print("\nPrompt: Convert 37 degrees Celsius to Fahrenheit.\n")
    response1 = llm_with_tools.invoke(
        "Convert 37 degrees Celsius to Fahrenheit."
    )
    print(f"Tool result: {response1.tool_calls}")
    # Execute the tool manually (LangChain agents automate this)
    if response1.tool_calls:
        for tc in response1.tool_calls:
            fn = tc["name"]
            args = tc["args"]
            if fn == "celsius_to_fahrenheit":
                print(f">> {celsius_to_fahrenheit.invoke(args)}")

    # Tool call 2 — word count
    print("\nPrompt: Count the words in 'The quick brown fox jumps over the lazy dog'.\n")
    response2 = llm_with_tools.invoke(
        "Count the words in 'The quick brown fox jumps over the lazy dog'."
    )
    print(f"Tool result: {response2.tool_calls}")
    if response2.tool_calls:
        for tc in response2.tool_calls:
            fn = tc["name"]
            args = tc["args"]
            if fn == "word_count":
                print(f">> {word_count.invoke(args)}")


# ===========================================================================
# SECTION 5 — Streaming
# ===========================================================================

def streaming():
    print("\n" + "=" * 60)
    print("  3. Streaming")
    print("=" * 60)

    print("\nPrompt: Tell me a short fact about artificial intelligence.\n")
    print("Streaming: ", end="", flush=True)

    collected = []
    for token in llm.stream("Tell me a short fact about artificial intelligence."):
        print(token.content, end="", flush=True)
        collected.append(token.content)
    print("\n")

    full_text = "".join(collected)
    print(f"[Total characters streamed: {len(full_text)}]")


# ===========================================================================
# SECTION 6 — Async
# ===========================================================================

async def async_demo():
    print("\n" + "=" * 60)
    print("  4. Async (ainvoke)")
    print("=" * 60)

    response = await llm.ainvoke("What is the capital of Japan?")
    print(f"\nPrompt: What is the capital of Japan?\n")
    print(f"Response: {response.content}")
    print(f"[Usage] {response.usage_metadata}")


# ===========================================================================
# SECTION 7 — Embeddings (for RAG)
# ===========================================================================

def embeddings_demo():
    print("\n" + "=" * 60)
    print("  5. Embeddings (OllamaEmbeddings)")
    print("=" * 60)

    embeddings = OllamaEmbeddings(
        model="nomic-embed-text",  # run: ollama pull nomic-embed-text
        base_url=OLLAMA_BASE_URL,
    )

    # Generate embeddings for sample texts
    texts = [
        "LangChain is a framework for building LLM applications.",
        "Qwen3 is a large language model from Alibaba Cloud.",
        "RAG stands for Retrieval-Augmented Generation.",
    ]

    print("\nGenerating embeddings for 3 texts...\n")
    for text in texts:
        vec = embeddings.embed_query(text)
        print(f"  Text : {text}")
        print(f"  Dims : {len(vec)}")
        print(f"  Head : {vec[:5]} ...\n")


# ===========================================================================
# SECTION 8 — Chat history (memory)
# ===========================================================================

def chat_with_memory():
    print("\n" + "=" * 60)
    print("  6. Chat with memory (conversation buffer)")
    print("=" * 60)

    from langchain.memory import ConversationBufferMemory
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain.chains import LLMChain

    memory = ConversationBufferMemory(memory_key="history", return_messages=True)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant who remembers conversation context."),
        MessagesPlaceholder("history"),
        ("human", "{input}"),
    ])

    chain = LLMChain(llm=llm, prompt=prompt, memory=memory)

    # Turn 1
    print("\n--- Turn 1 ---")
    r1 = chain.invoke({"input": "My name is Alice and I love reading science fiction."})
    print(f"Alice: My name is Alice and I love reading science fiction.")
    print(f"Bot  : {r1['text'][:120]}...")

    # Turn 2
    print("\n--- Turn 2 ---")
    r2 = chain.invoke({"input": "What is my name and what do I love?"})
    print(f"Alice: What is my name and what do I love?")
    print(f"Bot  : {r2['text']}")

    # Turn 3
    print("\n--- Turn 3 ---")
    r3 = chain.invoke({"input": "What did I tell you about myself?"})
    print(f"Alice: What did I tell you about myself?")
    print(f"Bot  : {r3['text']}")


# ===========================================================================
# ENTRY POINT
# ===========================================================================

if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║   LangChain + Local Qwen3 (Ollama)                          ║
╠══════════════════════════════════════════════════════════════╣
║  Model : {MODEL_NAME:<50} ║
║  URL   : {OLLAMA_BASE_URL:<50} ║
║                                                              ║
║  Make sure `ollama serve` is running in another terminal!   ║
╚══════════════════════════════════════════════════════════════╝
""")

    basic_chat()
    tool_calling()
    streaming()
    asyncio.run(async_demo())
    embeddings_demo()
    chat_with_memory()

    print("\n✔ All demos complete.")
    print("  Run 'ollama pull qwen3:8b' to try a smaller model.")
