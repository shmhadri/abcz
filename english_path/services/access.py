"""Commercial access policy for the single English Journey package."""

from phonics.plans import PLAN_CATALOG, PLAN_ENGLISH_JOURNEY
from phonics.subscriptions import get_user_entitlements

from english_path.services.curriculum import all_units

ENTITLEMENT = "english_journey_a1_a2"
FREE_UNIT_CODES = frozenset({"A1.1"})
FINAL_REVIEW_CODES = frozenset({"A1-FINAL", "A2-FINAL"})


def has_journey_subscription(user, *, now=None):
    if not getattr(user, "is_authenticated", False):
        return False
    return ENTITLEMENT in get_user_entitlements(user, now=now, synchronize=False).entitlements


def can_access_unit(user, unit_code, *, subscribed=None):
    if unit_code in FREE_UNIT_CODES:
        return True
    subscribed = has_journey_subscription(user) if subscribed is None else subscribed
    return subscribed


def accessible_review_codes(user, *, subscribed=None):
    subscribed = has_journey_subscription(user) if subscribed is None else subscribed
    if not subscribed:
        return set(FREE_UNIT_CODES)
    return {unit["code"] for unit in all_units()} | set(FINAL_REVIEW_CODES)


def decorate_subscription_access(units, *, subscribed):
    result = []
    for unit in units:
        item = dict(unit)
        item["subscription_locked"] = not can_access_unit(None, item["code"], subscribed=subscribed)
        result.append(item)
    return result


def journey_plan():
    definition = PLAN_CATALOG[PLAN_ENGLISH_JOURNEY]
    return {"code": definition["code"], "name": definition["name"], "price_sar": definition["price"], "duration_days": definition["duration_days"]}
