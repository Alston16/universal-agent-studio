"""Configuration management for Universal Agent Studio."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from src.core.exceptions import ConfigurationError


class ConfigManager:
    """Manages application configuration with support for multiple sources."""

    def __init__(self, config_dir: Optional[Path] = None) -> None:
        """
        Initialize the configuration manager.

        Args:
            config_dir: Directory to store configuration files.
                       Defaults to ~/.uas/config
        """
        if config_dir is None:
            config_dir = Path.home() / ".uas" / "config"

        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file and environment variables."""
        # Load from config file
        config_file = self.config_dir / "config.json"
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    self._config = json.load(f)
            except json.JSONDecodeError as e:
                raise ConfigurationError(f"Invalid JSON in config file: {e}") from e
            except Exception as e:
                raise ConfigurationError(f"Failed to load config file: {e}") from e

        # Override with environment variables
        self._load_from_env()

    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # Environment variables with UAS_ prefix override config file
        for key, value in os.environ.items():
            if key.startswith("UAS_"):
                config_key = key[4:].lower()  # Remove UAS_ prefix
                self._config[config_key] = value

    def save_config(self) -> None:
        """Save current configuration to file."""
        config_file = self.config_dir / "config.json"
        try:
            with open(config_file, "w") as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            raise ConfigurationError(f"Failed to save config file: {e}") from e

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key (supports dot notation for nested keys)
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration key (supports dot notation for nested keys)
            value: Value to set
        """
        keys = key.split(".")
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def delete(self, key: str) -> None:
        """
        Delete a configuration value.

        Args:
            key: Configuration key (supports dot notation for nested keys)

        Raises:
            ConfigurationError: If key not found
        """
        keys = key.split(".")
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                raise ConfigurationError(f"Configuration key '{key}' not found")
            config = config[k]

        if keys[-1] not in config:
            raise ConfigurationError(f"Configuration key '{key}' not found")

        del config[keys[-1]]

    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.

        Returns:
            Dictionary of all configuration values
        """
        return self._config.copy()

    def clear(self) -> None:
        """Clear all configuration values."""
        self._config = {}

    def has(self, key: str) -> bool:
        """
        Check if a configuration key exists.

        Args:
            key: Configuration key (supports dot notation for nested keys)

        Returns:
            True if key exists, False otherwise
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return False

        return True


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """
    Get the global configuration manager instance.

    Returns:
        ConfigManager instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

 
