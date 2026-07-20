from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TypeVar

from django.conf import settings
from django.core.cache import cache


T = TypeVar("T")
USER_CACHE_VERSION = "v1"
STATIC_CACHE_VERSION = "v1"


def user_cache_key(kind: str, user_id: int) -> str:
    return f"user:{kind}:{USER_CACHE_VERSION}:{user_id}"


def static_cache_key(kind: str) -> str:
    return f"static:{kind}:{STATIC_CACHE_VERSION}"


def subscription_cache_timeout() -> int:
    return int(getattr(settings, "SUBSCRIPTION_CACHE_TIMEOUT", 300))


def static_content_cache_timeout() -> int:
    return int(getattr(settings, "STATIC_CONTENT_CACHE_TIMEOUT", 1800))


def safe_cache_get(key: str):
    try:
        return cache.get(key)
    except Exception:
        return None


def safe_cache_set(key: str, value, timeout: int | None = None) -> None:
    try:
        cache.set(key, value, timeout=timeout)
    except Exception:
        return


def safe_cache_delete(key: str) -> None:
    try:
        cache.delete(key)
    except Exception:
        return


def safe_cache_delete_many(keys: Iterable[str]) -> None:
    try:
        cache.delete_many(list(keys))
    except Exception:
        for key in keys:
            safe_cache_delete(key)


def get_cached_user_group_slugs(user, calculator: Callable[[], set[str]]) -> set[str]:
    return set(_get_cached_user_list(user.pk, "group-slugs", calculator))


def get_cached_active_plan_codes(user, calculator: Callable[[], set[str]]) -> set[str]:
    return set(_get_cached_user_list(user.pk, "active-plan-codes", calculator))


def get_cached_feature_keys(user, calculator: Callable[[], set[str]]) -> set[str]:
    return set(_get_cached_user_list(user.pk, "feature-keys", calculator))


def get_cached_subscription_plan(user, calculator: Callable[[], str]) -> str:
    key = user_cache_key("subscription-plan", user.pk)
    cached = safe_cache_get(key)
    if isinstance(cached, str):
        return cached
    value = calculator()
    safe_cache_set(key, value, timeout=subscription_cache_timeout())
    return value


def _get_cached_user_list(user_id: int, kind: str, calculator: Callable[[], set[str]]) -> list[str]:
    key = user_cache_key(kind, user_id)
    cached = safe_cache_get(key)
    if isinstance(cached, list):
        return [str(item) for item in cached]
    values = sorted(str(item) for item in calculator())
    safe_cache_set(key, values, timeout=subscription_cache_timeout())
    return values


def invalidate_user_subscription_cache(user_id: int | None) -> None:
    if not user_id:
        return
    safe_cache_delete_many([
        user_cache_key("group-slugs", user_id),
        user_cache_key("active-plan-codes", user_id),
        user_cache_key("subscription-plan", user_id),
        user_cache_key("feature-keys", user_id),
    ])


def get_cached_static_value(kind: str, calculator: Callable[[], T], *, timeout: int | None = None) -> T:
    key = static_cache_key(kind)
    cached = safe_cache_get(key)
    if cached is not None:
        return cached
    value = calculator()
    safe_cache_set(
        key,
        value,
        timeout=static_content_cache_timeout() if timeout is None else timeout,
    )
    return value


def invalidate_static_cache(kind: str) -> None:
    safe_cache_delete(static_cache_key(kind))
