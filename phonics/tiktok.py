from __future__ import annotations

from decimal import Decimal

from django.conf import settings


REGISTRATION_SESSION_KEY = "tiktok_complete_registration"


def event(name: str, payload: dict | None = None) -> dict:
    result = {"name": name}
    if payload:
        result["payload"] = payload
    return result


def product_payload(*, plan_code: str, plan_name: str, value: Decimal) -> dict:
    return {
        "contents": [{
            "content_id": plan_code,
            "content_type": "product",
            "content_name": plan_name,
        }],
        "value": float(value),
        "currency": "SAR",
    }


def template_context(
    request,
    events: list[dict] | None = None,
    *,
    purchase_url: str = "",
) -> dict:
    pixel_id = getattr(settings, "TIKTOK_PIXEL_ID", "")
    if not pixel_id:
        return {
            "tiktok_pixel_id": "",
            "tiktok_events": [],
            "tiktok_purchase_url": "",
        }

    queued_events = list(events or [])
    if request.session.pop(REGISTRATION_SESSION_KEY, False):
        queued_events.insert(0, event("CompleteRegistration"))
    return {
        "tiktok_pixel_id": pixel_id,
        "tiktok_events": queued_events,
        "tiktok_purchase_url": purchase_url,
    }
