"""Registry and factory for LLM providers."""

from typing import Dict, Type

from src.core.exceptions import ConfigurationError, ModelNotFoundError
from src.core.types import LLMConfig
from src.llm.base import BaseLLMProvider


class LLMProviderRegistry:
    """Registry for managing LLM provider implementations."""

    _providers: Dict[str, Type[BaseLLMProvider]] = {}

    @classmethod
    def register(cls, provider_name: str) -> object:
        """
        Decorator to register an LLM provider.

        Args:
            provider_name: Unique name for the provider

        Returns:
            Decorator function

        Example:
            @LLMProviderRegistry.register("openai")
            class OpenAIProvider(BaseLLMProvider):
                pass
        """

        def decorator(provider_class: Type[BaseLLMProvider]) -> Type[BaseLLMProvider]:  # type: ignore
            if not issubclass(provider_class, BaseLLMProvider):
                raise TypeError(
                    f"{provider_class.__name__} must inherit from BaseLLMProvider"
                )
            cls._providers[provider_name.lower()] = provider_class
            return provider_class

        return decorator

    @classmethod
    def get_provider(cls, provider_name: str) -> Type[BaseLLMProvider]:
        """
        Get a registered provider class by name.

        Args:
            provider_name: Name of the provider

        Returns:
            Provider class

        Raises:
            ModelNotFoundError: If provider is not registered
        """
        provider_name_lower = provider_name.lower()
        if provider_name_lower not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ModelNotFoundError(
                f"Provider '{provider_name}' not found. Available providers: {available}"
            )
        return cls._providers[provider_name_lower]

    @classmethod
    def list_providers(cls) -> list[str]:
        """
        List all registered provider names.

        Returns:
            List of provider names
        """
        return list(cls._providers.keys())

    @classmethod
    def is_registered(cls, provider_name: str) -> bool:
        """
        Check if a provider is registered.

        Args:
            provider_name: Name of the provider

        Returns:
            True if registered, False otherwise
        """
        return provider_name.lower() in cls._providers


class LLMProviderFactory:
    """Factory for creating LLM provider instances."""

    @staticmethod
    def create_provider(config: LLMConfig) -> BaseLLMProvider:
        """
        Create an LLM provider instance from configuration.

        Args:
            config: LLM configuration

        Returns:
            Initialized LLM provider instance

        Raises:
            ConfigurationError: If configuration is invalid
            ModelNotFoundError: If provider is not registered
        """
        if not config.provider:
            raise ConfigurationError("Provider name is required in configuration")

        provider_class = LLMProviderRegistry.get_provider(config.provider)
        return provider_class(config)

    @staticmethod
    def create_from_dict(config_dict: Dict[str, object]) -> BaseLLMProvider:
        """
        Create an LLM provider instance from a dictionary.

        Args:
            config_dict: Configuration dictionary

        Returns:
            Initialized LLM provider instance

        Raises:
            ConfigurationError: If configuration is invalid
            ModelNotFoundError: If provider is not registered
        """
        try:
            config = LLMConfig(**config_dict)  # type: ignore
        except TypeError as e:
            raise ConfigurationError(f"Invalid configuration: {e}") from e

        return LLMProviderFactory.create_provider(config)

 
