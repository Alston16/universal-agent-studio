import os

from utils.env_manager import add_env_variable, get_env_variable, remove_env_variable


def test_add_env_variable() -> None:
    key = "TEST_ENV_VAR"
    value = "test_value"

    add_env_variable(key, value)
    assert os.environ.get(key) == value
    # Clean up
    remove_env_variable(key)

def test_get_env_variable() -> None:
    key = "TEST_ENV_VAR"
    value = "test_value"

    os.environ[key] = value
    retrieved_value = get_env_variable(key)
    assert retrieved_value == value

    # Test for non-existing variable
    assert get_env_variable("NON_EXISTING_VAR") is None
    # Clean up
    del os.environ[key]

def test_remove_env_variable() -> None:
    key = "TEST_ENV_VAR"
    value = "test_value"

    os.environ[key] = value
    remove_env_variable(key)
    assert os.environ.get(key) is None