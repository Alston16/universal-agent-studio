"""Custom exceptions for Universal Agent Studio."""


class UASException(Exception):
    """Base exception for all UAS errors."""

    pass


class ConfigurationError(UASException):
    """Raised when there's a configuration error."""

    pass


class LLMProviderError(UASException):
    """Raised when there's an error with an LLM provider."""

    pass


class AuthenticationError(LLMProviderError):
    """Raised when authentication with an LLM provider fails."""

    pass


class RateLimitError(LLMProviderError):
    """Raised when rate limit is exceeded."""

    pass


class InvalidRequestError(LLMProviderError):
    """Raised when the request to LLM provider is invalid."""

    pass


class ModelNotFoundError(LLMProviderError):
    """Raised when the requested model is not found."""

    pass

 
