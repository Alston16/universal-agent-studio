"""Unit tests for LLM provider registry and factory."""

import pytest

from src.core.exceptions import ConfigurationError, ModelNotFoundError
from src.core.types import LLMConfig, Message, MessageRole, ModelCapabilities
from src.llm.base import BaseLLMProvider
from src.llm.registry import LLMProviderFactory, LLMProviderRegistry


# Mock provider for testing
class MockProvider(BaseLLMProvider):
    """Mock LLM provider for testing."""

    def _validate_config(self) -> None:
        """Validate configuration."""
        if not self.config.model:
            raise ConfigurationError("Model is required")

    def get_capabilities(self) -> ModelCapabilities:
        """Get model capabilities."""
        return ModelCapabilities()

    def complete(self, messages, temperature=None, max_tokens=None, **kwargs):  # type: ignore
        """Mock completion."""
        from src.core.types import LLMResponse

        return LLMResponse(content="Mock response", model=self.config.model)

    def stream_complete(self, messages, temperature=None, max_tokens=None, **kwargs):  # type: ignore
        """Mock streaming completion."""
        yield "Mock"
        yield " response"

    async def acomplete(self, messages, temperature=None, max_tokens=None, **kwargs):  # type: ignore
        """Mock async completion."""
        from src.core.types import LLMResponse

        return LLMResponse(content="Mock async response", model=self.config.model)

    async def astream_complete(self, messages, temperature=None, max_tokens=None, **kwargs):  # type: ignore
        """Mock async streaming completion."""
        yield "Mock"
        yield " async"
        yield " response"


class TestLLMProviderRegistry:
    """Tests for LLMProviderRegistry."""

    def test_register_provider(self) -> None:
        """Test registering a provider."""

        @LLMProviderRegistry.register("test_provider")
        class TestProvider(BaseLLMProvider):
            def _validate_config(self) -> None:
                pass

            def get_capabilities(self) -> ModelCapabilities:
                return ModelCapabilities()

            def complete(self, messages, temperature=None, max_tokens=None, **kwargs):  # type: ignore
                pass

            def stream_complete(self, messages, temperature=None, max_tokens=None, **kwargs):  # type: ignore
                pass

            async def acomplete(self, messages, temperature=None, max_tokens=None, **kwargs):  # type: ignore
                pass

            async def astream_complete(self, messages, temperature=None, max_tokens=None, **kwargs):  # type: ignore
                pass

        assert LLMProviderRegistry.is_registered("test_provider")
        assert "test_provider" in LLMProviderRegistry.list_providers()

    def test_register_non_provider_raises_error(self) -> None:
        """Test registering non-BaseLLMProvider class raises error."""
        with pytest.raises(TypeError):

            @LLMProviderRegistry.register("invalid")
            class NotAProvider:
                pass

    def test_get_registered_provider(self) -> None:
        """Test getting a registered provider."""
        LLMProviderRegistry.register("mock")(MockProvider)
        provider_class = LLMProviderRegistry.get_provider("mock")
        assert provider_class == MockProvider

    def test_get_nonexistent_provider_raises_error(self) -> None:
        """Test getting nonexistent provider raises ModelNotFoundError."""
        with pytest.raises(ModelNotFoundError) as exc_info:
            LLMProviderRegistry.get_provider("nonexistent_provider")
        assert "nonexistent_provider" in str(exc_info.value)

    def test_list_providers(self) -> None:
        """Test listing all registered providers."""
        LLMProviderRegistry.register("mock1")(MockProvider)
        LLMProviderRegistry.register("mock2")(MockProvider)
        providers = LLMProviderRegistry.list_providers()
        assert "mock1" in providers
        assert "mock2" in providers

    def test_is_registered(self) -> None:
        """Test checking if provider is registered."""
        LLMProviderRegistry.register("mock_check")(MockProvider)
        assert LLMProviderRegistry.is_registered("mock_check") is True
        assert LLMProviderRegistry.is_registered("not_registered") is False

    def test_case_insensitive_registration(self) -> None:
        """Test that provider names are case-insensitive."""
        LLMProviderRegistry.register("CaseSensitive")(MockProvider)
        assert LLMProviderRegistry.is_registered("casesensitive")
        assert LLMProviderRegistry.is_registered("CASESENSITIVE")
        provider = LLMProviderRegistry.get_provider("CaSeSenSiTiVe")
        assert provider == MockProvider


class TestLLMProviderFactory:
    """Tests for LLMProviderFactory."""

    def test_create_provider_from_config(self) -> None:
        """Test creating provider from LLMConfig."""
        LLMProviderRegistry.register("factory_test")(MockProvider)
        config = LLMConfig(provider="factory_test", model="test-model")
        provider = LLMProviderFactory.create_provider(config)
        assert isinstance(provider, MockProvider)
        assert provider.config.model == "test-model"

    def test_create_provider_without_provider_name_raises_error(self) -> None:
        """Test creating provider without provider name raises error."""
        config = LLMConfig(provider="", model="test-model")
        with pytest.raises(ConfigurationError) as exc_info:
            LLMProviderFactory.create_provider(config)
        assert "Provider name is required" in str(exc_info.value)

    def test_create_provider_with_nonexistent_provider_raises_error(self) -> None:
        """Test creating provider with nonexistent provider raises error."""
        config = LLMConfig(provider="nonexistent", model="test-model")
        with pytest.raises(ModelNotFoundError):
            LLMProviderFactory.create_provider(config)

    def test_create_from_dict(self) -> None:
        """Test creating provider from dictionary."""
        LLMProviderRegistry.register("dict_test")(MockProvider)
        config_dict = {
            "provider": "dict_test",
            "model": "test-model",
            "temperature": 0.5,
            "max_tokens": 1000,
        }
        provider = LLMProviderFactory.create_from_dict(config_dict)
        assert isinstance(provider, MockProvider)
        assert provider.config.model == "test-model"
        assert provider.config.temperature == 0.5
        assert provider.config.max_tokens == 1000

    def test_create_from_dict_with_invalid_config_raises_error(self) -> None:
        """Test creating provider from invalid dict raises error."""
        invalid_dict = {"invalid_key": "value"}
        with pytest.raises(ConfigurationError):
            LLMProviderFactory.create_from_dict(invalid_dict)

    def test_create_provider_validates_config(self) -> None:
        """Test that provider config is validated on creation."""
        LLMProviderRegistry.register("validation_test")(MockProvider)
        config = LLMConfig(provider="validation_test", model="")
        with pytest.raises(ConfigurationError) as exc_info:
            LLMProviderFactory.create_provider(config)
        assert "Model is required" in str(exc_info.value)

 
