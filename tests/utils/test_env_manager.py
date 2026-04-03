import os

import utils.env_manager as env_manager
from utils.env_manager import add_env_variable, get_env_variable, remove_env_variable


def test_add_env_variable(tmp_path, monkeypatch):
    # Use a temporary .env file for this test
    tmp_env_file = tmp_path / ".env"
    tmp_env_file.touch()
    monkeypatch.setattr(env_manager, "ENV_PATH", tmp_env_file)

    key = "TEST_ENV_VAR"
    value = "test_value"

    # Ensure original environment state is restored after the test
    monkeypatch.delenv(key, raising=False)

    add_env_variable(key, value)
    assert os.environ.get(key) == value


def test_get_env_variable(tmp_path, monkeypatch):
    # Use a temporary .env file for this test
    tmp_env_file = tmp_path / ".env"
    tmp_env_file.touch()
    monkeypatch.setattr(env_manager, "ENV_PATH", tmp_env_file)

    key = "TEST_ENV_VAR"
    value = "test_value"

    # Set and later restore the environment variable via monkeypatch
    monkeypatch.setenv(key, value)

    retrieved_value = get_env_variable(key)
    assert retrieved_value == value

    # Test for non-existing variable
    assert get_env_variable("NON_EXISTING_VAR") is None


def test_remove_env_variable(tmp_path, monkeypatch):
    # Use a temporary .env file for this test
    tmp_env_file = tmp_path / ".env"
    tmp_env_file.touch()
    monkeypatch.setattr(env_manager, "ENV_PATH", tmp_env_file)

    key = "TEST_ENV_VAR"
    value = "test_value"

    # Set and later restore the environment variable via monkeypatch
    monkeypatch.setenv(key, value)
    remove_env_variable(key)
    assert os.environ.get(key) is None