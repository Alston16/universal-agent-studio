"""Unit tests for custom exceptions."""

import pytest

from src.core.exceptions import (
    AuthenticationError,
    ConfigurationError,
    InvalidRequestError,
    LLMProviderError,
    ModelNotFoundError,
    RateLimitError,
    UASException,
)


class TestExceptionHierarchy:
    """Tests for exception hierarchy."""

    def test_uas_exception_is_base(self) -> None:
        """Test that UASException is the base exception."""
        assert issubclass(UASException, Exception)

    def test_configuration_error_inheritance(self) -> None:
        """Test ConfigurationError inherits from UASException."""
        assert issubclass(ConfigurationError, UASException)

    def test_llm_provider_error_inheritance(self) -> None:
        """Test LLMProviderError inherits from UASException."""
        assert issubclass(LLMProviderError, UASException)

    def test_authentication_error_inheritance(self) -> None:
        """Test AuthenticationError inherits from LLMProviderError."""
        assert issubclass(AuthenticationError, LLMProviderError)
        assert issubclass(AuthenticationError, UASException)

    def test_rate_limit_error_inheritance(self) -> None:
        """Test RateLimitError inherits from LLMProviderError."""
        assert issubclass(RateLimitError, LLMProviderError)
        assert issubclass(RateLimitError, UASException)

    def test_invalid_request_error_inheritance(self) -> None:
        """Test InvalidRequestError inherits from LLMProviderError."""
        assert issubclass(InvalidRequestError, LLMProviderError)
        assert issubclass(InvalidRequestError, UASException)

    def test_model_not_found_error_inheritance(self) -> None:
        """Test ModelNotFoundError inherits from LLMProviderError."""
        assert issubclass(ModelNotFoundError, LLMProviderError)
        assert issubclass(ModelNotFoundError, UASException)


class TestExceptionRaising:
    """Tests for raising and catching exceptions."""

    def test_raise_uas_exception(self) -> None:
        """Test raising UASException."""
        with pytest.raises(UASException) as exc_info:
            raise UASException("Test error")
        assert str(exc_info.value) == "Test error"

    def test_raise_configuration_error(self) -> None:
        """Test raising ConfigurationError."""
        with pytest.raises(ConfigurationError) as exc_info:
            raise ConfigurationError("Invalid config")
        assert str(exc_info.value) == "Invalid config"

    def test_raise_llm_provider_error(self) -> None:
        """Test raising LLMProviderError."""
        with pytest.raises(LLMProviderError) as exc_info:
            raise LLMProviderError("Provider failed")
        assert str(exc_info.value) == "Provider failed"

    def test_raise_authentication_error(self) -> None:
        """Test raising AuthenticationError."""
        with pytest.raises(AuthenticationError) as exc_info:
            raise AuthenticationError("Auth failed")
        assert str(exc_info.value) == "Auth failed"

    def test_raise_rate_limit_error(self) -> None:
        """Test raising RateLimitError."""
        with pytest.raises(RateLimitError) as exc_info:
            raise RateLimitError("Rate limit exceeded")
        assert str(exc_info.value) == "Rate limit exceeded"

    def test_raise_invalid_request_error(self) -> None:
        """Test raising InvalidRequestError."""
        with pytest.raises(InvalidRequestError) as exc_info:
            raise InvalidRequestError("Invalid request")
        assert str(exc_info.value) == "Invalid request"

    def test_raise_model_not_found_error(self) -> None:
        """Test raising ModelNotFoundError."""
        with pytest.raises(ModelNotFoundError) as exc_info:
            raise ModelNotFoundError("Model not found")
        assert str(exc_info.value) == "Model not found"


class TestExceptionCatching:
    """Tests for catching exceptions at different levels."""

    def test_catch_specific_as_base(self) -> None:
        """Test catching specific exception as base exception."""
        with pytest.raises(UASException):
            raise ConfigurationError("Test")

    def test_catch_authentication_as_llm_provider_error(self) -> None:
        """Test catching AuthenticationError as LLMProviderError."""
        with pytest.raises(LLMProviderError):
            raise AuthenticationError("Test")

    def test_catch_rate_limit_as_llm_provider_error(self) -> None:
        """Test catching RateLimitError as LLMProviderError."""
        with pytest.raises(LLMProviderError):
            raise RateLimitError("Test")

 
