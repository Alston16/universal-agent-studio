"""Type definitions for Universal Agent Studio."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class MessageRole(Enum):
    """Enum for message roles in conversations."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"


@dataclass
class Message:
    """Represents a single message in a conversation."""

    role: MessageRole
    content: str
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format."""
        result: Dict[str, Any] = {
            "role": self.role.value,
            "content": self.content,
        }
        if self.name:
            result["name"] = self.name
        if self.function_call:
            result["function_call"] = self.function_call
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        return result


@dataclass
class ModelCapabilities:
    """Represents capabilities of an LLM model."""

    supports_function_calling: bool = False
    supports_json_mode: bool = False
    supports_vision: bool = False
    supports_streaming: bool = True
    max_tokens: Optional[int] = None
    context_window: Optional[int] = None


@dataclass
class LLMResponse:
    """Represents a response from an LLM."""

    content: str
    model: str
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMConfig:
    """Configuration for an LLM provider."""

    provider: str
    model: str
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 60
    max_retries: int = 3
    extra_params: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "provider": self.provider,
            "model": self.model,
            "api_key": self.api_key,
            "api_base": self.api_base,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "extra_params": self.extra_params,
        }

 
