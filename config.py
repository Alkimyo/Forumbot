"""Configuration module.

Loads and validates all environment variables required by the bot.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


class ConfigError(Exception):
    """Raised when required configuration values are missing or invalid."""


def _get_env(name: str) -> str:
    """Return the value of an environment variable or raise ConfigError.

    Args:
        name: The environment variable name.

    Returns:
        The value of the environment variable.

    Raises:
        ConfigError: If the variable is not set.
    """
    value = os.getenv(name)
    if not value:
        raise ConfigError(f"Environment variable '{name}' is not set.")
    return value


@dataclass(frozen=True)
class Config:
    """Holds all runtime configuration for the bot."""

    bot_token: str
    api_id: int
    api_hash: str
    session_string: str
    topics_per_page: int = 100

    @classmethod
    def load(cls) -> "Config":
        """Build a Config instance from environment variables.

        Returns:
            A populated, validated Config object.

        Raises:
            ConfigError: If any required variable is missing or malformed.
        """
        bot_token = _get_env("BOT_TOKEN")
        api_id_raw = _get_env("API_ID")
        api_hash = _get_env("API_HASH")
        session_string = _get_env("SESSION_STRING")

        try:
            api_id = int(api_id_raw)
        except ValueError as exc:
            raise ConfigError("Environment variable 'API_ID' must be an integer.") from exc

        return cls(
            bot_token=bot_token,
            api_id=api_id,
            api_hash=api_hash,
            session_string=session_string,
        )


config = Config.load()
