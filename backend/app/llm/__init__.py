"""
LLM provider factory for FinBank AI.
"""

from typing import Literal
from app.llm.base import BaseLLMProvider, LLMResponse
from app.llm.openai_provider import OpenAIProvider
from app.llm.claude_provider import ClaudeProvider
from app.llm.ollama_provider import OllamaProvider
from app.config import get_settings

ProviderType = Literal["openai", "claude", "azure", "ollama"]


def get_llm_provider(provider_type: ProviderType | None = None) -> BaseLLMProvider:
    """
    Get an LLM provider instance.

    Args:
        provider_type: The provider to use. If None, uses the default from settings.

    Returns:
        An LLM provider instance.
    """
    settings = get_settings()
    provider = provider_type or settings.default_llm_provider

    if provider == "openai":
        return OpenAIProvider()
    elif provider == "claude":
        return ClaudeProvider()
    elif provider == "azure":
        # Azure OpenAI uses the same interface as OpenAI
        return OpenAIProvider(model=settings.azure_openai_deployment or "gpt-4")
    elif provider == "ollama":
        return OllamaProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


__all__ = [
    "BaseLLMProvider",
    "LLMResponse",
    "OpenAIProvider",
    "ClaudeProvider",
    "OllamaProvider",
    "get_llm_provider",
    "ProviderType",
]
