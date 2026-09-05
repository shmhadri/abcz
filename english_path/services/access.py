"""Commercial access policy for the single English Journey package."""

from phonics.plans import PLAN_CATALOG, PLAN_ENGLISH_JOURNEY
from phonics.subscriptions import get_user_entitlements

from english_path.services.curriculum import all_units

ENTITLEMENT = "english_journey_a1_a2"
FREE_UNIT_CODES = frozenset({"A1.1"})
FINAL_REVIEW_CODES = frozenset({"A1-FINAL", "A2-FINAL"})
DEVELOPER_PREVIEW_GROUP = "English Journey Preview"


def is_developer_preview_user(user):
    if not getattr(user, "is_authenticated", False) or not getattr(user, "is_active", False):
        return False
    return user.groups.filter(name=DEVELOPER_PREVIEW_GROUP).exists()


def has_journey_subscription(user, *, now=None):
    if not getattr(user, "is_authenticated", False):
        return False
    return ENTITLEMENT in get_user_entitlements(user, now=now, synchronize=False).entitlements


def has_journey_access(user, *, now=None):
    return is_developer_preview_user(user) or has_journey_subscription(user, now=now)


def can_access_unit(user, unit_code, *, access_granted=None):
    if unit_code in FREE_UNIT_CODES:
        return True
    access_granted = has_journey_access(user) if access_granted is None else access_granted
    return access_granted


def accessible_review_codes(user, *, access_granted=None):
    access_granted = has_journey_access(user) if access_granted is None else access_granted
    if not access_granted:
        return set(FREE_UNIT_CODES)
    return {unit["code"] for unit in all_units()} | set(FINAL_REVIEW_CODES)


def decorate_subscription_access(units, *, access_granted):
    result = []
    for unit in units:
        item = dict(unit)
        item["subscription_locked"] = not can_access_unit(None, item["code"], access_granted=access_granted)
        result.append(item)
    return result


def journey_plan():
    definition = PLAN_CATALOG[PLAN_ENGLISH_JOURNEY]
    return {"code": definition["code"], "name": definition["name"], "price_sar": definition["price"], "duration_days": definition["duration_days"]}
