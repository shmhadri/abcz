from english_path.services.access import accessible_review_codes, can_access_unit, has_journey_subscription
from english_path.services.curriculum import LEVELS
from english_path.services.progress import decorated_units, journey_summary, select_due_review_items


def build_daily_mission(user):
    """Build tasks only from content the learner currently owns."""
    subscribed = has_journey_subscription(user)
    review_codes = accessible_review_codes(user, subscribed=subscribed)
    due_items = select_due_review_items(user, limit=5, unit_codes=review_codes)
    due = [{"id": item.id, "skill": item.skill, "subskill": item.subskill} for item in due_items]
    summary = journey_summary(user)
    weakest = min(summary["skills"], key=summary["skills"].get) if any(summary["skills"].values()) else "listening"
    current = next((
        unit
        for slug in LEVELS
        for unit in decorated_units(user, slug)
        if not unit["locked"]
        and unit["score"] < 80
        and can_access_unit(user, unit["code"], subscribed=subscribed)
    ), None)
    tasks = [{"kind": "review", "label": f"مراجعة {len(due)} عناصر", "count": len(due)}] if due else []
    if current:
        tasks.extend((
            {"kind": "vocabulary", "label": "3 كلمات من الوحدة الحالية", "count": 3},
            {"kind": weakest, "label": f"تدريب قصير: {weakest.title()}", "count": 1},
            {"kind": "speaking", "label": "Speaking Mission", "count": 1},
            {"kind": "game", "label": "لعبة مهارية", "count": 1},
        ))
    return {
        "minutes": 12,
        "review_item_ids": [item["id"] for item in due],
        "weakest_skill": weakest,
        "current_unit": current,
        "tasks": tasks[:5],
        "subscription_required": not subscribed and current is None,
    }
