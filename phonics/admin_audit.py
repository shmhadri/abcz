from __future__ import annotations

from typing import Any

from .models import AdminAuditLog


def _audit_value(value: Any) -> dict:
    if value in (None, ""):
        return {}
    if isinstance(value, dict):
        return value
    return {"value": str(value)}


def log_admin_action(
    request,
    *,
    action: str,
    target,
    before_status=None,
    after_status=None,
    note: str = "",
    provider_event_id: str = "",
):
    actor = request.user if getattr(request.user, "is_authenticated", False) else None
    if actor is not None and not actor.pk:
        actor = None

    meta = getattr(request, "META", {})
    ip_address = str(meta.get("REMOTE_ADDR") or "").strip() or None
    user_agent = str(meta.get("HTTP_USER_AGENT") or "")[:512]
    model_label = target._meta.label if hasattr(target, "_meta") else target.__class__.__name__
    target_id = str(getattr(target, "pk", "") or "")

    return AdminAuditLog.objects.create(
        actor=actor,
        action=str(action)[:80],
        target_model=str(model_label)[:120],
        target_id=target_id[:120],
        target_repr=str(target)[:255],
        before_status=_audit_value(before_status),
        after_status=_audit_value(after_status),
        note=str(note),
        ip_address=ip_address,
        user_agent=user_agent,
        provider_event_id=str(provider_event_id)[:120],
    )
