"""Unit tests for configuration manager."""

import json
import os
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from src.config.manager import ConfigManager, get_config_manager
from src.core.exceptions import ConfigurationError


class TestConfigManager:
    """Tests for ConfigManager class."""

    @pytest.fixture
    def temp_config_dir(self) -> Generator[Path, None, None]:
        """Create a temporary config directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def config_manager(self, temp_config_dir: Path) -> ConfigManager:
        """Create a ConfigManager instance with temp directory."""
        return ConfigManager(config_dir=temp_config_dir)

    def test_init_creates_directory(self, temp_config_dir: Path) -> None:
        """Test that initialization creates config directory."""
        config_dir = temp_config_dir / "new_config"
        assert not config_dir.exists()
        ConfigManager(config_dir=config_dir)
        assert config_dir.exists()

    def test_get_nonexistent_key_returns_default(
        self, config_manager: ConfigManager
    ) -> None:
        """Test getting nonexistent key returns default value."""
        result = config_manager.get("nonexistent", "default")
        assert result == "default"

    def test_get_nonexistent_key_returns_none(
        self, config_manager: ConfigManager
    ) -> None:
        """Test getting nonexistent key without default returns None."""
        result = config_manager.get("nonexistent")
        assert result is None

    def test_set_and_get_simple_value(self, config_manager: ConfigManager) -> None:
        """Test setting and getting a simple value."""
        config_manager.set("test_key", "test_value")
        result = config_manager.get("test_key")
        assert result == "test_value"

    def test_set_and_get_nested_value(self, config_manager: ConfigManager) -> None:
        """Test setting and getting nested values using dot notation."""
        config_manager.set("level1.level2.key", "value")
        result = config_manager.get("level1.level2.key")
        assert result == "value"

    def test_get_nested_with_default(self, config_manager: ConfigManager) -> None:
        """Test getting nested nonexistent key returns default."""
        result = config_manager.get("level1.level2.key", "default")
        assert result == "default"

    def test_has_existing_key(self, config_manager: ConfigManager) -> None:
        """Test has() returns True for existing key."""
        config_manager.set("test_key", "value")
        assert config_manager.has("test_key") is True

    def test_has_nonexistent_key(self, config_manager: ConfigManager) -> None:
        """Test has() returns False for nonexistent key."""
        assert config_manager.has("nonexistent") is False

    def test_has_nested_key(self, config_manager: ConfigManager) -> None:
        """Test has() works with nested keys."""
        config_manager.set("level1.level2.key", "value")
        assert config_manager.has("level1.level2.key") is True
        assert config_manager.has("level1.level2.nonexistent") is False

    def test_delete_existing_key(self, config_manager: ConfigManager) -> None:
        """Test deleting an existing key."""
        config_manager.set("test_key", "value")
        config_manager.delete("test_key")
        assert config_manager.has("test_key") is False

    def test_delete_nonexistent_key_raises_error(
        self, config_manager: ConfigManager
    ) -> None:
        """Test deleting nonexistent key raises ConfigurationError."""
        with pytest.raises(ConfigurationError):
            config_manager.delete("nonexistent")

    def test_delete_nested_key(self, config_manager: ConfigManager) -> None:
        """Test deleting a nested key."""
        config_manager.set("level1.level2.key", "value")
        config_manager.delete("level1.level2.key")
        assert config_manager.has("level1.level2.key") is False

    def test_get_all(self, config_manager: ConfigManager) -> None:
        """Test getting all configuration values."""
        config_manager.set("key1", "value1")
        config_manager.set("key2", "value2")
        all_config = config_manager.get_all()
        assert all_config == {"key1": "value1", "key2": "value2"}

    def test_clear(self, config_manager: ConfigManager) -> None:
        """Test clearing all configuration."""
        config_manager.set("key1", "value1")
        config_manager.set("key2", "value2")
        config_manager.clear()
        assert config_manager.get_all() == {}

    def test_save_and_load_config(self, temp_config_dir: Path) -> None:
        """Test saving and loading configuration from file."""
        manager1 = ConfigManager(config_dir=temp_config_dir)
        manager1.set("test_key", "test_value")
        manager1.save_config()

        # Create new manager instance to load saved config
        manager2 = ConfigManager(config_dir=temp_config_dir)
        assert manager2.get("test_key") == "test_value"

    def test_load_invalid_json_raises_error(self, temp_config_dir: Path) -> None:
        """Test loading invalid JSON raises ConfigurationError."""
        config_file = temp_config_dir / "config.json"
        config_file.write_text("invalid json{")

        with pytest.raises(ConfigurationError):
            ConfigManager(config_dir=temp_config_dir)

    def test_environment_variable_override(
        self, temp_config_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that environment variables override config file."""
        # Set up config file
        manager = ConfigManager(config_dir=temp_config_dir)
        manager.set("test_key", "file_value")
        manager.save_config()

        # Set environment variable
        monkeypatch.setenv("UAS_TEST_KEY", "env_value")

        # Create new manager to load config
        new_manager = ConfigManager(config_dir=temp_config_dir)
        assert new_manager.get("test_key") == "env_value"

    def test_set_complex_nested_structure(self, config_manager: ConfigManager) -> None:
        """Test setting complex nested structures."""
        config_manager.set("db.host", "localhost")
        config_manager.set("db.port", 5432)
        config_manager.set("db.credentials.user", "admin")
        config_manager.set("db.credentials.password", "secret")

        assert config_manager.get("db.host") == "localhost"
        assert config_manager.get("db.port") == 5432
        assert config_manager.get("db.credentials.user") == "admin"
        assert config_manager.get("db.credentials.password") == "secret"


class TestGetConfigManager:
    """Tests for get_config_manager function."""

    def test_returns_singleton(self) -> None:
        """Test that get_config_manager returns the same instance."""
        manager1 = get_config_manager()
        manager2 = get_config_manager()
        assert manager1 is manager2

    def test_singleton_persists_data(self) -> None:
        """Test that singleton instance persists data."""
        manager1 = get_config_manager()
        manager1.set("test_key", "test_value")

        manager2 = get_config_manager()
        assert manager2.get("test_key") == "test_value"

 
