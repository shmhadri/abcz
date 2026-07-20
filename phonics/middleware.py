from __future__ import annotations

import logging
import re
import time
import uuid
from contextvars import ContextVar

from django.conf import settings


_current_request: ContextVar[object | None] = ContextVar("current_request", default=None)
_REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
logger = logging.getLogger("abcz.requests")


def get_current_request():
    return _current_request.get()


def safe_request_id(value):
    if not value:
        return ""
    candidate = str(value).strip()
    if not _REQUEST_ID_RE.fullmatch(candidate):
        return ""
    return candidate


class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = safe_request_id(request.headers.get("X-Request-ID")) or str(uuid.uuid4())
        request.request_id = request_id
        token = _current_request.set(request)
        try:
            response = self.get_response(request)
        finally:
            _current_request.reset(token)
        response["X-Request-ID"] = request_id
        return response


class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started_at = time.perf_counter()
        response = self.get_response(request)
        duration_ms = (time.perf_counter() - started_at) * 1000

        if getattr(settings, "REQUEST_LOG_ENABLED", True):
            logger.info(
                "request_complete",
                extra={
                    "request_id": getattr(request, "request_id", ""),
                    "method": request.method,
                    "path": request.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                },
            )

        if settings.DEBUG or getattr(settings, "ENABLE_SERVER_TIMING_HEADER", False):
            response["Server-Timing"] = f"app;dur={duration_ms:.1f}"

        csp_report_only = getattr(settings, "CSP_REPORT_ONLY", "")
        if csp_report_only:
            response.setdefault("Content-Security-Policy-Report-Only", csp_report_only)

        return response
