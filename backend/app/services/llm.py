"""OpenAI-compatible chat completions (DeepSeek and others)."""

from typing import Optional

from openai import APIConnectionError, APIStatusError, AsyncOpenAI, AuthenticationError

from app.core.config import settings


def llm_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=settings.LLM_API_KEY or "missing-key",
        base_url=settings.LLM_API_BASE,
        timeout=60,
    )


async def chat(
    messages: list[dict[str, str]],
    *,
    model: Optional[str] = None,
    temperature: float = 0.2,
) -> str:
    if not settings.LLM_API_KEY.strip():
        raise ValueError("Set LLM_API_KEY, DEEPSEEK_API_KEY, or OPENAI_API_KEY in the environment")

    client = llm_client()
    resp = await client.chat.completions.create(
        model=model or settings.LLM_MODEL,
        messages=messages,
        temperature=temperature,
    )
    choice = resp.choices[0].message
    return (choice.content or "").strip()


__all__ = ["chat", "llm_client", "APIConnectionError", "APIStatusError", "AuthenticationError"]
