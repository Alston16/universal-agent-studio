"""Anthropic LLM provider implementation."""

from collections.abc import AsyncIterator
from typing import Iterator, List, Optional

import anthropic
from anthropic import Anthropic, AsyncAnthropic

from src.core.exceptions import (
    AuthenticationError,
    ConfigurationError,
    InvalidRequestError,
    LLMProviderError,
    RateLimitError,
)
from src.core.types import LLMConfig, LLMResponse, Message, MessageRole, ModelCapabilities
from src.llm.base import BaseLLMProvider
from src.llm.registry import LLMProviderRegistry


@LLMProviderRegistry.register("anthropic")
class AnthropicProvider(BaseLLMProvider):
    """Anthropic (Claude) LLM provider implementation."""

    def __init__(self, config: LLMConfig) -> None:
        """Initialize Anthropic provider."""
        super().__init__(config)
        self.client = Anthropic(
            api_key=config.api_key,
            base_url=config.api_base,
            timeout=config.timeout,
            max_retries=config.max_retries,
        )
        self.async_client = AsyncAnthropic(
            api_key=config.api_key,
            base_url=config.api_base,
            timeout=config.timeout,
            max_retries=config.max_retries,
        )

    def _validate_config(self) -> None:
        """Validate Anthropic configuration."""
        if not self.config.api_key:
            raise ConfigurationError("Anthropic API key is required")
        if not self.config.model:
            raise ConfigurationError("Model name is required")

    def get_capabilities(self) -> ModelCapabilities:
        """Get capabilities of the Anthropic model."""
        supports_vision = "claude-3" in self.config.model

        return ModelCapabilities(
            supports_function_calling=True,
            supports_json_mode=False,
            supports_vision=supports_vision,
            supports_streaming=True,
            context_window=self._get_context_window(),
        )

    def _get_context_window(self) -> int:
        """Get context window size for the model."""
        model_lower = self.config.model.lower()
        if "claude-3" in model_lower or "claude-2.1" in model_lower:
            return 200000
        elif "claude-2" in model_lower:
            return 100000
        return 100000  # Default

    def _convert_messages(self, messages: List[Message]) -> tuple[Optional[str], List[dict[str, str]]]:
        """
        Convert internal Message objects to Anthropic format.
        
        Returns:
            Tuple of (system_prompt, messages_list)
        """
        system_prompt: Optional[str] = None
        anthropic_messages: List[dict[str, str]] = []

        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_prompt = msg.content
            else:
                anthropic_messages.append({
                    "role": "user" if msg.role == MessageRole.USER else "assistant",
                    "content": msg.content,
                })

        return system_prompt, anthropic_messages

    def _handle_error(self, error: Exception) -> None:
        """Convert Anthropic errors to UAS exceptions."""
        if isinstance(error, anthropic.AuthenticationError):
            raise AuthenticationError(f"Anthropic authentication failed: {error}") from error
        elif isinstance(error, anthropic.RateLimitError):
            raise RateLimitError(f"Anthropic rate limit exceeded: {error}") from error
        elif isinstance(error, anthropic.BadRequestError):
            raise InvalidRequestError(f"Invalid Anthropic request: {error}") from error
        else:
            raise LLMProviderError(f"Anthropic error: {error}") from error

    def complete(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: object,
    ) -> LLMResponse:
        """Generate a completion using Anthropic."""
        try:
            system_prompt, anthropic_messages = self._convert_messages(messages)
            
            # Anthropic requires max_tokens
            max_tokens_value = self._get_max_tokens(max_tokens) or 4096

            response = self.client.messages.create(
                model=self.config.model,
                messages=anthropic_messages,  # type: ignore
                system=system_prompt or "",
                temperature=self._get_temperature(temperature),
                max_tokens=max_tokens_value,
                **kwargs,
            )

            return LLMResponse(
                content=response.content[0].text if response.content else "",
                model=response.model,
                finish_reason=response.stop_reason,
                usage={
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
            )
        except Exception as e:
            self._handle_error(e)
            raise  # This won't be reached but satisfies type checker

    def stream_complete(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: object,
    ) -> Iterator[str]:
        """Stream a completion using Anthropic."""
        try:
            system_prompt, anthropic_messages = self._convert_messages(messages)
            
            # Anthropic requires max_tokens
            max_tokens_value = self._get_max_tokens(max_tokens) or 4096

            with self.client.messages.stream(
                model=self.config.model,
                messages=anthropic_messages,  # type: ignore
                system=system_prompt or "",
                temperature=self._get_temperature(temperature),
                max_tokens=max_tokens_value,
                **kwargs,
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            self._handle_error(e)

    async def acomplete(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: object,
    ) -> LLMResponse:
        """Asynchronously generate a completion using Anthropic."""
        try:
            system_prompt, anthropic_messages = self._convert_messages(messages)
            
            # Anthropic requires max_tokens
            max_tokens_value = self._get_max_tokens(max_tokens) or 4096

            response = await self.async_client.messages.create(
                model=self.config.model,
                messages=anthropic_messages,  # type: ignore
                system=system_prompt or "",
                temperature=self._get_temperature(temperature),
                max_tokens=max_tokens_value,
                **kwargs,
            )

            return LLMResponse(
                content=response.content[0].text if response.content else "",
                model=response.model,
                finish_reason=response.stop_reason,
                usage={
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
            )
        except Exception as e:
            self._handle_error(e)
            raise  # This won't be reached but satisfies type checker

    async def astream_complete(  # type: ignore
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: object,
    ) -> AsyncIterator[str]:
        """Asynchronously stream a completion using Anthropic."""
        try:
            system_prompt, anthropic_messages = self._convert_messages(messages)
            
            # Anthropic requires max_tokens
            max_tokens_value = self._get_max_tokens(max_tokens) or 4096

            async with self.async_client.messages.stream(
                model=self.config.model,
                messages=anthropic_messages,  # type: ignore
                system=system_prompt or "",
                temperature=self._get_temperature(temperature),
                max_tokens=max_tokens_value,
                **kwargs,
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            self._handle_error(e)

 
