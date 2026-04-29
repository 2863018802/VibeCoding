import os
from typing import Iterator, Optional
from openai import OpenAI

from app.config import settings


class Qwen3Client:
    """Qwen3-32B 客户端封装，支持流式和非流式调用"""

    def __init__(self):
        api_key = settings.dashscope_api_key or os.getenv("DASHSCOPE_API_KEY", "")
        self.client = OpenAI(
            api_key=api_key,
            base_url=settings.llm_base_url,
        )
        self.model = settings.llm_model

    def chat(
        self,
        messages: list[dict],
        stream: bool = True,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> Iterator[str] | str:
        """
        发送对话请求
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            stream: 是否流式返回
            temperature: 温度参数
            max_tokens: 最大 token 数
            
        Yields/Returns:
            流式模式: yield 每个 chunk 的 content
            非流式: 返回完整的 content
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=stream,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        if stream:
            full_content = ""
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_content += content
                    yield content
        else:
            return response.choices[0].message.content

    def chat_with_thinking(
        self,
        messages: list[dict],
        stream: bool = True,
        temperature: float = 0.3,
    ) -> Iterator[dict] | dict:
        """
        发送对话请求（包含思考过程）
        
        Returns:
            流式模式: yield {"thinking": "...", "content": "..."}
            非流式: 返回 {"thinking": "...", "content": "..."}
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=stream,
            temperature=temperature,
        )

        if stream:
            thinking = ""
            content = ""
            in_thinking = False
            
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    
                    # 检测思考标签
                    if "<thinking>" in text:
                        in_thinking = True
                        thinking += text.replace("<thinking>", "")
                    elif "</thinking>" in text:
                        in_thinking = False
                        thinking += text.replace("</thinking>", "")
                    elif in_thinking:
                        thinking += text
                    else:
                        content += text
                    
                    yield {"thinking": thinking, "content": content}
        else:
            full = response.choices[0].message.content
            thinking = ""
            content = ""
            in_thinking = False
            
            if "<thinking>" in full:
                start = full.find("<thinking>") + len("<thinking>")
                end = full.find("</thinking>")
                thinking = full[start:end] if end > start else ""
                content = full[end + len("</thinking>"):] if end > 0 else full
            
            return {"thinking": thinking, "content": content}


# Singleton instance
_qwen_client: Optional[Qwen3Client] = None


def get_qwen_client() -> Qwen3Client:
    global _qwen_client
    if _qwen_client is None:
        _qwen_client = Qwen3Client()
    return _qwen_client
