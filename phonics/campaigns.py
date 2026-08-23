"""Central, server-side pricing for temporary marketing campaigns."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN

from django.conf import settings

WHOLE_SAR = Decimal("1")
ONE_HUNDRED = Decimal("100")


@dataclass(frozen=True)
class CampaignPrice:
    original_price: Decimal
    final_price: Decimal
    discount_percent: int
    campaign_active: bool
    name: str = "Back to School Offer"
    arabic_name: str = "عرض العودة للمدارس"


def back_to_school_is_active() -> bool:
    return bool(getattr(settings, "BACK_TO_SCHOOL_ENABLED", True))


def back_to_school_discount_percent() -> int:
    value = int(getattr(settings, "BACK_TO_SCHOOL_DISCOUNT_PERCENT", 20))
    return max(0, min(value, 100))


def campaign_price(original_price: Decimal) -> CampaignPrice:
    """Return the only price source used by UI, checkout and payment creation."""
    original = Decimal(original_price).quantize(Decimal("0.01"))
    active = back_to_school_is_active()
    percent = back_to_school_discount_percent()
    final = (
        (original * (ONE_HUNDRED - Decimal(percent)) / ONE_HUNDRED).quantize(
            WHOLE_SAR, rounding=ROUND_DOWN
        )
        if active else original
    )
    return CampaignPrice(original, final, percent, active)


def campaign_context_for_plan(plan) -> dict:
    price = campaign_price(plan["price"] if isinstance(plan, dict) else plan)
    return {
        "original_price": price.original_price,
        "final_price": price.final_price,
        "discount_percent": price.discount_percent,
        "campaign_active": price.campaign_active,
        "name": price.name,
        "arabic_name": price.arabic_name,
    }
