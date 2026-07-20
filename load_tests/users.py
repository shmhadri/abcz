from __future__ import annotations

from collections import defaultdict
from itertools import count
from threading import Lock

from .config import get_config


_counters = defaultdict(lambda: count(1))
_lock = Lock()


def next_username(role: str) -> str:
    config = get_config()
    with _lock:
        index = next(_counters[role])
    return f"{config.username_prefix}{role}_{index:04d}"


def credentials_for(role: str) -> tuple[str, str]:
    config = get_config()
    return next_username(role), config.password
