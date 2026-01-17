"""Unit tests for core types."""

import pytest

from src.core.types import LLMConfig, LLMResponse, Message, MessageRole, ModelCapabilities


class TestMessageRole:
    """Tests for MessageRole enum."""

    def test_message_role_values(self) -> None:
        """Test that MessageRole has correct values."""
        assert MessageRole.SYSTEM.value == "system"
        assert MessageRole.USER.value == "user"
        assert MessageRole.ASSISTANT.value == "assistant"
        assert MessageRole.FUNCTION.value == "function"
        assert MessageRole.TOOL.value == "tool"


class TestMessage:
    """Tests for Message dataclass."""

    def test_message_creation(self) -> None:
        """Test creating a basic message."""
        msg = Message(role=MessageRole.USER, content="Hello")
        assert msg.role == MessageRole.USER
        assert msg.content == "Hello"
        assert msg.name is None
        assert msg.function_call is None
        assert msg.tool_calls is None

    def test_message_to_dict(self) -> None:
        """Test converting message to dictionary."""
        msg = Message(role=MessageRole.USER, content="Hello")
        result = msg.to_dict()
        assert result == {"role": "user", "content": "Hello"}

    def test_message_to_dict_with_name(self) -> None:
        """Test converting message with name to dictionary."""
        msg = Message(role=MessageRole.ASSISTANT, content="Hi", name="assistant1")
        result = msg.to_dict()
        assert result == {"role": "assistant", "content": "Hi", "name": "assistant1"}

    def test_message_to_dict_with_function_call(self) -> None:
        """Test converting message with function call to dictionary."""
        function_call = {"name": "get_weather", "arguments": '{"location": "NYC"}'}
        msg = Message(
            role=MessageRole.ASSISTANT, content="", function_call=function_call
        )
        result = msg.to_dict()
        assert result["function_call"] == function_call


class TestModelCapabilities:
    """Tests for ModelCapabilities dataclass."""

    def test_default_capabilities(self) -> None:
        """Test default model capabilities."""
        caps = ModelCapabilities()
        assert caps.supports_function_calling is False
        assert caps.supports_json_mode is False
        assert caps.supports_vision is False
        assert caps.supports_streaming is True
        assert caps.max_tokens is None
        assert caps.context_window is None

    def test_custom_capabilities(self) -> None:
        """Test custom model capabilities."""
        caps = ModelCapabilities(
            supports_function_calling=True,
            supports_json_mode=True,
            max_tokens=4096,
            context_window=8192,
        )
        assert caps.supports_function_calling is True
        assert caps.supports_json_mode is True
        assert caps.max_tokens == 4096
        assert caps.context_window == 8192


class TestLLMResponse:
    """Tests for LLMResponse dataclass."""

    def test_basic_response(self) -> None:
        """Test creating a basic LLM response."""
        response = LLMResponse(content="Hello!", model="gpt-4")
        assert response.content == "Hello!"
        assert response.model == "gpt-4"
        assert response.finish_reason is None
        assert response.usage is None
        assert response.metadata == {}

    def test_response_with_usage(self) -> None:
        """Test LLM response with usage information."""
        usage = {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        response = LLMResponse(
            content="Hello!", model="gpt-4", usage=usage, finish_reason="stop"
        )
        assert response.usage == usage
        assert response.finish_reason == "stop"


class TestLLMConfig:
    """Tests for LLMConfig dataclass."""

    def test_minimal_config(self) -> None:
        """Test creating minimal LLM configuration."""
        config = LLMConfig(provider="openai", model="gpt-4")
        assert config.provider == "openai"
        assert config.model == "gpt-4"
        assert config.temperature == 0.7
        assert config.timeout == 60
        assert config.max_retries == 3

    def test_full_config(self) -> None:
        """Test creating full LLM configuration."""
        config = LLMConfig(
            provider="openai",
            model="gpt-4",
            api_key="test-key",
            api_base="https://api.example.com",
            temperature=0.5,
            max_tokens=1000,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.2,
            timeout=120,
            max_retries=5,
            extra_params={"custom": "value"},
        )
        assert config.api_key == "test-key"
        assert config.api_base == "https://api.example.com"
        assert config.temperature == 0.5
        assert config.max_tokens == 1000
        assert config.extra_params == {"custom": "value"}

    def test_config_to_dict(self) -> None:
        """Test converting config to dictionary."""
        config = LLMConfig(provider="openai", model="gpt-4", api_key="test-key")
        result = config.to_dict()
        assert result["provider"] == "openai"
        assert result["model"] == "gpt-4"
        assert result["api_key"] == "test-key"
        assert result["temperature"] == 0.7
