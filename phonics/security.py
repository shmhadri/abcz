from __future__ import annotations

import hashlib
import time
from functools import wraps

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse


def client_ip(request) -> str:
    """Use the address supplied by the trusted WSGI server, never a client header."""
    return str(request.META.get("REMOTE_ADDR") or "unknown")[:64]


def _digest(value: object) -> str:
    return hashlib.sha256(str(value or "").strip().casefold().encode("utf-8")).hexdigest()[:32]


def rate_limit(scope: str, *, limit_setting: str, default: int, window: int = 60, identity=None, methods=("POST",)):
    """Small cache-backed fixed-window limiter; Redis is used when configured."""
    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if request.method not in methods:
                return view(request, *args, **kwargs)
            limit = max(1, int(getattr(settings, limit_setting, default)))
            bucket = int(time.time() // window)
            identity_value = identity(request) if identity else client_ip(request)
            key = f"security:rate:{scope}:{_digest(identity_value)}:{bucket}"
            try:
                if cache.add(key, 1, timeout=window + 2):
                    count = 1
                else:
                    count = cache.incr(key)
            except Exception:
                # Do not silently disable protection when the shared store is unavailable.
                return JsonResponse(
                    {"error": "rate_limit_unavailable", "message": "Please try again later."},
                    status=503,
                )
            if count > limit:
                response = JsonResponse(
                    {"error": "rate_limited", "message": "Too many requests. Please try again later."},
                    status=429,
                )
                response["Retry-After"] = str(window)
                return response
            return view(request, *args, **kwargs)
        return wrapped
    return decorator


def login_identity(request):
    return request.POST.get("username", "")
