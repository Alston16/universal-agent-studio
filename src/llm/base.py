"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Iterator, List, Optional

from src.core.types import LLMConfig, LLMResponse, Message, ModelCapabilities


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers."""

    def __init__(self, config: LLMConfig) -> None:
        """
        Initialize the LLM provider.

        Args:
            config: Configuration for the LLM provider
        """
        self.config = config
        self._validate_config()

    @abstractmethod
    def _validate_config(self) -> None:
        """
        Validate the provider configuration.

        Raises:
            ConfigurationError: If configuration is invalid
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> ModelCapabilities:
        """
        Get the capabilities of the model.

        Returns:
            ModelCapabilities object describing what the model supports
        """
        pass

    @abstractmethod
    def complete(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: object,
    ) -> LLMResponse:
        """
        Generate a completion for the given messages.

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature (overrides config)
            max_tokens: Maximum tokens to generate (overrides config)
            **kwargs: Additional provider-specific parameters

        Returns:
            LLMResponse containing the generated completion

        Raises:
            LLMProviderError: If completion fails
        """
        pass

    @abstractmethod
    def stream_complete(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: object,
    ) -> Iterator[str]:
        """
        Stream a completion for the given messages.

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature (overrides config)
            max_tokens: Maximum tokens to generate (overrides config)
            **kwargs: Additional provider-specific parameters

        Yields:
            Chunks of the generated completion

        Raises:
            LLMProviderError: If streaming fails
        """
        pass

    @abstractmethod
    async def acomplete(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: object,
    ) -> LLMResponse:
        """
        Asynchronously generate a completion for the given messages.

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature (overrides config)
            max_tokens: Maximum tokens to generate (overrides config)
            **kwargs: Additional provider-specific parameters

        Returns:
            LLMResponse containing the generated completion

        Raises:
            LLMProviderError: If completion fails
        """
        pass

    @abstractmethod
    async def astream_complete(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: object,
    ) -> AsyncIterator[str]:
        """
        Asynchronously stream a completion for the given messages.

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature (overrides config)
            max_tokens: Maximum tokens to generate (overrides config)
            **kwargs: Additional provider-specific parameters

        Yields:
            Chunks of the generated completion

        Raises:
            LLMProviderError: If streaming fails
        """
        pass

    def _get_temperature(self, temperature: Optional[float]) -> float:
        """Get temperature value, using override or config default."""
        return temperature if temperature is not None else self.config.temperature

    def _get_max_tokens(self, max_tokens: Optional[int]) -> Optional[int]:
        """Get max_tokens value, using override or config default."""
        return max_tokens if max_tokens is not None else self.config.max_tokens

    def __repr__(self) -> str:
        """String representation of the provider."""
        return f"{self.__class__.__name__}(model={self.config.model})"

 
