import os
from typing import Any, Dict, List, Optional

import yaml
from dotenv import load_dotenv


def load_env() -> None:
    """Load environment variables from .env if present."""
    load_dotenv(override=False)


def load_yaml_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(name, default)


def coalesce_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def take_first_words(text: str, max_words: int) -> str:
    words: List[str] = text.split()
    return " ".join(words[:max_words]) if max_words > 0 else text


def ensure_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def jql_escape_literal(text: str) -> str:
    """Escape a value for use inside JQL quoted literals.

    Only escape backslash and double quote for JQL quoted strings.
    """
    if text is None:
        return ""
    escaped = str(text)
    escaped = escaped.replace("\\", "\\\\").replace('"', '\\"')
    return escaped
