"""Integration tests for LLM providers.

Note: These tests require valid API keys to be set in environment variables:
- OPENAI_API_KEY for OpenAI tests
- ANTHROPIC_API_KEY for Anthropic tests

Mark tests with @pytest.mark.integration and skip if API keys are not available.
"""

import os

import pytest

from src.core.types import LLMConfig, Message, MessageRole
from src.llm.providers.anthropic_provider import AnthropicProvider
from src.llm.providers.openai_provider import OpenAIProvider
from src.llm.registry import LLMProviderFactory


@pytest.mark.integration
class TestOpenAIProviderIntegration:
    """Integration tests for OpenAI provider."""

    @pytest.fixture
    def skip_if_no_api_key(self) -> None:
        """Skip test if OpenAI API key is not available."""
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")

    def test_openai_completion(self, skip_if_no_api_key: None) -> None:
        """Test OpenAI completion with real API."""
        config = LLMConfig(
            provider="openai",
            model="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.7,
            max_tokens=50,
        )
        provider = OpenAIProvider(config)

        messages = [Message(role=MessageRole.USER, content="Say 'Hello, World!' and nothing else.")]

        response = provider.complete(messages)

        assert response.content
        assert response.model
        assert "hello" in response.content.lower()

    def test_openai_streaming(self, skip_if_no_api_key: None) -> None:
        """Test OpenAI streaming with real API."""
        config = LLMConfig(
            provider="openai",
            model="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.7,
            max_tokens=50,
        )
        provider = OpenAIProvider(config)

        messages = [Message(role=MessageRole.USER, content="Count from 1 to 3.")]

        chunks = list(provider.stream_complete(messages))

        assert len(chunks) > 0
        full_response = "".join(chunks)
        assert full_response

    @pytest.mark.asyncio
    async def test_openai_async_completion(self, skip_if_no_api_key: None) -> None:
        """Test OpenAI async completion with real API."""
        config = LLMConfig(
            provider="openai",
            model="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.7,
            max_tokens=50,
        )
        provider = OpenAIProvider(config)

        messages = [Message(role=MessageRole.USER, content="Say 'Hello, World!' and nothing else.")]

        response = await provider.acomplete(messages)

        assert response.content
        assert "hello" in response.content.lower()


@pytest.mark.integration
class TestAnthropicProviderIntegration:
    """Integration tests for Anthropic provider."""

    @pytest.fixture
    def skip_if_no_api_key(self) -> None:
        """Skip test if Anthropic API key is not available."""
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

    def test_anthropic_completion(self, skip_if_no_api_key: None) -> None:
        """Test Anthropic completion with real API."""
        config = LLMConfig(
            provider="anthropic",
            model="claude-3-haiku-20240307",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.7,
            max_tokens=50,
        )
        provider = AnthropicProvider(config)

        messages = [Message(role=MessageRole.USER, content="Say 'Hello, World!' and nothing else.")]

        response = provider.complete(messages)

        assert response.content
        assert response.model
        assert "hello" in response.content.lower()

    def test_anthropic_streaming(self, skip_if_no_api_key: None) -> None:
        """Test Anthropic streaming with real API."""
        config = LLMConfig(
            provider="anthropic",
            model="claude-3-haiku-20240307",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.7,
            max_tokens=50,
        )
        provider = AnthropicProvider(config)

        messages = [Message(role=MessageRole.USER, content="Count from 1 to 3.")]

        chunks = list(provider.stream_complete(messages))

        assert len(chunks) > 0
        full_response = "".join(chunks)
        assert full_response


@pytest.mark.integration
class TestProviderFactory:
    """Integration tests for provider factory."""

    def test_create_openai_provider_from_factory(self) -> None:
        """Test creating OpenAI provider using factory."""
        config = LLMConfig(
            provider="openai",
            model="gpt-3.5-turbo",
            api_key="test-key",
        )
        provider = LLMProviderFactory.create_provider(config)

        assert isinstance(provider, OpenAIProvider)
        assert provider.config.model == "gpt-3.5-turbo"

    def test_create_anthropic_provider_from_factory(self) -> None:
        """Test creating Anthropic provider using factory."""
        config = LLMConfig(
            provider="anthropic",
            model="claude-3-haiku-20240307",
            api_key="test-key",
        )
        provider = LLMProviderFactory.create_provider(config)

        assert isinstance(provider, AnthropicProvider)
        assert provider.config.model == "claude-3-haiku-20240307"

 
