"""OpenAI LLM provider implementation."""

from collections.abc import AsyncIterator
from typing import Iterator, List, Optional

import openai
from openai import AsyncOpenAI, OpenAI

from src.core.exceptions import (
    AuthenticationError,
    ConfigurationError,
    InvalidRequestError,
    LLMProviderError,
    RateLimitError,
)
from src.core.types import LLMConfig, LLMResponse, Message, ModelCapabilities
from src.llm.base import BaseLLMProvider
from src.llm.registry import LLMProviderRegistry


@LLMProviderRegistry.register("openai")
class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider implementation."""

    def __init__(self, config: LLMConfig) -> None:
        """Initialize OpenAI provider."""
        super().__init__(config)
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.api_base,
            timeout=config.timeout,
            max_retries=config.max_retries,
        )
        self.async_client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.api_base,
            timeout=config.timeout,
            max_retries=config.max_retries,
        )

    def _validate_config(self) -> None:
        """Validate OpenAI configuration."""
        if not self.config.api_key:
            raise ConfigurationError("OpenAI API key is required")
        if not self.config.model:
            raise ConfigurationError("Model name is required")

    def get_capabilities(self) -> ModelCapabilities:
        """Get capabilities of the OpenAI model."""
        # Most OpenAI models support these features
        supports_function_calling = "gpt-4" in self.config.model or "gpt-3.5" in self.config.model
        supports_vision = "vision" in self.config.model or "gpt-4o" in self.config.model

        return ModelCapabilities(
            supports_function_calling=supports_function_calling,
            supports_json_mode=True,
            supports_vision=supports_vision,
            supports_streaming=True,
            context_window=self._get_context_window(),
        )

    def _get_context_window(self) -> int:
        """Get context window size for the model."""
        model_lower = self.config.model.lower()
        if "gpt-4-turbo" in model_lower or "gpt-4o" in model_lower:
            return 128000
        elif "gpt-4" in model_lower:
            return 8192
        elif "gpt-3.5-turbo-16k" in model_lower:
            return 16384
        elif "gpt-3.5" in model_lower:
            return 4096
        return 4096  # Default

    def _convert_messages(self, messages: List[Message]) -> List[dict[str, object]]:
        """Convert internal Message objects to OpenAI format."""
        return [msg.to_dict() for msg in messages]

    def _handle_error(self, error: Exception) -> None:
        """Convert OpenAI errors to UAS exceptions."""
        if isinstance(error, openai.AuthenticationError):
            raise AuthenticationError(f"OpenAI authentication failed: {error}") from error
        elif isinstance(error, openai.RateLimitError):
            raise RateLimitError(f"OpenAI rate limit exceeded: {error}") from error
        elif isinstance(error, openai.BadRequestError):
            raise InvalidRequestError(f"Invalid OpenAI request: {error}") from error
        else:
            raise LLMProviderError(f"OpenAI error: {error}") from error

    def complete(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: object,
    ) -> LLMResponse:
        """Generate a completion using OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=self._convert_messages(messages),  # type: ignore
                temperature=self._get_temperature(temperature),
                max_tokens=self._get_max_tokens(max_tokens),
                top_p=self.config.top_p,
                frequency_penalty=self.config.frequency_penalty,
                presence_penalty=self.config.presence_penalty,
                **kwargs,
            )

            choice = response.choices[0]
            return LLMResponse(
                content=choice.message.content or "",
                model=response.model,
                finish_reason=choice.finish_reason,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
                function_call=choice.message.function_call.model_dump() if choice.message.function_call else None,  # type: ignore
                tool_calls=[tc.model_dump() for tc in choice.message.tool_calls] if choice.message.tool_calls else None,  # type: ignore
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
        """Stream a completion using OpenAI."""
        try:
            stream = self.client.chat.completions.create(
                model=self.config.model,
                messages=self._convert_messages(messages),  # type: ignore
                temperature=self._get_temperature(temperature),
                max_tokens=self._get_max_tokens(max_tokens),
                top_p=self.config.top_p,
                frequency_penalty=self.config.frequency_penalty,
                presence_penalty=self.config.presence_penalty,
                stream=True,
                **kwargs,
            )

            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            self._handle_error(e)

    async def acomplete(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: object,
    ) -> LLMResponse:
        """Asynchronously generate a completion using OpenAI."""
        try:
            response = await self.async_client.chat.completions.create(
                model=self.config.model,
                messages=self._convert_messages(messages),  # type: ignore
                temperature=self._get_temperature(temperature),
                max_tokens=self._get_max_tokens(max_tokens),
                top_p=self.config.top_p,
                frequency_penalty=self.config.frequency_penalty,
                presence_penalty=self.config.presence_penalty,
                **kwargs,
            )

            choice = response.choices[0]
            return LLMResponse(
                content=choice.message.content or "",
                model=response.model,
                finish_reason=choice.finish_reason,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
                function_call=choice.message.function_call.model_dump() if choice.message.function_call else None,  # type: ignore
                tool_calls=[tc.model_dump() for tc in choice.message.tool_calls] if choice.message.tool_calls else None,  # type: ignore
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
        """Asynchronously stream a completion using OpenAI."""
        try:
            stream = await self.async_client.chat.completions.create(
                model=self.config.model,
                messages=self._convert_messages(messages),  # type: ignore
                temperature=self._get_temperature(temperature),
                max_tokens=self._get_max_tokens(max_tokens),
                top_p=self.config.top_p,
                frequency_penalty=self.config.frequency_penalty,
                presence_penalty=self.config.presence_penalty,
                stream=True,
                **kwargs,
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            self._handle_error(e)

 
