from datetime import timedelta

from english_path.models import AssessmentResult, ReviewItem, UnitProgress
from english_path.services.curriculum import SKILLS
from english_path.services.progress import journey_summary


def _streak(records):
    dates = sorted({record.last_activity_at.date() for record in records}, reverse=True)
    if not dates:
        return 0
    streak = 1
    for previous, current in zip(dates, dates[1:]):
        if previous - current != timedelta(days=1):
            break
        streak += 1
    return streak


def build_journey_report(user):
    records = list(UnitProgress.objects.filter(user=user).only("unit_code", "score", "skill_scores", "last_activity_at"))
    finals = {}
    for item in AssessmentResult.objects.filter(user=user, assessment_type__in=("a1_final", "a2_final")).order_by("-created_at"):
        finals.setdefault(item.assessment_type, item)
    summary = journey_summary(user)
    skills = summary["skills"]
    ranked = sorted(SKILLS, key=lambda skill: skills.get(skill, 0), reverse=True)
    active_review = ReviewItem.objects.filter(user=user, active=True).count()
    mastered_review = ReviewItem.objects.filter(user=user, active=False).count()
    return {
        "a1_completion": sum(record.unit_code.startswith("A1.") and record.score >= 80 for record in records),
        "a2_completion": sum(record.unit_code.startswith("A2.") and record.score >= 80 for record in records),
        "unit_mastery": summary,
        "a1_final": finals.get("a1_final"), "a2_final": finals.get("a2_final"),
        "skills": skills, "streak": _streak(records),
        "review": {"active": active_review, "mastered": mastered_review},
        "strongest": ranked[:2], "weakest": ranked[-2:],
    }
