import json
from functools import wraps

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Max, Min, Sum
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import salted_hmac
from django.views.decorators.http import require_POST
from phonics.security import rate_limit

from english_path.models import AssessmentResult, ReviewItem, ReviewSession
from english_path.services.a1_final import RUBRICS as A1_FINAL_RUBRICS
from english_path.services.a1_final import grade as grade_a1_final
from english_path.services.a1_final import public_questions as public_a1_final_questions
from english_path.services.a1_phase3 import A1_READINESS_REVIEW
from english_path.services.a2_final import RUBRICS as A2_FINAL_RUBRICS
from english_path.services.a2_final import TASKS as A2_FINAL_TASKS
from english_path.services.a2_final import grade as grade_a2_final
from english_path.services.a2_final import public_questions as public_a2_final_questions
from english_path.services.access import (
    accessible_review_codes,
    can_access_unit,
    decorate_subscription_access,
    has_journey_access,
    has_journey_subscription,
    is_developer_preview_user,
    journey_plan,
)
from english_path.services.curriculum import ASSESSMENT_QUESTIONS, LEVELS, SKILLS, get_unit
from english_path.services.daily_mission import build_daily_mission
from english_path.services.grading import grade_quiz, grade_similar
from english_path.services.journey_report import build_journey_report
from english_path.services.progress import a1_course_complete, a2_course_complete, add_review_mistakes, decorated_units, journey_summary, record_unit_result, schedule_review, select_due_review_items
from english_path.services.unit_schema import public_unit
from english_path.services.units import get_unit_content


def feature_enabled(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not getattr(settings, "ENGLISH_PATH_ENABLED", False):
            raise Http404("English Journey is not available yet.")
        return view(request, *args, **kwargs)
    return wrapped


def _plan_context(user):
    subscribed = has_journey_subscription(user)
    preview_access = is_developer_preview_user(user)
    plan = journey_plan()
    return {
        "journey_subscribed": subscribed,
        "preview_access": preview_access,
        "journey_access": subscribed or preview_access,
        "journey_plan": plan,
        "journey_checkout_url": reverse("checkout", kwargs={"plan_code": plan["code"]}),
    }


def _subscription_error():
    return JsonResponse({"error": "english_journey_subscription_required"}, status=403)


def _educationally_locked(user, unit):
    level_slug = unit["code"][:2].lower()
    return next(item for item in decorated_units(user, level_slug) if item["code"] == unit["code"])["locked"]


def _local_state_scope(user):
    """Return an opaque, user-specific namespace for non-sensitive browser state."""
    return salted_hmac("english_path.a1_local_state", str(user.pk)).hexdigest()[:20]


def _available_a1_units(user):
    plan_context = _plan_context(user)
    return decorate_subscription_access(
        decorated_units(user, "a1"), access_granted=plan_context["journey_access"]
    )


def _a1_neighbors(user, unit_code):
    units = _available_a1_units(user)
    index = next((position for position, item in enumerate(units) if item["code"] == unit_code), None)
    if index is None:
        return None, None

    def available(position):
        if not 0 <= position < len(units):
            return None
        candidate = units[position]
        return None if candidate["locked"] or candidate["subscription_locked"] else candidate

    return available(index - 1), available(index + 1)


def _a1_continue_unit(units):
    available = [item for item in units if not item["locked"] and not item["subscription_locked"]]
    in_progress = [item for item in available if item["progress"] and item["score"] < 80]
    if in_progress:
        return max(in_progress, key=lambda item: item["progress"].last_activity_at)
    return next((item for item in available if item["score"] < 80), available[-1] if available else None)


@feature_enabled
def overview(request):
    return render(request, "english_path/overview.html", {"levels": LEVELS.values(), **_plan_context(request.user)})


@feature_enabled
@login_required
def dashboard(request):
    plan_context = _plan_context(request.user)
    summary = journey_summary(request.user)
    review_codes = accessible_review_codes(request.user, access_granted=plan_context["journey_access"])
    due_reviews = ReviewItem.objects.filter(user=request.user, active=True, next_review_at__lte=timezone.now(), unit_code__in=review_codes).count()
    mission = build_daily_mission(request.user)
    return render(request, "english_path/dashboard.html", {"summary": summary, "due_reviews": due_reviews, "current_unit": mission["current_unit"], "daily_mission": mission, **plan_context})


@feature_enabled
@login_required
def level_detail(request, level_slug):
    level = LEVELS.get(level_slug.lower())
    if not level:
        raise Http404("Unknown level")
    plan_context = _plan_context(request.user)
    units = decorate_subscription_access(decorated_units(request.user, level_slug.lower()), access_granted=plan_context["journey_access"])
    final_unlocked = (level_slug.lower() == "a1" and a1_course_complete(request.user)) or (level_slug.lower() == "a2" and a2_course_complete(request.user))
    a1_context = {}
    if level_slug.lower() == "a1":
        a1_context = {"continue_unit": _a1_continue_unit(units), "local_state_scope": _local_state_scope(request.user), "readiness_review": A1_READINESS_REVIEW}
    return render(request, "english_path/level.html", {"level": level, "units": units, "final_unlocked": final_unlocked, **a1_context, **plan_context})


@feature_enabled
@login_required
def unit_detail(request, unit_slug):
    unit = get_unit(unit_slug)
    if not unit:
        raise Http404("Unknown unit")
    if not can_access_unit(request.user, unit["code"]):
        return redirect("english_path:level", level_slug=unit["code"][:2].lower())
    level_slug = unit["code"][:2].lower()
    decorated = decorated_units(request.user, level_slug)
    selected = next(item for item in decorated if item["code"] == unit["code"])
    if selected["locked"]:
        return redirect("english_path:level", level_slug=level_slug)
    content = get_unit_content(unit_slug)
    if not content:
        return render(request, "english_path/unit.html", {"unit": selected, "level": LEVELS[level_slug], "content": selected, "sentence_tokens": ()})
    safe_content = public_unit(content)
    sentence_tokens = tuple(reversed(content["grammar"]["examples"][0].split()))
    a1_context = {}
    if content["level"] == "A1":
        previous_unit, next_unit = _a1_neighbors(request.user, unit["code"])
        a1_context = {
            "previous_unit": previous_unit,
            "next_unit": next_unit,
            "has_later_unit": content["order"] < len(LEVELS["a1"]["units"]),
            "local_state_scope": _local_state_scope(request.user),
        }
    return render(request, "english_path/unit.html", {"unit": selected, "level": LEVELS[level_slug], "content": safe_content, "sentence_tokens": sentence_tokens, **a1_context})


def _payload(request):
    try:
        return json.loads(request.body or "{}")
    except (TypeError, ValueError):
        return None


@feature_enabled
@login_required
@require_POST
@rate_limit("english-unit-progress", limit_setting="RATE_LIMIT_WRITE", default=60)
def save_unit_progress(request, unit_slug):
    unit = get_unit(unit_slug)
    data = _payload(request)
    if not unit or not isinstance(data, dict):
        return JsonResponse({"error": "invalid_request"}, status=400)
    if not can_access_unit(request.user, unit["code"]):
        return _subscription_error()
    if get_unit_content(unit_slug):
        return JsonResponse({"error": "verified_quiz_required"}, status=400)
    accessible = next(item for item in decorated_units(request.user, unit["code"][:2].lower()) if item["code"] == unit["code"])
    if accessible["locked"]:
        return JsonResponse({"error": "unit_locked"}, status=403)
    try:
        score = int(data.get("score"))
    except (TypeError, ValueError):
        return JsonResponse({"error": "invalid_score"}, status=400)
    if not 0 <= score <= 100:
        return JsonResponse({"error": "invalid_score"}, status=400)
    skills = data.get("skills", {})
    if not isinstance(skills, dict) or any(key not in SKILLS or not isinstance(value, int) or not 0 <= value <= 100 for key, value in skills.items()):
        return JsonResponse({"error": "invalid_skills"}, status=400)
    mistakes = data.get("mistakes", [])
    progress = record_unit_result(request.user, unit["code"], score, skills, mistakes if isinstance(mistakes, list) else ())
    return JsonResponse({"ok": True, "score": progress.score, "status": progress.status, "next": "review" if progress.score < 80 else "continue"})


@feature_enabled
@login_required
@require_POST
@rate_limit("english-unit-quiz", limit_setting="RATE_LIMIT_WRITE", default=60)
def submit_unit_quiz(request, unit_slug):
    unit = get_unit(unit_slug)
    content = get_unit_content(unit_slug)
    data = _payload(request)
    if not unit or not content or not isinstance(data, dict) or not isinstance(data.get("answers"), dict):
        return JsonResponse({"error": "invalid_request"}, status=400)
    if not can_access_unit(request.user, unit["code"]):
        return _subscription_error()
    level_slug = content["level"].lower()
    if next(item for item in decorated_units(request.user, level_slug) if item["code"] == unit["code"])["locked"]:
        return JsonResponse({"error": "unit_locked"}, status=403)
    try:
        result = grade_quiz(content, data["answers"])
    except ValueError:
        return JsonResponse({"error": "invalid_answers"}, status=400)
    progress = record_unit_result(request.user, unit["code"], result["score"], result["skills"], result.pop("mistakes"))
    response = {"ok": True, **result, "best_score": progress.score}
    if content["level"] == "A1" and result["mastered"]:
        _, next_unit = _a1_neighbors(request.user, unit["code"])
        if next_unit:
            response["next_unit"] = {
                "title": next_unit["title"],
                "url": reverse("english_path:unit", args=(next_unit["slug"],)),
            }
    return JsonResponse(response)


@feature_enabled
@login_required
@require_POST
@rate_limit("english-similar-question", limit_setting="RATE_LIMIT_WRITE", default=60)
def check_similar_question(request, unit_slug):
    data = _payload(request)
    unit = get_unit(unit_slug)
    content = get_unit_content(unit_slug)
    if not unit or not content or not isinstance(data, dict):
        return JsonResponse({"error": "invalid_request"}, status=400)
    if not can_access_unit(request.user, unit["code"]):
        return _subscription_error()
    if _educationally_locked(request.user, unit):
        return JsonResponse({"error": "unit_locked"}, status=403)
    try:
        result = grade_similar(content, data.get("question_id"), data.get("answer"))
    except ValueError:
        return JsonResponse({"error": "invalid_request"}, status=400)
    return JsonResponse({"ok": True, **result})


@feature_enabled
@login_required
def review(request):
    review_codes = accessible_review_codes(request.user)
    accessible_items = ReviewItem.objects.filter(user=request.user, active=True, unit_code__in=review_codes)
    session = None
    if request.GET.get("session"):
        session = get_object_or_404(ReviewSession, pk=request.GET["session"], user=request.user)
        items_by_id = {item.id: item for item in accessible_items.filter(id__in=session.item_ids)}
        items = [items_by_id[item_id] for item_id in session.item_ids if item_id in items_by_id]
    else:
        items = list(accessible_items.filter(next_review_at__lte=timezone.now())[:20])
    groups = list(accessible_items.values("skill", "subskill", "unit_code", "difficulty").annotate(items=Count("id"), total_errors=Sum("error_count"), last_seen=Max("last_seen_at"), next_review=Min("next_review_at")).order_by("skill", "subskill"))
    return render(request, "english_path/review.html", {"items": items, "groups": groups, "review_session": session, **_plan_context(request.user)})


@feature_enabled
@login_required
@require_POST
@rate_limit("english-review-session", limit_setting="RATE_LIMIT_WRITE", default=60)
def start_review_session(request):
    ids = [item.id for item in select_due_review_items(request.user, limit=10, unit_codes=accessible_review_codes(request.user))]
    if not ids:
        return redirect("english_path:review")
    session = ReviewSession.objects.create(user=request.user, item_ids=ids)
    return redirect(f"{reverse('english_path:review')}?session={session.pk}")


@feature_enabled
@login_required
@require_POST
@rate_limit("english-review-answer", limit_setting="RATE_LIMIT_WRITE", default=60)
def review_answer(request, item_id):
    item = get_object_or_404(ReviewItem, pk=item_id, user=request.user, active=True)
    if item.unit_code not in accessible_review_codes(request.user):
        return _subscription_error()
    data = _payload(request)
    if not isinstance(data, dict) or not isinstance(data.get("correct"), bool):
        return JsonResponse({"error": "invalid_request"}, status=400)
    schedule_review(item, data["correct"])
    return JsonResponse({"ok": True, "mastery": item.mastery, "active": item.active})


@feature_enabled
@login_required
def assessment(request):
    latest = AssessmentResult.objects.filter(user=request.user).first()
    return render(request, "english_path/assessment.html", {"questions": ASSESSMENT_QUESTIONS, "latest": latest})


@feature_enabled
@login_required
@require_POST
def submit_assessment(request):
    totals = {skill: [0, 0] for skill in SKILLS}
    correct = 0
    for question in ASSESSMENT_QUESTIONS:
        is_correct = request.POST.get(question["id"]) == question["answer"]
        correct += int(is_correct)
        totals[question["skill"]][0] += int(is_correct)
        totals[question["skill"]][1] += 1
    score = round(correct / len(ASSESSMENT_QUESTIONS) * 100)
    skills = {skill: round(got / count * 100) if count else 0 for skill, (got, count) in totals.items()}
    level = "A2" if score >= 80 else "A1" if score >= 40 else "Bridge"
    AssessmentResult.objects.create(user=request.user, score=score, level=level, skill_scores=skills)
    return redirect("english_path:assessment")


@feature_enabled
@login_required
def a1_final_challenge(request):
    if not has_journey_access(request.user):
        return redirect("english_path:level", level_slug="a1")
    if not a1_course_complete(request.user):
        return redirect("english_path:level", level_slug="a1")
    latest = AssessmentResult.objects.filter(user=request.user, assessment_type="a1_final").first()
    weakest = min(latest.skill_scores, key=latest.skill_scores.get) if latest and latest.skill_scores else None
    return render(request, "english_path/a1_final.html", {"questions": public_a1_final_questions(), "rubrics": A1_FINAL_RUBRICS, "latest": latest, "weakest": weakest})


@feature_enabled
@login_required
@require_POST
@rate_limit("english-a1-final", limit_setting="RATE_LIMIT_WRITE", default=60)
def submit_a1_final(request):
    if not has_journey_access(request.user):
        return _subscription_error()
    if not a1_course_complete(request.user):
        return JsonResponse({"error": "a1_units_incomplete"}, status=403)
    answers = {item["id"]: request.POST.get(item["id"], "") for item in public_a1_final_questions()}
    rubric_checks = {skill: set(request.POST.getlist(skill)) for skill in A1_FINAL_RUBRICS}
    try:
        result = grade_a1_final(answers, rubric_checks)
    except ValueError:
        return JsonResponse({"error": "invalid_answers"}, status=400)
    add_review_mistakes(request.user, "A1-FINAL", result.pop("mistakes"))
    AssessmentResult.objects.create(user=request.user, assessment_type="a1_final", level="A1 Master" if result["passed"] else "A1 Developing", score=result["score"], skill_scores=result["skills"])
    return redirect("english_path:a1_final")


def _a2_final_passed(user):
    a1_result = AssessmentResult.objects.filter(user=user, assessment_type="a1_final", score__gte=80).first()
    result = AssessmentResult.objects.filter(user=user, assessment_type="a2_final", score__gte=80).first()
    return bool(a1_result and a2_course_complete(user) and result and all(result.skill_scores.get(skill, 0) >= 60 for skill in ("vocabulary", "grammar", "reading", "listening")))


@feature_enabled
@login_required
def a2_final_challenge(request):
    if not has_journey_access(request.user):
        return redirect("english_path:level", level_slug="a2")
    if not a2_course_complete(request.user):
        return redirect("english_path:level", level_slug="a2")
    latest = AssessmentResult.objects.filter(user=request.user, assessment_type="a2_final").first()
    skills = latest.skill_scores if latest else {}
    return render(request, "english_path/a2_final.html", {"questions": public_a2_final_questions(), "rubrics": A2_FINAL_RUBRICS, "tasks": A2_FINAL_TASKS, "latest": latest, "strong": [skill for skill, score in skills.items() if score >= 80], "developing": [skill for skill, score in skills.items() if 60 <= score < 80], "needs_review": [skill for skill, score in skills.items() if score < 60]})


@feature_enabled
@login_required
@require_POST
@rate_limit("english-a2-final", limit_setting="RATE_LIMIT_WRITE", default=60)
def submit_a2_final(request):
    if not has_journey_access(request.user):
        return _subscription_error()
    if not a2_course_complete(request.user):
        return JsonResponse({"error": "a2_units_incomplete"}, status=403)
    answers = {item["id"]: request.POST.get(item["id"], "") for item in public_a2_final_questions()}
    rubric_checks = {skill: set(request.POST.getlist(skill)) for skill in A2_FINAL_RUBRICS}
    try:
        result = grade_a2_final(answers, rubric_checks)
    except ValueError:
        return JsonResponse({"error": "invalid_answers"}, status=400)
    add_review_mistakes(request.user, "A2-FINAL", result.pop("mistakes"))
    AssessmentResult.objects.create(user=request.user, assessment_type="a2_final", level="A2 Master" if result["passed"] else "A2 Developing", score=result["score"], skill_scores=result["skills"])
    return redirect("english_path:a2_final")


@feature_enabled
@login_required
def journey_completion(request):
    if not has_journey_access(request.user):
        return redirect("english_path:level", level_slug="a2")
    if not _a2_final_passed(request.user):
        return redirect("english_path:level", level_slug="a2")
    return render(request, "english_path/journey_completion.html", {"report": build_journey_report(request.user)})
