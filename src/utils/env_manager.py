import os
from pathlib import Path

from dotenv import set_key, unset_key

ENV_PATH = Path(__file__).parent.parent.parent / ".env"


def add_env_variable(key: str, value: str) -> None:
    """
    Adds an environment variable to the .env.
    Replaces the value if the variable already exists.

    Args:
        key (str): The name of the environment variable.
        value (str): The value of the environment variable.
    """
    os.environ[key] = value

    if not ENV_PATH.exists():
        ENV_PATH.touch()
    set_key(str(ENV_PATH), key, value)

def get_env_variable(key: str) -> str | None:
    """
    Retrieves the value of an environment variable.

    Args:
        key (str): The name of the environment variable.

    Returns:
        str | None: The value of the environment variable, or None if it does not exist.
    """
    return os.environ.get(key)

def remove_env_variable(key: str) -> None:
    """
    Removes an environment variable from the .env.
    Does nothing if the variable does not exist.

    Args:
        key (str): The name of the environment variable to remove.
    """
    if key in os.environ:
        del os.environ[key]

    if ENV_PATH.exists():
        unset_key(str(ENV_PATH), key)