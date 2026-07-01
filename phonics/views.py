"""
Phonics App Views - SECURED & OPTIMIZED (SAFE VERSION)
- Robust JSON parsing
- Strict method constraints
- Safer DB operations
- Avoids `.only()` pitfalls that commonly cause 500 when fields differ
"""

from __future__ import annotations

import json
import time
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import models, transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from xhtml2pdf import pisa

from .forms import StudentProfileForm, StudentRegistrationForm
from .models import (
    Student,
    StudentProfile,
    LetterProgress,
    ExternalGame,
    TopGoalUnit,
    CVCWord,
    CVCSentence,
    CVCStory,
    CVCProgress,
)


# ============================================
# AUTO-SEED FOR RENDER (No Shell Required)
# ============================================

def ensure_seed_data():
    """
    Auto-populate database on first request if empty.
    Works on Render Free tier without shell/pre-deploy access.
    
    This runs ONCE when the first API call is made and database is empty.
    Safe to call multiple times - checks if data exists first.
    """
    # Skip during tests
    if getattr(settings, "DISABLE_AUTO_SEED", False):
        return
    
    # Check if data already exists (fast query)
    try:
        has_words = CVCWord.objects.exists()
        has_sentences = CVCSentence.objects.exists()
        
        # If we have data, no need to seed
        if has_words and has_sentences:
            return
        
        print("🌱 Database is empty. Auto-seeding...")
        
        # Use transaction for safety
        with transaction.atomic():
            # Populate CVC data
            if not has_words or not has_sentences:
                print("📚 Populating CVC data...")
                call_command("populate_all_cvc")
            
            # Populate Top Goal data (optional - won't fail if command doesn't exist)
            try:
                has_topgoal = TopGoalUnit.objects.exists()
                if not has_topgoal:
                    print("🥅 Populating Top Goal data...")
                    call_command("populate_topgoal_unit5")
            except Exception as e:
                print(f"⚠️ Top Goal population skipped: {e}")
        
        print("✅ Auto-seed completed successfully!")
        
    except Exception as e:
        # Log error but don't crash the app
        print(f"❌ Auto-seed failed: {e}")
        # Continue anyway - let the app show "no data" message


# ============================================
# HELPERS
# ============================================

def _json_error(message: str, status: int = 400, **extra):
    payload = {"error": message}
    if extra:
        payload.update(extra)
    return JsonResponse(payload, status=status)


def parse_json_safely(request):
    """
    Parse JSON request body safely.
    Returns (data, error_response)
    """
    try:
        if not request.body:
            return None, _json_error("Empty request body", 400)
        data = json.loads(request.body.decode("utf-8"))
        if not isinstance(data, dict):
            return None, _json_error("JSON must be an object", 400)
        return data, None
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return None, _json_error("Invalid JSON format", 400, details=str(e))
    except Exception as e:
        return None, _json_error("Failed to parse request", 400, details=str(e))


def get_or_create_student_profile(user):
    if not user.is_authenticated:
        return None

    profile, _ = StudentProfile.objects.get_or_create(
        user=user,
        defaults={
            "student_name": user.get_full_name() or user.username,
            "school": "",
            "parent_phone": "",
        },
    )
    return profile


def serialize_student_profile(profile):
    if not profile:
        return {
            "student_name": "",
            "school": "",
            "parent_phone": "",
            "is_premium": False,
        }

    return {
        "student_name": profile.student_name,
        "school": profile.school,
        "parent_phone": profile.parent_phone,
        "is_premium": profile.is_premium,
    }


def get_existing_bird_lottie_files():
    animation_dir = settings.BASE_DIR / "static" / "animations" / "bird"
    expected_files = {
        "idle": "bird_idle.json",
        "talking": "bird_talk.json",
        "happy": "bird_happy.json",
        "wrong": "bird_wrong.json",
        "thinking": "bird_thinking.json",
    }

    return {
        state: f"/static/animations/bird/{filename}"
        for state, filename in expected_files.items()
        if (animation_dir / filename).exists()
    }


def validate_int(value, *, min_val: int, max_val: int, field_name="value"):
    """
    Validate and convert value to int within range.
    Returns (int_value, error_response)
    """
    try:
        iv = int(value)
        if not (min_val <= iv <= max_val):
            return None, _json_error(
                f"{field_name} must be between {min_val} and {max_val}",
                400
            )
        return iv, None
    except (ValueError, TypeError):
        return None, _json_error(f"Invalid {field_name}. Must be an integer.", 400)


def validate_letter(letter):
    if not (isinstance(letter, str) and len(letter) == 1 and letter.isalpha()):
        return None, _json_error("Letter must be a single alphabetic character", 400)
    return letter.upper(), None


# ============================================
# LETTER PROGRESS (CSRF Protected)
# ============================================

@require_POST
def save_progress(request):
    """
    Expected JSON: {student, letter, score}
    score is 0..20
    """
    data, error = parse_json_safely(request)
    if error:
        return error

    student_name = (data.get("student") or "").strip()
    letter_raw = data.get("letter")
    score_raw = data.get("score")

    if not student_name or letter_raw is None or score_raw is None:
        return _json_error("Missing required fields: student, letter, score", 400)

    letter, error = validate_letter(letter_raw)
    if error:
        return error

    score, error = validate_int(score_raw, min_val=0, max_val=20, field_name="score")
    if error:
        return error

    try:
        with transaction.atomic():
            student, _ = Student.objects.get_or_create(name=student_name)

            # enforce previous letter completion
            if letter != "A":
                prev_letter = chr(ord(letter) - 1)
                prev_passed = LetterProgress.objects.filter(
                    student=student,
                    letter=prev_letter,
                    passed=True
                ).exists()
                if not prev_passed:
                    return JsonResponse({
                        "error": "previous_letter_not_passed",
                        "message": f"Please complete letter {prev_letter} first",
                        "required_letter": prev_letter
                    }, status=400)

            lp, created = LetterProgress.objects.get_or_create(
                student=student,
                letter=letter,
                defaults={"score": 0, "passed": False},
            )

            # only update if improved
            if score > (lp.score or 0):
                lp.score = score

            if score >= 14:
                lp.passed = True

            lp.save(update_fields=["score", "passed"])

        return JsonResponse({
            "status": "ok",
            "passed": lp.passed,
            "score": lp.score,
            "created": created
        })

    except Exception as e:
        return _json_error("Database error", 500, details=str(e))


# هذا endpoint خارجي (لاحقًا حطي API KEY)
@csrf_exempt
@require_POST
def speech_check(request):
    try:
        letter = (request.POST.get("letter") or "").strip()
        if not letter:
            return _json_error("Letter parameter required", 400)

        recognized = letter.upper()
        return JsonResponse({
            "recognized": recognized,
            "accuracy": 100,
            "correct": True,
            "message": "Speech recognition will be implemented soon"
        })
    except Exception as e:
        return _json_error("Speech check failed", 500, details=str(e))


@require_GET
def generate_certificate(request, student_id):
    """
    PDF certificate if completed A-Z
    """
    try:
        student = get_object_or_404(Student, id=student_id)

        passed_count = LetterProgress.objects.filter(student=student, passed=True).count()
        if passed_count < 26:
            return JsonResponse({
                "error": "Certificate not available",
                "message": f"Complete all 26 letters first. Progress: {passed_count}/26",
                "progress": passed_count,
                "required": 26
            }, status=400)

        template = get_template("phonics/certificate_template.html")
        total_score = (LetterProgress.objects.filter(student=student)
                       .aggregate(models.Sum("score"))["score__sum"]) or 0

        html = template.render({
            "name": student.name,
            "date": datetime.now().date(),
            "total_score": total_score,
        })

        response = HttpResponse(content_type="application/pdf")
        # إذا ما تبين تحميل مباشر، شيلي Content-Disposition
        response["Content-Disposition"] = f'attachment; filename="certificate_{student.name}.pdf"'

        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return _json_error("PDF generation failed", 500)

        return response

    except Exception as e:
        return _json_error("Certificate generation failed", 500, details=str(e))


# ============================================
# GENERAL PAGES
# ============================================


@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return redirect("index")

    form = StudentRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        auth_login(request, user)
        messages.success(request, "تم إنشاء الحساب بنجاح.")
        return redirect("index")

    return render(request, "accounts/register.html", {"form": form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("index")

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        auth_login(request, form.get_user())
        messages.success(request, "تم تسجيل الدخول بنجاح.")
        return redirect(request.GET.get("next") or "index")

    return render(request, "accounts/login.html", {"form": form})


@require_GET
def logout_view(request):
    auth_logout(request)
    messages.success(request, "تم تسجيل الخروج.")
    return redirect("index")


@login_required
@require_http_methods(["GET", "POST"])
def profile_api(request):
    profile = get_or_create_student_profile(request.user)

    if request.method == "GET":
        return JsonResponse({"profile": serialize_student_profile(profile)})

    data, error = parse_json_safely(request)
    if error:
        return error

    form = StudentProfileForm(data, instance=profile)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors}, status=400)

    profile = form.save()
    return JsonResponse({"status": "ok", "profile": serialize_student_profile(profile)})


@ensure_csrf_cookie
@require_GET
def index(request):
    profile = get_or_create_student_profile(request.user)
    profile_payload = serialize_student_profile(profile)

    return render(request, "letters.html", {
        "is_authenticated": request.user.is_authenticated,
        "is_premium_user": profile.is_premium if profile else False,
        "phonics_user_id": str(request.user.id) if request.user.is_authenticated else "",
        "phonics_user_email": request.user.email if request.user.is_authenticated else "",
        "student_profile_json": json.dumps(profile_payload, ensure_ascii=False),
        "bird_lottie_files_json": json.dumps(get_existing_bird_lottie_files(), ensure_ascii=False),
    })


@require_GET
def pricing(request):
    return render(request, "pricing.html")


@require_GET
def leaderboard(request):
    try:
        students = (
            Student.objects.annotate(
                total=models.Sum("progress_entries__score", default=0),
                passed_letters=models.Count(
                    "progress_entries",
                    filter=models.Q(progress_entries__passed=True),
                    distinct=True,
                ),
                class_name=models.Value("", output_field=models.CharField()),
                school_name=models.F("school"),
            )
            .filter(progress_entries__isnull=False)
            .order_by("-total")[:50]
        )
        return render(request, "phonics/leaderboard.html", {"rows": students})
    except Exception:
        return render(request, "phonics/leaderboard.html", {"rows": [], "error": "Failed to load leaderboard"})


@require_GET
def letter_data_api(request, letter):
    # Not implemented (models missing)
    return JsonResponse({
        "error": "not_implemented",
        "message": "Word and QuizQuestion models need to be created first",
        "letter": str(letter).upper()
    }, status=501)


@require_GET
def external_games_by_letter(request, letter):
    letter, error = validate_letter(letter)
    if error:
        return error

    games = ExternalGame.objects.filter(
        letter=letter,
        is_active=True,
        review_status=ExternalGame.REVIEW_APPROVED,
    ).order_by("title")

    return render(request, "phonics/external_games.html", {
        "letter": letter,
        "games": games,
    })


# ============================================
# CVC PAGES & APIs
# ============================================

@require_GET
def cvc_reading_view(request):
    return render(request, "phonics/cvc_reading.html")

def grade_2_unit_1_view(request):
    return render(request, 'phonics/grade_2_unit_1.html')

def grade_3_unit_1_view(request):
    return render(request, 'phonics/grade_3_unit_1.html')

def grade_4_unit_1_view(request):
    return render(request, 'phonics/grade_4_unit_1.html')


@require_GET
def get_cvc_words_api(request):
    """
    Returns JSON words.
    IMPORTANT: Avoid `.only()` to prevent 500 if fields differ from expectations.
    """
    # Auto-seed if database is empty (Render Free tier solution)
    ensure_seed_data()
    
    try:
        qs = CVCWord.objects.all()
        # إذا عندك حقل order رتب، وإلا تجاهله
        if "order" in [f.name for f in CVCWord._meta.get_fields()]:
            qs = qs.order_by("order")
        else:
            qs = qs.order_by("id")

        words = []
        for w in qs:
            words.append({
                "id": w.id,
                "word": getattr(w, "word", ""),
                "arabic_meaning": getattr(w, "arabic_meaning", "") or getattr(w, "meaning_ar", ""),
                "image_url": getattr(w, "image_url", "") or getattr(w, "image", ""),
                "emoji": getattr(w, "emoji", ""),
                "category": getattr(w, "category", ""),
                "word_family": getattr(w, "word_family", ""),
                "vowel_sound": getattr(w, "vowel_sound", ""),
                "difficulty_level": getattr(w, "difficulty_level", None) or getattr(w, "difficulty", None),
            })

        return JsonResponse({"words": words, "count": len(words)})

    except Exception as e:
        # هذا يفيدك لمعرفة سبب 500 بالضبط من Render logs
        return _json_error("Failed to fetch CVC words", 500, details=str(e))


@require_GET
def get_cvc_sentences_api(request):
    # Auto-seed if database is empty
    ensure_seed_data()
    
    try:
        qs = CVCSentence.objects.all()
        if "order" in [f.name for f in CVCSentence._meta.get_fields()]:
            qs = qs.order_by("order")
        else:
            qs = qs.order_by("id")

        sentences = []
        for s in qs:
            sentences.append({
                "id": s.id,
                "sentence": getattr(s, "sentence", "") or getattr(s, "text", ""),
                "arabic_translation": getattr(s, "arabic_translation", "") or getattr(s, "translation_ar", ""),
                "difficulty": getattr(s, "difficulty", None),
                "time_limit": getattr(s, "time_limit", None),
                "category": getattr(s, "category", ""),
                "quiz_data": getattr(s, "quiz_data", None),
                "emoji": getattr(s, "emoji", ""),
            })

        return JsonResponse({"sentences": sentences, "count": len(sentences)})

    except Exception as e:
        return _json_error("Failed to fetch CVC sentences", 500, details=str(e))


@require_GET
def get_cvc_stories_api(request):
    # Auto-seed if database is empty
    ensure_seed_data()
    
    try:
        qs = CVCStory.objects.all()
        if "order" in [f.name for f in CVCStory._meta.get_fields()]:
            qs = qs.order_by("order")
        else:
            qs = qs.order_by("id")

        stories = []
        for s in qs:
            stories.append({
                "id": s.id,
                "title": getattr(s, "title", ""),
                "content": getattr(s, "content", "") or getattr(s, "story", ""),
                "arabic_explanation": getattr(s, "arabic_explanation", "") or getattr(s, "explanation_ar", ""),
                "image_url": getattr(s, "image_url", "") or getattr(s, "image", ""),
                "quiz_data": getattr(s, "quiz_data", None),
                "difficulty": getattr(s, "difficulty", None),
            })

        return JsonResponse({"stories": stories, "count": len(stories)})

    except Exception as e:
        return _json_error("Failed to fetch CVC stories", 500, details=str(e))


@require_POST
def save_cvc_progress_api(request):
    data, error = parse_json_safely(request)
    if error:
        return error

    student_name = (data.get("student") or "").strip()
    progress_type = (data.get("type") or "").strip()
    points_raw = data.get("points", 0)

    if not student_name or not progress_type:
        return _json_error("Missing required fields: student, type", 400)

    valid_types = {"word", "sentence", "story"}
    if progress_type not in valid_types:
        return _json_error(f"Invalid type. Must be one of: {sorted(valid_types)}", 400)

    points, error = validate_int(points_raw, min_val=0, max_val=1000, field_name="points")
    if error:
        return error

    try:
        with transaction.atomic():
            student, _ = Student.objects.get_or_create(name=student_name)
            cvc_progress, created = CVCProgress.objects.get_or_create(student=student)

            if progress_type == "word":
                cvc_progress.update_word_score(points)

            elif progress_type == "sentence":
                reading_time = data.get("reading_time", 0)
                try:
                    reading_time = float(reading_time or 0)
                except (ValueError, TypeError):
                    return _json_error("Invalid reading_time format. Must be a number.", 400)
                cvc_progress.update_sentence_score(points, reading_time)

            elif progress_type == "story":
                cvc_progress.mark_story_complete()

        return JsonResponse({
            "status": "ok",
            "total_score": cvc_progress.total_score,
            "words_completed": cvc_progress.words_completed,
            "sentences_completed": cvc_progress.sentences_completed,
            "stories_completed": cvc_progress.stories_completed,
            "created": created
        })

    except Exception as e:
        return _json_error("Failed to save progress", 500, details=str(e))


@csrf_exempt
@require_POST
def check_cvc_pronunciation(request):
    try:
        target_word = (request.POST.get("word") or "").strip().upper()
        if not target_word:
            return _json_error("Word parameter required", 400)

        # mock response
        accuracy = 85
        return JsonResponse({
            "word": target_word,
            "accuracy": accuracy,
            "correct": True,
            "message": "رائع! نطق ممتاز" if accuracy >= 80 else "جيد، حاول مرة أخرى"
        })

    except Exception as e:
        return _json_error("Pronunciation check failed", 500, details=str(e))


# ============================================
# TOP GOAL
# ============================================

@require_GET
def top_goal_view(request):
    """
    Top Goal 6 Unit 1 - Robust version
    """
    try:
        # Don't require data to exist
        unit = None
        vocab = []
        sentences = []
        quizzes_json = "[]"
        
        try:
            ensure_seed_data()
            unit = TopGoalUnit.objects.filter(grade="Top Goal 6").prefetch_related("vocabularies", "sentences", "quizzes").first()
            
            if unit:
                vocab = list(unit.vocabularies.all().order_by("order")) if hasattr(unit, 'vocabularies') else []
                sentences = list(unit.sentences.all().order_by("order")) if hasattr(unit, 'sentences') else []
                quizzes = list(unit.quizzes.all().order_by("order")) if hasattr(unit, 'quizzes') else []
                
                quizzes_json = json.dumps([
                    {"id": q.id, "question": getattr(q, "question_text", ""), "options": getattr(q, "options", []), 
                     "correct": getattr(q, "correct_answer", ""), "explanation": getattr(q, "explanation_ar", "")}
                    for q in quizzes
                ], ensure_ascii=False)
        except:
            pass  # Continue with empty data
        
        return render(request, "phonics/top_goal_6_unit_1.html", {
            "unit": unit, "vocab": vocab, "sentences": sentences, "quizzes_json": quizzes_json,
            "timestamp": int(time.time())
        })
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return render(request, "phonics/top_goal_6_unit_1.html", {"vocab": [], "sentences": [], "quizzes_json": "[]", "timestamp": int(time.time())})

