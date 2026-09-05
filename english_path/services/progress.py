from collections import defaultdict
from datetime import timedelta

from django.utils import timezone
from django.db import transaction

from english_path.models import AssessmentResult, ReviewItem, UnitProgress
from english_path.services.curriculum import LEVELS, SKILLS, all_units, units_for


def status_for(score):
    if score >= 90:
        return UnitProgress.Status.EXCELLENT
    if score >= 80:
        return UnitProgress.Status.MASTERED
    if score >= 60:
        return UnitProgress.Status.DEVELOPING
    return UnitProgress.Status.STARTED


def a1_course_complete(user):
    mastered_codes = set(UnitProgress.objects.filter(user=user, unit_code__startswith="A1.", score__gte=80).values_list("unit_code", flat=True))
    return all(f"A1.{order}" in mastered_codes for order in range(1, 11))


def a2_course_complete(user):
    mastered_codes = set(UnitProgress.objects.filter(user=user, unit_code__startswith="A2.", score__gte=80).values_list("unit_code", flat=True))
    return all(f"A2.{order}" in mastered_codes for order in range(1, 11))


def select_due_review_items(user, limit=10, unit_codes=None):
    """Prioritize repeated errors while capping one subskill at 40% of a session."""
    queryset = ReviewItem.objects.filter(user=user, active=True, next_review_at__lte=timezone.now())
    if unit_codes is not None:
        queryset = queryset.filter(unit_code__in=unit_codes)
    candidates = list(queryset.order_by("-error_count", "next_review_at", "id")[: max(30, limit * 5)])
    cap = max(1, (limit * 2 + 4) // 5)
    selected, counts = [], defaultdict(int)
    for item in candidates:
        if counts[item.subskill] < cap:
            selected.append(item)
            counts[item.subskill] += 1
        if len(selected) == limit:
            break
    return selected


def decorated_units(user, level_slug):
    units = units_for(level_slug)
    progress = {item.unit_code: item for item in UnitProgress.objects.filter(user=user, unit_code__startswith=LEVELS[level_slug]["code"])}
    result = []
    if level_slug == "a2":
        final = AssessmentResult.objects.filter(user=user, assessment_type="a1_final", score__gte=80).first()
        objective_scores = final.skill_scores if final else {}
        previous_mastered = bool(final and all(objective_scores.get(skill, 0) >= 60 for skill in ("vocabulary", "grammar", "reading", "listening")))
    else:
        previous_mastered = True
    for unit in units:
        item = dict(unit)
        record = progress.get(unit["code"])
        item.update({"progress": record, "score": record.score if record else 0, "locked": not previous_mastered})
        result.append(item)
        previous_mastered = bool(record and record.score >= 80)
    return result


def journey_summary(user):
    records = list(UnitProgress.objects.filter(user=user))
    scores = [record.score for record in records]
    mastered = sum(record.score >= 80 for record in records)
    skill_values = defaultdict(list)
    for record in records:
        for skill, value in record.skill_scores.items():
            if skill in SKILLS and isinstance(value, (int, float)):
                skill_values[skill].append(value)
    skills = {skill: round(sum(skill_values[skill]) / len(skill_values[skill])) if skill_values[skill] else 0 for skill in SKILLS}
    return {"mastered": mastered, "total": len(all_units()), "average": round(sum(scores) / len(scores)) if scores else 0, "skills": skills}


def add_review_mistakes(user, unit_code, mistakes):
    now = timezone.now()
    for mistake in mistakes[:10]:
        if not isinstance(mistake, dict):
            continue
        key = str(mistake.get("key", ""))[:80]
        skill = str(mistake.get("skill", "grammar"))
        prompt = str(mistake.get("prompt", ""))[:300]
        answer = str(mistake.get("answer", ""))[:300]
        if not key or not prompt or not answer or skill not in SKILLS:
            continue
        try:
            difficulty = min(5, max(1, int(mistake.get("difficulty", 1))))
        except (TypeError, ValueError):
            difficulty = 1
        item, created = ReviewItem.objects.get_or_create(
            user=user,
            item_key=key,
            defaults={"unit_code": unit_code, "skill": skill, "subskill": str(mistake.get("subskill", "general"))[:64], "difficulty": difficulty, "prompt": prompt, "answer": answer, "active": True, "mastery": 0, "interval_days": 1, "next_review_at": now},
        )
        if not created:
            item.unit_code = unit_code
            item.skill = skill
            item.subskill = str(mistake.get("subskill", item.subskill))[:64]
            item.difficulty = difficulty
            item.prompt = prompt
            item.answer = answer
            item.error_count += 1
            item.active = True
            item.next_review_at = now
            item.save()


def record_unit_result(user, unit_code, score, skills, mistakes=()):
    """Store a verified result while preserving the learner's best score."""
    with transaction.atomic():
        progress, _ = UnitProgress.objects.select_for_update().get_or_create(user=user, unit_code=unit_code)
        progress.score = max(progress.score, score)
        progress.status = status_for(progress.score)
        progress.skill_scores = {**progress.skill_scores, **skills}
        progress.attempts += 1
        progress.completed_at = timezone.now() if progress.score >= 80 else None
        progress.save()
        add_review_mistakes(user, unit_code, mistakes)
    return progress


def schedule_review(item, correct):
    if correct:
        item.mastery = min(5, item.mastery + 1)
        item.interval_days = min(30, max(1, item.interval_days * 2))
        item.active = item.mastery < 5
    else:
        item.mastery = max(0, item.mastery - 1)
        item.interval_days = 1
        item.active = True
    item.next_review_at = timezone.now() + timedelta(days=item.interval_days)
    item.save(update_fields=("mastery", "interval_days", "active", "next_review_at", "updated_at"))
