from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlparse


PRODUCTION_HOSTS = {"abcz-epbz.onrender.com"}
DEFAULT_PASSWORD = "LoadTestPass123!"


@dataclass(frozen=True)
class LoadTestConfig:
    base_url: str
    username_prefix: str
    password: str
    run_id: str
    allow_production: bool


def env_bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def is_production_url(base_url: str) -> bool:
    parsed = urlparse(base_url)
    return parsed.hostname in PRODUCTION_HOSTS


def validate_base_url(base_url: str, *, allow_production: bool = False) -> str:
    candidate = (base_url or "").strip().rstrip("/")
    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("LOAD_TEST_BASE_URL must be an absolute http(s) URL.")
    if is_production_url(candidate) and not allow_production:
        raise ValueError(
            "Refusing to run load tests against production. "
            "Set ALLOW_PRODUCTION_LOAD_TEST=true only after explicit approval."
        )
    return candidate


def get_config() -> LoadTestConfig:
    allow_production = env_bool("ALLOW_PRODUCTION_LOAD_TEST", "false")
    base_url = validate_base_url(
        os.getenv("LOAD_TEST_BASE_URL", "http://127.0.0.1:8000"),
        allow_production=allow_production,
    )
    prefix = os.getenv("LOAD_TEST_USERNAME_PREFIX", "loadtest_user_").strip()
    if not prefix.startswith("loadtest_"):
        raise ValueError("LOAD_TEST_USERNAME_PREFIX must start with 'loadtest_'.")
    return LoadTestConfig(
        base_url=base_url,
        username_prefix=prefix,
        password=os.getenv("LOAD_TEST_PASSWORD", DEFAULT_PASSWORD),
        run_id=os.getenv("LOAD_TEST_RUN_ID", "local"),
        allow_production=allow_production,
    )
