"""
Phonics App Views - SECURED & OPTIMIZED (SAFE VERSION)
- Robust JSON parsing
- Strict method constraints
- Safer DB operations
- Avoids `.only()` pitfalls that commonly cause 500 when fields differ
"""

from __future__ import annotations

import json
import hashlib
import logging
import math
import re
import uuid
import secrets
from functools import lru_cache
from io import BytesIO
from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.management import call_command
from django.db import IntegrityError, models, transaction
from django.db.models import Count, F, Max, Q, Sum
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone
from django.views.decorators.cache import cache_page, never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from xhtml2pdf import pisa

from .forms import SecureAuthenticationForm, StudentProfileForm, StudentRegistrationForm
from .models import (
    Student,
    StudentProfile,
    BirdTutorProgress,
    BirdReviewItem,
    SoundPracticeProgress,
    LetterProgress,
    ExternalGame,
    CVCWord,
    CVCSentence,
    CVCStory,
    CVCProgress,
    CVCReadingProgress,
    EnglishFoundationProgress,
    UserSubscription,
    PaymentOrder,
    PaymentWebhookEvent,
    BankTransferProof,
    activate_subscription_from_payment,
)
from .cache_helpers import (
    get_cached_static_value,
    safe_cache_get,
    safe_cache_set,
)
from .middleware import get_current_request
from .security import client_ip, login_identity, rate_limit
from .payments.moyasar import (
    MoyasarAPIError,
    MoyasarConfigurationError,
    MoyasarInvalidResponseError,
    MoyasarNetworkError,
    create_invoice as create_moyasar_invoice,
    validate_checkout_url as validate_moyasar_checkout_url,
)
from .payments.reconciliation import reconcile_payment_order
from .plans import (
    BASIC_FEATURE_KEYS,
    FEATURE_KEYS_BY_PLAN,
    FULL_ACCESS_FEATURE_KEYS,
    FULL_ACCESS_ONLY_FEATURE_KEYS,
    LEVEL_FOUR_FEATURE_KEYS,
    LEVEL_THREE_FEATURE_KEYS,
    PLAN_BASIC,
    PLAN_CATALOG,
    PLAN_DIAMOND,
    PLAN_FREE,
    PLAN_FULL_ACCESS,
    PLAN_LEVEL_FOUR,
    PLAN_LEVEL_THREE,
    PLAN_SILVER,
    PLAN_VIP,
    SILVER_FEATURE_KEYS,
    VIP_FEATURE_KEYS,
    normalize_plan_code,
)
from .subscriptions import (
    PurchaseNotAllowed,
    get_user_entitlements,
    purchase_options_for_user,
    quote_plan_purchase,
    subscription_dashboard_context,
    synchronize_user_subscription_compatibility,
)


PUBLIC_PAGE_CACHE_TIMEOUT = getattr(settings, "PUBLIC_PAGE_CACHE_TIMEOUT", 600)
logger = logging.getLogger("abcz.performance")
payment_logger = logging.getLogger("abcz.payments.moyasar")

LEADERBOARD_CACHE_TIMEOUT = 60
LEADERBOARD_LIMIT = 100
CVC_API_DEFAULT_PAGE_SIZE = 100
CVC_API_MAX_PAGE_SIZE = 100
CVC_WORKSHEET_WORD_LIMIT = 120
CVC_WORKSHEET_SENTENCE_LIMIT = 20
CVC_WORKSHEET_STORY_LIMIT = 20
CVC_CONTENT_CACHE_VERSION = "v1"
CVC_COUNT_CACHE_TIMEOUT = 300
CVC_SEED_CHECK_CACHE_TIMEOUT = 300


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

    seed_cache_key = f"cvc-seed-ready:{CVC_CONTENT_CACHE_VERSION}"
    if safe_cache_get(seed_cache_key) is True:
        return

    # Check if data already exists (fast query)
    try:
        has_words = CVCWord.objects.exists()
        has_sentences = CVCSentence.objects.exists()

        # If we have data, no need to seed
        if has_words and has_sentences:
            safe_cache_set(seed_cache_key, True, timeout=CVC_SEED_CHECK_CACHE_TIMEOUT)
            return

        print("🌱 Database is empty. Auto-seeding...")

        # Use transaction for safety
        with transaction.atomic():
            # Populate CVC data
            if not has_words or not has_sentences:
                print("📚 Populating CVC data...")
                call_command("populate_all_cvc")
                safe_cache_set(seed_cache_key, True, timeout=CVC_SEED_CHECK_CACHE_TIMEOUT)


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


@require_GET
def health(request):
    return JsonResponse({
        "status": "ok",
        "release": "startup-migrations-20260710",
    })


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
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, _json_error("Invalid JSON format", 400)
    except Exception:
        logger.exception("request_json_parse_failed request_id=%s", getattr(request, "request_id", ""))
        return None, _json_error("Failed to parse request", 400, request_id=getattr(request, "request_id", ""))


def get_request_feature_cache(user):
    if not getattr(user, "is_authenticated", False):
        return None

    request = get_current_request()
    if request is None:
        return None

    request_user = getattr(request, "user", None)
    if not getattr(request_user, "is_authenticated", False):
        return None
    if getattr(request_user, "pk", None) != getattr(user, "pk", None):
        return None

    cache = getattr(request, "_subscription_feature_cache", None)
    if cache is None:
        cache = {}
        request._subscription_feature_cache = cache
    return cache


def get_or_create_student_profile(user):
    if not user.is_authenticated:
        return None

    cache = get_request_feature_cache(user)
    if cache is not None and "student_profile" in cache:
        return cache["student_profile"]

    profile, _ = StudentProfile.objects.get_or_create(
        user=user,
        defaults={
            "display_name": user.get_full_name() or user.username,
            "student_name": user.get_full_name() or user.username,
            "school": "",
            "parent_phone": "",
        },
    )
    if cache is not None:
        cache["student_profile"] = profile
    return profile


def serialize_student_profile(profile):
    if not profile:
        return {
            "display_name": "",
            "student_name": "",
            "city": "",
            "grade": "",
            "school": "",
            "parent_phone": "",
            "is_premium": False,
            "is_vip": False,
        }

    return {
        "display_name": profile.display_name,
        "student_name": profile.student_name,
        "city": profile.city,
        "grade": profile.grade,
        "school": profile.school,
        "parent_phone": profile.parent_phone,
        "is_premium": profile.is_premium,
        "is_vip": profile.is_vip,
    }


FREE_LEVEL_ONE_LETTERS = {"A", "B"}

CHECKOUT_PLANS = {
    PLAN_BASIC: {
        "code": PLAN_BASIC,
        "name": "Basic",
        "name_ar": "Basic",
        "price_sar": PLAN_CATALOG[PLAN_BASIC]["price"],
        "duration_days": PLAN_CATALOG[PLAN_BASIC]["duration_days"],
        "description": "المستوى الأول: الحروف الإنجليزية A-Z مع الألعاب الداخلية والتقدم وشهادة المستوى الأول حسب الإنجاز.",
        "features": [
            "المستوى الأول: الحروف الإنجليزية A-Z.",
            "ألعاب الموقع الداخلية.",
            "متابعة تقدم المتعلم.",
            "تقرير الإنجاز.",
            "شهادة المستوى الأول حسب الإنجاز.",
        ],
        "start_url": "/",
    },
    PLAN_SILVER: {
        "code": PLAN_SILVER,
        "name": "Silver",
        "name_ar": "Silver",
        "price_sar": PLAN_CATALOG[PLAN_SILVER]["price"],
        "duration_days": PLAN_CATALOG[PLAN_SILVER]["duration_days"],
        "description": "الحروف والصوتيات والنطق مع أوراق عمل قابلة للطباعة والتحميل.",
        "features": [
            "كل مزايا Basic.",
            "المستوى الأول: الحروف الإنجليزية A-Z.",
            "المستوى الثاني: الصوتيات والنطق.",
            "تدريبات المايك.",
            "أوراق العمل.",
            "طباعة أوراق العمل.",
            "تحميل أوراق العمل PDF.",
        ],
        "start_url": "/sounds/",
    },
    PLAN_VIP: {
        "code": PLAN_VIP,
        "name": "VIP",
        "name_ar": "VIP",
        "price_sar": PLAN_CATALOG[PLAN_VIP]["price"],
        "duration_days": PLAN_CATALOG[PLAN_VIP]["duration_days"],
        "description": "الحروف والصوتيات مع الكتاب الكامل وWordwall والعصفور الذكي والتقارير المتقدمة.",
        "features": [
            "كل مزايا Silver.",
            "تحميل الكتاب الكامل PDF.",
            "Wordwall.",
            "العصفور الذكي.",
            "تقرير ولي أمر مفصل.",
            "الشهادة الذهبية حسب الإنجاز.",
        ],
        "start_url": "/",
    },
    PLAN_DIAMOND: {
        "code": PLAN_DIAMOND,
        "name": "Diamond",
        "name_ar": "الماسي",
        "price_sar": PLAN_CATALOG[PLAN_DIAMOND]["price"],
        "duration_days": PLAN_CATALOG[PLAN_DIAMOND]["duration_days"],
        "description": "اشتراك واحد يفتح كل الموقع وجميع المستويات والميزات الحالية.",
        "features": [
            "كل مزايا VIP.",
            "المستوى الثالث: قراءة CVC.",
            "المستوى الرابع كاملًا.",
            "كل أوراق العمل والطباعة والتحميل.",
            "كل الألعاب والتقارير والشهادات المتاحة.",
        ],
        "start_url": "/levels/",
    },
    PLAN_LEVEL_THREE: {
        "code": PLAN_LEVEL_THREE,
        "name": "Level 3",
        "name_ar": "المستوى الثالث",
        "price_sar": PLAN_CATALOG[PLAN_LEVEL_THREE]["price"],
        "duration_days": PLAN_CATALOG[PLAN_LEVEL_THREE]["duration_days"],
        "description": "قراءة CVC، عائلات الكلمات، الجمل، القصص القصيرة، وأوراق العمل الخاصة بالمستوى الثالث.",
        "features": [
            "CVC Words.",
            "Word Families.",
            "Sentences and Stories.",
            "CVC Worksheets.",
            "CVC Certificate حسب الإنجاز.",
        ],
        "start_url": "/cvc-reading/",
    },
    PLAN_LEVEL_FOUR: {
        "code": PLAN_LEVEL_FOUR,
        "name": "Level 4",
        "name_ar": "المستوى الرابع",
        "price_sar": PLAN_CATALOG[PLAN_LEVEL_FOUR]["price"],
        "duration_days": PLAN_CATALOG[PLAN_LEVEL_FOUR]["duration_days"],
        "description": "قراءة واستماع وتحدث وكتابة وجمل شائعة ومحادثات ضمن المستوى الرابع.",
        "features": [
            "Reading.",
            "Listening.",
            "Speaking.",
            "Writing.",
            "Common Sentences and Conversations.",
            "Level Four Certificate حسب الإنجاز.",
        ],
        "start_url": "/level-four/",
    },
}

UPGRADE_VIP_OR_FULL_MESSAGE = "هذه الميزة متاحة في VIP أو الباقة الماسية."
UPGRADE_FULL_ACCESS_MESSAGE = "هذه الميزة متاحة في الباقة الماسية."
UPGRADE_SILVER_OR_HIGHER_MESSAGE = "هذه الميزة متاحة في Silver أو باقة أعلى."
UPGRADE_LEVEL_THREE_MESSAGE = "هذه الميزة متاحة في اشتراك المستوى الثالث أو الباقة الماسية."
UPGRADE_LEVEL_FOUR_MESSAGE = "هذه الميزة متاحة في اشتراك المستوى الرابع أو الباقة الماسية."


def upgrade_message_for_feature(feature_key, fallback_message):
    if feature_key in FULL_ACCESS_ONLY_FEATURE_KEYS:
        return UPGRADE_FULL_ACCESS_MESSAGE
    return fallback_message


def get_active_subscription_plan_codes(user):
    if not user.is_authenticated:
        return set()

    cache = get_request_feature_cache(user)
    if cache is not None and "active_plan_codes" in cache:
        return cache["active_plan_codes"]

    active_plan_codes = set(get_user_entitlements(user).plan_codes)
    if cache is not None:
        cache["active_plan_codes"] = active_plan_codes
    return active_plan_codes


def get_subscription_plan(user):
    if not user.is_authenticated:
        return PLAN_FREE

    cache = get_request_feature_cache(user)
    if cache is not None and "subscription_plan" in cache:
        return cache["subscription_plan"]

    snapshot = get_user_entitlements(user)
    plan = snapshot.main_subscription.plan_code if snapshot.main_subscription else PLAN_FREE
    if cache is not None:
        cache["subscription_plan"] = plan
    return plan


def get_feature_keys(user):
    cache = get_request_feature_cache(user)
    if cache is not None and "feature_keys" in cache:
        return cache["feature_keys"]

    feature_keys = set(get_user_entitlements(user).entitlements)
    if cache is not None:
        cache["feature_keys"] = feature_keys
    return feature_keys


def has_feature(user, feature_key):
    return feature_key in get_feature_keys(user)


def feature_unavailable_response(request, message, *, feature_key="feature_unavailable"):
    if request.path.startswith("/api/") or "application/json" in request.headers.get("Accept", ""):
        return JsonResponse({
            "error": "feature_unavailable",
            "feature": feature_key,
            "message": message,
        }, status=403)

    html = f"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>الترقية مطلوبة</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ margin: 0; min-height: 100vh; display: grid; place-items: center; font-family: Tahoma, Arial, sans-serif; background: #f8fafc; color: #172033; }}
        main {{ width: min(560px, calc(100% - 32px)); background: #fff; border: 1px solid #dbe3ef; border-radius: 8px; padding: 28px; box-shadow: 0 18px 45px rgba(15, 23, 42, 0.1); text-align: center; }}
        h1 {{ margin: 0 0 12px; font-size: 1.6rem; }}
        p {{ margin: 0 0 22px; color: #526173; font-weight: 700; }}
        a {{ display: inline-flex; align-items: center; justify-content: center; min-height: 44px; padding: 0 18px; border-radius: 8px; background: #4361ee; color: #fff; text-decoration: none; font-weight: 900; }}
    </style>
</head>
<body>
    <main>
        <h1>هذه الميزة تحتاج ترقية</h1>
        <p>{message}</p>
        <a href="/pricing/">عرض الباقات</a>
    </main>
</body>
</html>"""
    return HttpResponse(html, status=403)


def require_feature(request, feature_key, message):
    if has_feature(request.user, feature_key):
        return None
    return feature_unavailable_response(
        request,
        upgrade_message_for_feature(feature_key, message),
        feature_key=feature_key,
    )


def deny_current_plan_without_feature(request, feature_key, message, *, plans=None):
    plan = get_subscription_plan(request.user)
    protected_plans = set(plans or {PLAN_BASIC, PLAN_SILVER, PLAN_VIP})
    if plan in protected_plans and not has_feature(request.user, feature_key):
        return feature_unavailable_response(
            request,
            upgrade_message_for_feature(feature_key, message),
            feature_key=feature_key,
        )
    return None


def level_one_disabled_features(user):
    return {
        "wordwall": not has_feature(user, "wordwall_level1"),
        "letterWorksheets": not has_feature(user, "worksheets_level1"),
        "worksheetBook": not has_feature(user, "book_download_level1"),
        "leaderboard": not has_feature(user, "leaderboard"),
        "smartBird": not has_feature(user, "bird_tutor"),
        "parentReport": not has_feature(user, "basic_parent_report"),
        "certificate": not has_feature(user, "letter_certificate_basic"),
    }


def is_level_one_basic_user(user):
    return has_feature(user, "letters_full")


def level_one_feature_unavailable_response():
    return HttpResponse("هذه الميزة غير متاحة في باقتك الحالية. يرجى الترقية من صفحة الأسعار.", status=403)


PLACEMENT_TEST_QUESTIONS = [
    {
        "id": "letters_1",
        "section": "letters",
        "section_label": "الحروف",
        "question": "ما اسم هذا الحرف؟",
        "prompt": "B",
        "options": ["A", "B", "D", "P"],
        "answer": "B",
    },
    {
        "id": "letters_2",
        "section": "letters",
        "section_label": "الحروف",
        "question": "اختر الحرف الكبير المطابق للحرف الصغير.",
        "prompt": "m",
        "options": ["N", "M", "W", "H"],
        "answer": "M",
    },
    {
        "id": "letters_3",
        "section": "letters",
        "section_label": "الحروف",
        "question": "أي حرف يأتي بعد C في ترتيب الحروف الإنجليزية؟",
        "prompt": "A B C ...",
        "options": ["B", "D", "E", "G"],
        "answer": "D",
    },
    {
        "id": "letters_4",
        "section": "letters",
        "section_label": "الحروف",
        "question": "اختر الحرف الصغير للحرف الكبير.",
        "prompt": "T",
        "options": ["f", "t", "l", "i"],
        "answer": "t",
    },
    {
        "id": "sounds_1",
        "section": "letter_sounds",
        "section_label": "أصوات الحروف",
        "question": "أي كلمة تبدأ بصوت /b/؟",
        "prompt": "/b/",
        "options": ["ball", "sun", "cat", "fish"],
        "answer": "ball",
    },
    {
        "id": "sounds_2",
        "section": "letter_sounds",
        "section_label": "أصوات الحروف",
        "question": "أي كلمة تبدأ بصوت /m/؟",
        "prompt": "/m/",
        "options": ["map", "dog", "pen", "red"],
        "answer": "map",
    },
    {
        "id": "sounds_3",
        "section": "letter_sounds",
        "section_label": "أصوات الحروف",
        "question": "ما الصوت الأول في كلمة sun؟",
        "prompt": "sun",
        "options": ["/s/", "/n/", "/u/", "/b/"],
        "answer": "/s/",
    },
    {
        "id": "sounds_4",
        "section": "letter_sounds",
        "section_label": "أصوات الحروف",
        "question": "أي كلمة تنتهي بصوت /t/؟",
        "prompt": "/t/",
        "options": ["hat", "bag", "man", "pen"],
        "answer": "hat",
    },
    {
        "id": "phonics_1",
        "section": "phonics",
        "section_label": "الصوتيات",
        "question": "أي كلمة تحتوي على الصوت الثنائي sh؟",
        "prompt": "sh",
        "options": ["ship", "chip", "thin", "duck"],
        "answer": "ship",
    },
    {
        "id": "phonics_2",
        "section": "phonics",
        "section_label": "الصوتيات",
        "question": "ما الصوت الثنائي في كلمة chair؟",
        "prompt": "chair",
        "options": ["ch", "sh", "th", "ck"],
        "answer": "ch",
    },
    {
        "id": "phonics_3",
        "section": "phonics",
        "section_label": "الصوتيات",
        "question": "أي نهاية نسمعها في كلمة duck؟",
        "prompt": "duck",
        "options": ["ck", "ng", "ll", "ss"],
        "answer": "ck",
    },
    {
        "id": "phonics_4",
        "section": "phonics",
        "section_label": "الصوتيات",
        "question": "أي كلمة تحتوي على الصوت الثلاثي igh؟",
        "prompt": "igh",
        "options": ["night", "rain", "shop", "bell"],
        "answer": "night",
    },
    {
        "id": "cvc_1",
        "section": "cvc",
        "section_label": "قراءة CVC",
        "question": "اختر الكلمة التي تعني قط.",
        "prompt": "قط",
        "options": ["cat", "cup", "cap", "cot"],
        "answer": "cat",
    },
    {
        "id": "cvc_2",
        "section": "cvc",
        "section_label": "قراءة CVC",
        "question": "أكمل الكلمة المناسبة للصورة الذهنية: c _ t",
        "prompt": "c _ t",
        "options": ["a", "e", "i", "u"],
        "answer": "a",
    },
    {
        "id": "cvc_3",
        "section": "cvc",
        "section_label": "قراءة CVC",
        "question": "أي كلمة تنتمي إلى عائلة -at؟",
        "prompt": "-at",
        "options": ["mat", "map", "mop", "mud"],
        "answer": "mat",
    },
    {
        "id": "cvc_4",
        "section": "cvc",
        "section_label": "قراءة CVC",
        "question": "اختر الكلمة الصحيحة من الأصوات: /s/ /u/ /n/",
        "prompt": "/s/ /u/ /n/",
        "options": ["sun", "sit", "sand", "son"],
        "answer": "sun",
    },
    {
        "id": "sentence_1",
        "section": "sentences",
        "section_label": "الجمل القصيرة",
        "question": "اقرأ الجملة: The cat is on the mat. أين القط؟",
        "prompt": "The cat is on the mat.",
        "options": ["on the mat", "in the bag", "under the bed", "near the sun"],
        "answer": "on the mat",
    },
    {
        "id": "sentence_2",
        "section": "sentences",
        "section_label": "الجمل القصيرة",
        "question": "اختر معنى الجملة: I can run.",
        "prompt": "I can run.",
        "options": ["أستطيع الركض", "أحب السمك", "أرى كتابا", "أنا نائم"],
        "answer": "أستطيع الركض",
    },
    {
        "id": "level4_1",
        "section": "level_four",
        "section_label": "المستوى الرابع",
        "question": "اختر الرد المناسب: How are you?",
        "prompt": "How are you?",
        "options": ["I am fine.", "It is a pen.", "On Monday.", "Blue, please."],
        "answer": "I am fine.",
    },
    {
        "id": "level4_2",
        "section": "level_four",
        "section_label": "المستوى الرابع",
        "question": "أكمل الجملة بالكلمة المناسبة: She ___ a book.",
        "prompt": "She ___ a book.",
        "options": ["reads", "read", "reading", "are read"],
        "answer": "reads",
    },
]


def public_placement_questions():
    return [
        {key: value for key, value in question.items() if key != "answer"}
        for question in PLACEMENT_TEST_QUESTIONS
    ]


def placement_level_meta(level_key):
    meta = {
        "level_1": {
            "title": "المستوى الأول",
            "track": "الحروف الإنجليزية A-Z",
            "message": "نقترح أن تبدأ من الحروف الإنجليزية وأصواتها الأساسية حتى تبني قاعدة ثابتة.",
            "cta_label": "ابدأ المستوى الأول",
            "cta_url": reverse("index"),
        },
        "level_2": {
            "title": "المستوى الثاني",
            "track": "الصوتيات والنطق",
            "message": "أنت تعرف جزءا جيدا من الحروف، والأنسب الآن تثبيت الصوتيات والنطق قبل الانتقال للقراءة.",
            "cta_label": "ابدأ المستوى الثاني",
            "cta_url": reverse("sounds"),
        },
        "level_3": {
            "title": "المستوى الثالث",
            "track": "قراءة CVC",
            "message": "أنت جاهز للانتقال إلى قراءة كلمات CVC والجمل والقصص القصيرة.",
            "cta_label": "اشترك في المستوى الثالث - 15 ريال شهريا",
            "cta_url": reverse("pricing") + "#level-3-plan",
        },
        "level_4": {
            "title": "المستوى الرابع",
            "track": "قراءة واستماع وتحدث وكتابة",
            "message": "أنت جاهز لمسار أوسع يطور القراءة والاستماع والتحدث والكتابة والمحادثة.",
            "cta_label": "اشترك في المستوى الرابع - 15 ريال شهريا",
            "cta_url": reverse("pricing") + "#level-4-plan",
        },
    }
    return meta[level_key]


def score_placement_test(answers):
    answer_map = answers if isinstance(answers, dict) else {}
    section_scores = {}
    correct_count = 0

    for question in PLACEMENT_TEST_QUESTIONS:
        section = question["section"]
        section_scores.setdefault(section, {
            "label": question["section_label"],
            "correct": 0,
            "total": 0,
        })
        section_scores[section]["total"] += 1

        if str(answer_map.get(question["id"], "")).strip() == question["answer"]:
            correct_count += 1
            section_scores[section]["correct"] += 1

    total = len(PLACEMENT_TEST_QUESTIONS)
    percentage = round((correct_count / total) * 100) if total else 0

    letters = section_scores.get("letters", {"correct": 0, "total": 1})
    letters_ratio = letters["correct"] / max(letters["total"], 1)

    phonics_correct = (
        section_scores.get("letter_sounds", {"correct": 0})["correct"]
        + section_scores.get("phonics", {"correct": 0})["correct"]
    )
    phonics_total = (
        section_scores.get("letter_sounds", {"total": 0})["total"]
        + section_scores.get("phonics", {"total": 0})["total"]
    )
    phonics_ratio = phonics_correct / max(phonics_total, 1)

    if letters_ratio < 0.6:
        recommended_level = "level_1"
        reason = "أسئلة الحروف الأساسية تحتاج مراجعة؛ لذلك الأفضل البداية من المستوى الأول."
    elif phonics_ratio < 0.55:
        recommended_level = "level_2"
        reason = "نتيجة الصوتيات تحتاج تثبيت قبل قراءة CVC؛ لذلك الأنسب المستوى الثاني."
    elif percentage < 40:
        recommended_level = "level_1"
        reason = "النتيجة العامة تشير إلى أن البداية من الحروف ستكون أكثر فائدة."
    elif percentage < 65:
        recommended_level = "level_2"
        reason = "النتيجة العامة مناسبة لمسار الصوتيات والنطق."
    elif percentage < 80:
        recommended_level = "level_3"
        reason = "الأساسيات جيدة، ويمكنك الانتقال إلى قراءة CVC."
    else:
        recommended_level = "level_4"
        reason = "النتيجة قوية وتناسب مسار القراءة والاستماع والتحدث والكتابة."

    meta = placement_level_meta(recommended_level)
    return {
        "score": correct_count,
        "total": total,
        "percentage": percentage,
        "recommended_level": recommended_level,
        "recommended_title": meta["title"],
        "recommended_track": meta["track"],
        "message": meta["message"],
        "reason": reason,
        "cta_label": meta["cta_label"],
        "cta_url": meta["cta_url"],
        "section_scores": section_scores,
    }


ENGLISH_FOUNDATION_SECTIONS = [
    {
        "key": "vocabulary",
        "title": "المفردات الإنجليزية",
        "subtitle": "Vocabulary Foundation",
        "icon": "📘",
        "url_name": "vocabulary_foundation",
        "url": "/vocabulary-foundation/",
        "color": "#2563eb",
        "description": "كلمات إنجليزية مع ترجمة ونطق وأمثلة وأسئلة قصيرة.",
        "actions": ["استماع", "مايك", "اختبر نفسك", "ورقة عمل"],
    },
    {
        "key": "grammar",
        "title": "القواعد التأسيسية",
        "subtitle": "Grammar Foundation",
        "icon": "📗",
        "url_name": "grammar_foundation",
        "url": "/grammar-foundation/",
        "color": "#059669",
        "description": "قواعد أساسية مشروحة بالعربي مع أمثلة وتدريبات.",
        "actions": ["حل التدريب", "إظهار الإجابة", "طباعة", "ورقة عمل"],
    },
    {
        "key": "conversations",
        "title": "المحادثات",
        "subtitle": "Interactive Conversations",
        "icon": "💬",
        "url_name": "conversations",
        "url": "/conversations/",
        "color": "#7c3aed",
        "description": "مواقف محادثة مع نطق لكل جملة ومايك للتقييم.",
        "actions": ["استمع للحوار", "اقرأ بالمايك", "رتب الحوار", "اختر الرد"],
    },
    {
        "key": "common_sentences",
        "title": "الجمل الشائعة",
        "subtitle": "Common Sentences",
        "icon": "🗣️",
        "url_name": "common_sentences",
        "url": "/common-sentences/",
        "color": "#0891b2",
        "description": "جمل يومية شائعة مع ترجمة ونطق واختبار سرعة القراءة.",
        "actions": ["نطق", "اختبار سرعة", "صح أو خطأ", "ورقة عمل"],
    },
    {
        "key": "worksheets",
        "title": "أوراق العمل",
        "subtitle": "Printable Worksheets",
        "icon": "📝",
        "url_name": "english_worksheets",
        "url": "/worksheets/",
        "color": "#b45309",
        "description": "أوراق مراجعة للطباعة: مفردات وقواعد ومحادثات وجمل.",
        "actions": ["طباعة", "حل", "مراجعة", "تسليم"],
    },
    {
        "key": "games",
        "title": "ألعاب وتدريبات",
        "subtitle": "Games and Practice",
        "icon": "🎮",
        "url_name": "english_games",
        "url": "/games/",
        "color": "#dc2626",
        "description": "Flashcards وMatching وSentence Builder وتحديات نطق.",
        "actions": ["Flashcards", "Match", "Build", "Speak"],
    },
]

ENGLISH_FOUNDATION_SECTION_MAP = {item["key"]: item for item in ENGLISH_FOUNDATION_SECTIONS}
ENGLISH_FOUNDATION_EXTRA_PROGRESS_SECTIONS = {
    "level_four_reading",
    "level_four_listening",
    "level_four_speaking",
    "level_four_writing",
    "level_four_stories",
    "level_four_exam",
}


def get_english_foundation_progress_map(user):
    if not user.is_authenticated:
        return {}
    return {
        item.section: item
        for item in EnglishFoundationProgress.objects.filter(user=user)
    }


def get_existing_bird_lottie_files():
    def calculate_files():
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

    return get_cached_static_value("bird-lottie-files", calculate_files)


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


def normalize_bird_word(value):
    word = (value or "").strip().lower()
    return word[:50]


def serialize_bird_review_item(item):
    return {
        "id": item.id,
        "letter": item.letter,
        "word": item.word,
        "question_type": item.question_type,
        "mistakes_count": item.mistakes_count,
        "success_count": item.success_count,
        "mastered": item.mastered,
        "last_reviewed_at": item.last_reviewed_at.isoformat() if item.last_reviewed_at else None,
    }


def safe_json_list(value):
    if isinstance(value, list):
        return value[:50]
    return []


def safe_json_dict(value):
    if isinstance(value, dict):
        return value
    return {}


def serialize_letter_progress(progress):
    return {
        "letter": progress.letter,
        "writing_score": progress.writing_score,
        "words_score": progress.words_score,
        "quiz_score": progress.quiz_score,
        "total_score": progress.total_score,
        "completed": progress.completed,
        "completed_at": progress.completed_at.isoformat() if progress.completed_at else None,
        "words_practiced": progress.words_practiced_json,
        "mistakes": progress.mistakes_json,
        "last_updated_at": progress.last_updated_at.isoformat() if progress.last_updated_at else None,
    }


CURRICULUM_STAGES = [
    {
        "id": "letters_a_z",
        "title_en": "Letters A-Z",
        "title_ar": "ط§ظ„ط­ط±ظˆظپ ط§ظ„ط¥ظ†ط¬ظ„ظٹط²ظٹط©",
        "description_ar": "طھط¹ظ„ظ… ط§ظ„ط­ط±ظˆظپ ط§ظ„ظƒط¨ظٹط±ط© ظˆط§ظ„طµط؛ظٹط±ط©طŒ طµظˆطھ ط§ظ„ط­ط±ظپطŒ ظƒطھط§ط¨ط© ط§ظ„ط­ط±ظپطŒ ظˆظƒظ„ظ…ط§طھ طھط¨ط¯ط£ ط¨ظ‡.",
        "order": 1,
        "status": "available",
        "unlock_condition": "",
        "lessons": [
            "uppercase_letters",
            "lowercase_letters",
            "letter_sounds",
            "letter_writing",
            "letter_words",
            "letter_games",
            "final_letters_test",
        ],
        "examples": [],
        "mastery_goal": "ط¥طھظ‚ط§ظ† A-Z ظ‚ط±ط§ط،ط© ظˆظƒطھط§ط¨ط© ظˆطµظˆطھظ‹ط§ ظˆظƒظ„ظ…ط§طھ ط£ط³ط§ط³ظٹط©.",
        "certificate": "Letter Mastery Certificate / ط´ظ‡ط§ط¯ط© ط¥طھظ‚ط§ظ† ط§ظ„ط­ط±ظˆظپ",
        "button_text": "ط§ط¨ط¯ط£ ط§ظ„ط­ط±ظˆظپ",
        "link": "/",
    },

    {
        "id": "reading_foundation",
        "title_en": "Reading Foundation",
        "title_ar": "ط£ط³ط§ط³ظٹط§طھ ط§ظ„ظ‚ط±ط§ط،ط©",
        "description_ar": "ط§ظ†طھظ‚ط§ظ„ ط§ظ„ط·ظپظ„ ظ…ظ† ط§ظ„ظƒظ„ظ…ط§طھ ط¥ظ„ظ‰ ط§ظ„ط¬ظ…ظ„ ظˆط§ظ„ظ‚طµطµ ط§ظ„ظ‚طµظٹط±ط© ظ…ط¹ ظپظ‡ظ… ط§ظ„ظ…ط¹ظ†ظ‰ ظˆط§ظ„ظ‚ط±ط§ط،ط© ط¨ط·ظ„ط§ظ‚ط©.",
        "order": 2,
        "status": "locked",
        "unlock_condition": "complete_letters_certificate",
        "lessons": [
            "Decodable Sentences",
            "Short Stories",
            "Comprehension Skills",
            "Fast Reading / Fluency",
        ],
        "examples": [
            "The cat sat.",
            "The dog can run.",
            "I see a ship.",
            "The girl has a cake.",
            "repeated reading",
            "60-second reading",
            "words per minute",
            "accuracy",
        ],
        "mastery_goal": "ظ‚ط±ط§ط،ط© ط¬ظ…ظ„ ظˆظ‚طµطµ ظ‚طµظٹط±ط© ط¨ط¯ظ‚ط© ظˆط³ط±ط¹ط© ظ…ظ†ط§ط³ط¨ط© ظ„ط¹ظ…ط± ط§ظ„ط·ظپظ„.",
        "certificate": "",
        "button_text": "ظ…ظ‚ظپظ„ ط§ظ„ط¢ظ†",
        "link": "",
    },
    {
        "id": "basic_grammar_foundation",
        "title_en": "Basic Grammar Foundation",
        "title_ar": "ط£ط³ط§ط³ظٹط§طھ ط§ظ„ظ‚ظˆط§ط¹ط¯",
        "description_ar": "ظ‚ظˆط§ط¹ط¯ ط¥ظ†ط¬ظ„ظٹط²ظٹط© ظ…ط¨ط³ط·ط© طھط³ط§ط¹ط¯ ط§ظ„ط·ظپظ„ ط¹ظ„ظ‰ طھظƒظˆظٹظ† ط¬ظ…ظ„ طµط­ظٹط­ط© ظپظٹ ط§ظ„ظ‚ط±ط§ط،ط© ظˆط§ظ„ظƒطھط§ط¨ط© ظˆط§ظ„ظ…ط­ط§ط¯ط«ط©.",
        "order": 3,
        "status": "locked",
        "unlock_condition": "complete_reading_foundation",
        "lessons": [
            "Pronouns",
            "Be Verbs",
            "Action Verbs",
            "Have / Has",
            "Like / Want / Need",
            "Nouns",
            "Adjectives",
            "Articles",
            "Prepositions",
            "Question Words",
            "Negatives",
            "Simple Present",
            "Present Continuous",
            "Simple Past",
            "Plural Nouns",
        ],
        "examples": [
            "Pronouns: I, you, he, she, it, we, they",
            "Be Verbs: am, is, are, was, were",
            "Action Verbs: run, walk, eat, drink, read, write, open, close",
            "Adjectives: big, small, hot, cold, happy, sad, fast, slow",
            "Prepositions: in, on, under, next to, behind, between",
            "Question Words: what, where, who, when, why, how",
            "I am a student.",
            "She is happy.",
            "He has a book.",
            "I read a book.",
            "Where is my bag?",
        ],
        "mastery_goal": "ظپظ‡ظ… ط§ظ„ط¬ظ…ظ„ط© ط§ظ„ط¨ط³ظٹط·ط© ظˆط¨ظ†ط§ط، ط¬ظ…ظ„ ظٹظˆظ…ظٹط© طµط­ظٹط­ط©.",
        "certificate": "",
        "button_text": "ظ…ظ‚ظپظ„ ط§ظ„ط¢ظ†",
        "link": "",
    },
    {
        "id": "functional_english",
        "title_en": "Functional English",
        "title_ar": "ط§ظ„ط¥ظ†ط¬ظ„ظٹط²ظٹط© ط§ظ„ظٹظˆظ…ظٹط© ظˆط§ظ„ظˆط¸ظٹظپظٹط©",
        "description_ar": "ط¹ط¨ط§ط±ط§طھ ظˆظ…ظˆط§ظ‚ظپ ظٹط­طھط§ط¬ظ‡ط§ ط§ظ„ط·ظپظ„ ظپظٹ ط§ظ„ظ…ط¯ط±ط³ط© ظˆط§ظ„ط¨ظٹطھ ظˆط§ظ„ط³ظپط± ظˆط§ظ„ظ…ط·ط¹ظ… ظˆط§ظ„ظ…طھط¬ط±.",
        "order": 4,
        "status": "locked",
        "unlock_condition": "complete_basic_grammar_foundation",
        "lessons": [
            "Classroom English",
            "Daily Common Sentences",
            "Real-Life Situations",
            "Vocabulary by Themes",
        ],
        "examples": [
            "Stand up. = ظ‚ظپ",
            "Sit down. = ط§ط¬ظ„ط³",
            "Open your book. = ط§ظپطھط­ ظƒطھط§ط¨ظƒ",
            "Close your book. = ط£ط؛ظ„ظ‚ ظƒطھط§ط¨ظƒ",
            "Listen carefully. = ط§ط³طھظ…ط¹ ط¬ظٹط¯ظ‹ط§",
            "Raise your hand. = ط§ط±ظپط¹ ظٹط¯ظƒ",
            "Good morning. = طµط¨ط§ط­ ط§ظ„ط®ظٹط±",
            "How are you? = ظƒظٹظپ ط­ط§ظ„ظƒطں",
            "I am fine. = ط£ظ†ط§ ط¨ط®ظٹط±",
            "What is your name? = ظ…ط§ ط§ط³ظ…ظƒطں",
            "Thank you. = ط´ظƒط±ظ‹ط§",
            "I am sorry. = ط£ظ†ط§ ط¢ط³ظپ",
            "At school",
            "At home",
            "At the cafe",
            "At the airport",
            "At the store",
            "At the restaurant",
            "Asking directions",
            "At the doctor",
            "Where is my classroom? = ط£ظٹظ† ظپطµظ„ظٹطں",
            "Can I go to the bathroom? = ظ‡ظ„ ط£ط³طھط·ظٹط¹ ط§ظ„ط°ظ‡ط§ط¨ ط¥ظ„ظ‰ ط¯ظˆط±ط© ط§ظ„ظ…ظٹط§ظ‡طں",
            "I want water, please. = ط£ط±ظٹط¯ ظ…ط§ط، ظ…ظ† ظپط¶ظ„ظƒ",
            "How much is this? = ظƒظ… ط³ط¹ط± ظ‡ط°ط§طں",
            "The bill, please. = ط§ظ„ط­ط³ط§ط¨ ظ…ظ† ظپط¶ظ„ظƒ",
            "Where is the gate? = ط£ظٹظ† ط§ظ„ط¨ظˆط§ط¨ط©طں",
            "I have a ticket. = ظ„ط¯ظٹ طھط°ظƒط±ط©",
            "I need help. = ط£ط­طھط§ط¬ ظ…ط³ط§ط¹ط¯ط©",
            "How much is it? = ظƒظ… ط³ط¹ط±ظ‡طں",
            "I want this one. = ط£ط±ظٹط¯ ظ‡ط°ط§",
            "Do you have a bigger size? = ظ‡ظ„ ظٹظˆط¬ط¯ ظ…ظ‚ط§ط³ ط£ظƒط¨ط±طں",
        ],
        "mastery_goal": "ط§ط³طھط®ط¯ط§ظ… ط¬ظ…ظ„ ط¹ظ…ظ„ظٹط© ظپظٹ ظ…ظˆط§ظ‚ظپ ظٹظˆظ…ظٹط© ط­ظ‚ظٹظ‚ظٹط©.",
        "certificate": "",
        "button_text": "ظ…ظ‚ظپظ„ ط§ظ„ط¢ظ†",
        "link": "",
    },
    {
        "id": "writing_foundation",
        "title_en": "Writing Foundation",
        "title_ar": "ط£ط³ط§ط³ظٹط§طھ ط§ظ„ظƒطھط§ط¨ط©",
        "description_ar": "طھط¯ط±ظٹط¨ط§طھ طھط¯ط±ظٹط¬ظٹط© ظ…ظ† طھطھط¨ط¹ ط§ظ„ظƒظ„ظ…ط§طھ ط¥ظ„ظ‰ ظƒطھط§ط¨ط© ط¬ظ…ظ„ ظ‚طµظٹط±ط© ط¹ظ† طµظˆط±ط© ط£ظˆ ط¥ظ…ظ„ط§ط،.",
        "order": 5,
        "status": "coming_soon",
        "unlock_condition": "complete_functional_english",
        "lessons": [
            "trace_words",
            "copy_sentence",
            "complete_sentence",
            "arrange_words",
            "write_about_picture",
            "dictation",
        ],
        "examples": [],
        "mastery_goal": "ظƒطھط§ط¨ط© ظƒظ„ظ…ط§طھ ظˆط¬ظ…ظ„ ظ‚طµظٹط±ط© ط¨ط«ظ‚ط© ظˆطھظ†ط¸ظٹظ….",
        "certificate": "",
        "button_text": "ظ‚ط±ظٹط¨ظ‹ط§",
        "link": "",
    },
    {
        "id": "worksheets",
        "title_en": "Worksheets",
        "title_ar": "ط£ظˆط±ط§ظ‚ ط§ظ„ط¹ظ…ظ„",
        "description_ar": "ط£ظˆط±ط§ظ‚ طھط¯ط±ظٹط¨ ط¯ط§ط¹ظ…ط© ظ„ظ„ط·ط¨ط§ط¹ط© ط£ظˆ ط§ظ„ط­ظ„ ط¯ط§ط®ظ„ ط§ظ„ظ…ظ†طµط© ط­ط³ط¨ ظ…ط±ط­ظ„ط© ط§ظ„ط·ظپظ„.",
        "order": 6,
        "status": "coming_soon",
        "unlock_condition": "curriculum_practice",
        "lessons": [
            "trace",
            "circle",
            "match",
            "fill_missing_sound",
            "missing_word",
            "dictation",
            "read_and_color",
            "mini_quiz",
        ],
        "examples": [],
        "mastery_goal": "طھط«ط¨ظٹطھ ط§ظ„ظ…ظ‡ط§ط±ط§طھ ط¹ط¨ط± طھط¯ط±ظٹط¨ط§طھ ظ‚طµظٹط±ط© ظˆظ…طھظ†ظˆط¹ط©.",
        "certificate": "",
        "button_text": "ظ‚ط±ظٹط¨ظ‹ط§",
        "link": "",
    },
    {
        "id": "workbook_pdf",
        "title_en": "Workbook PDF",
        "title_ar": "ظƒطھط§ط¨ ط§ظ„طھظ…ط§ط±ظٹظ† PDF",
        "description_ar": "ظƒطھط§ط¨ طھط¯ط±ظٹط¨ط§طھ ط´ط§ظ…ظ„ ظٹط؛ط·ظٹ ط§ظ„ط­ط±ظˆظپ ظˆط§ظ„ظپظˆظ†ظƒط³ ظˆط§ظ„ظ‚ط±ط§ط،ط© ظˆط§ظ„ظ‚ظˆط§ط¹ط¯ ظˆط§ظ„ظ…ظپط±ط¯ط§طھ.",
        "order": 7,
        "status": "coming_soon",
        "unlock_condition": "curriculum_practice",
        "lessons": [
            "letters_workbook",
            "phonics_workbook",
            "reading_workbook",
            "grammar_workbook",
            "vocabulary_workbook",
            "full_workbook",
        ],
        "examples": [],
        "mastery_goal": "طھظˆظپظٹط± ظ…ط³ط§ط± طھط¯ط±ظٹط¨ظٹ ظ…ط·ط¨ظˆط¹/ط±ظ‚ظ…ظٹ ظƒط§ظ…ظ„ ظ„ظ„ظ…ط±ط§ط¬ط¹ط©.",
        "certificate": "",
        "button_text": "ظ‚ط±ظٹط¨ظ‹ط§",
        "link": "",
    },
]


CURRICULUM_STAGES = [
    {
        "id": "letters_a_z",
        "title_en": "Letters A-Z",
        "title_ar": "الحروف الإنجليزية",
        "description_ar": "تعلم الحروف الكبيرة والصغيرة، صوت الحرف، كتابة الحرف، وكلمات تبدأ به.",
        "order": 1,
        "status": "available",
        "unlock_condition": "",
        "lessons": [
            "Uppercase Letters",
            "Lowercase Letters",
            "Letter Sounds",
            "Letter Writing",
            "Words by Letter",
            "Letter Games",
            "Final Letters Test",
        ],
        "examples": [],
        "mastery_goal": "إتقان A-Z قراءة وكتابة وصوتًا وكلمات أساسية.",
        "certificate": "Letter Mastery Certificate / شهادة إتقان الحروف",
        "button_text": "ابدأ الحروف",
        "link": "/",
    },

    {
        "id": "reading_foundation",
        "title_en": "Reading Foundation",
        "title_ar": "أساسيات القراءة",
        "description_ar": "انتقال المتعلم من الكلمات إلى الجمل والقصص القصيرة مع فهم المعنى والقراءة بطلاقة.",
        "order": 2,
        "status": "locked",
        "unlock_condition": "complete_letters_certificate",
        "lessons": [
            "Decodable Sentences",
            "Short Stories",
            "Comprehension Skills",
            "Fast Reading / Fluency",
        ],
        "examples": [
            "The cat sat.",
            "The dog can run.",
            "I see a ship.",
            "The girl has a cake.",
            "Repeated reading",
            "60-second reading",
            "Words per minute",
            "Accuracy",
        ],
        "mastery_goal": "قراءة جمل وقصص قصيرة بدقة وسرعة مناسبة لمستوى المتعلم.",
        "certificate": "",
        "button_text": "مقفل الآن",
        "link": "",
    },
    {
        "id": "basic_grammar_foundation",
        "title_en": "Basic Grammar Foundation",
        "title_ar": "أساسيات القواعد",
        "description_ar": "قواعد إنجليزية مبسطة تساعد المتعلم على تكوين جمل صحيحة في القراءة والكتابة والمحادثة.",
        "order": 3,
        "status": "locked",
        "unlock_condition": "complete_reading_foundation",
        "lessons": [
            "Pronouns",
            "Be Verbs",
            "Action Verbs",
            "Have / Has",
            "Like / Want / Need",
            "Nouns",
            "Adjectives",
            "Articles",
            "Prepositions",
            "Question Words",
            "Negatives",
            "Simple Present",
            "Present Continuous",
            "Simple Past",
            "Plural Nouns",
        ],
        "examples": [
            "Pronouns: I, you, he, she, it, we, they",
            "Be Verbs: am, is, are, was, were",
            "Action Verbs: run, walk, eat, drink, read, write",
            "Adjectives: big, small, hot, cold, happy, sad",
            "Prepositions: in, on, under, next to, behind",
            "I am a student.",
            "She is happy.",
            "He has a book.",
            "Where is my bag?",
        ],
        "mastery_goal": "فهم الجملة البسيطة وبناء جمل يومية صحيحة.",
        "certificate": "",
        "button_text": "مقفل الآن",
        "link": "",
    },
    {
        "id": "functional_english",
        "title_en": "Functional English",
        "title_ar": "الإنجليزية اليومية والوظيفية",
        "description_ar": "عبارات ومواقف يحتاجها المتعلم في المدرسة والبيت والسفر والمطعم والمتجر.",
        "order": 4,
        "status": "locked",
        "unlock_condition": "complete_basic_grammar_foundation",
        "lessons": [
            "Classroom English",
            "Daily Common Sentences",
            "Real-Life Situations",
            "Vocabulary by Themes",
        ],
        "examples": [
            "Stand up. = قف",
            "Sit down. = اجلس",
            "Open your book. = افتح كتابك",
            "Close your book. = أغلق كتابك",
            "Listen carefully. = استمع جيدًا",
            "Good morning. = صباح الخير",
            "How are you? = كيف حالك؟",
            "I am fine. = أنا بخير",
            "Thank you. = شكرًا",
            "I need help. = أحتاج مساعدة",
        ],
        "mastery_goal": "استخدام جمل عملية في مواقف يومية حقيقية.",
        "certificate": "",
        "button_text": "مقفل الآن",
        "link": "",
    },
    {
        "id": "writing_foundation",
        "title_en": "Writing Foundation",
        "title_ar": "أساسيات الكتابة",
        "description_ar": "تدريبات تدريجية من تتبع الكلمات إلى كتابة جمل قصيرة عن صورة أو إملاء.",
        "order": 5,
        "status": "coming_soon",
        "unlock_condition": "complete_functional_english",
        "lessons": [
            "Trace Words",
            "Copy Sentence",
            "Complete Sentence",
            "Arrange Words",
            "Write About Picture",
            "Dictation",
        ],
        "examples": [],
        "mastery_goal": "كتابة كلمات وجمل قصيرة بثقة وتنظيم.",
        "certificate": "",
        "button_text": "قريبًا",
        "link": "",
    },
    {
        "id": "worksheets",
        "title_en": "Worksheets",
        "title_ar": "أوراق العمل",
        "description_ar": "أوراق تدريب داعمة للطباعة أو الحل داخل المنصة حسب مرحلة المتعلم.",
        "order": 6,
        "status": "coming_soon",
        "unlock_condition": "curriculum_practice",
        "lessons": [
            "Trace",
            "Circle",
            "Match",
            "Fill Missing Sound",
            "Missing Word",
            "Dictation",
            "Read and Color",
            "Mini Quiz",
        ],
        "examples": [],
        "mastery_goal": "تثبيت المهارات عبر تدريبات قصيرة ومتنوعة.",
        "certificate": "",
        "button_text": "قريبًا",
        "link": "",
    },
    {
        "id": "workbook_pdf",
        "title_en": "Workbook PDF",
        "title_ar": "كتاب التمارين PDF",
        "description_ar": "كتاب تدريبات شامل يغطي الحروف والفونكس والقراءة والقواعد والمفردات.",
        "order": 7,
        "status": "coming_soon",
        "unlock_condition": "curriculum_practice",
        "lessons": [
            "Letters Workbook",
            "Phonics Workbook",
            "Reading Workbook",
            "Grammar Workbook",
            "Vocabulary Workbook",
            "Full Workbook",
        ],
        "examples": [],
        "mastery_goal": "توفير مسار تدريبي مطبوع أو رقمي كامل للمراجعة.",
        "certificate": "",
        "button_text": "قريبًا",
        "link": "",
    },
]


# ============================================
# LETTER PROGRESS (CSRF Protected)
# ============================================

@require_POST
@login_required
@rate_limit("letter-progress", limit_setting="RATE_LIMIT_WRITE", default=60)
def save_progress(request):
    """
    Expected JSON: {student, letter, score}
    score is 0..20
    """
    data, error = parse_json_safely(request)
    if error:
        return error

    letter_raw = data.get("letter")
    score_raw = data.get("score")

    if letter_raw is None or score_raw is None:
        return _json_error("Missing required fields: letter, score", 400)

    letter, error = validate_letter(letter_raw)
    if error:
        return error

    if letter not in FREE_LEVEL_ONE_LETTERS and not is_level_one_basic_user(request.user):
        return JsonResponse({
            "error": "basic_plan_required",
            "message": "التجربة المجانية متاحة لحرفي A و B فقط.",
            "allowed_letters": sorted(FREE_LEVEL_ONE_LETTERS),
        }, status=403)

    score, error = validate_int(score_raw, min_val=0, max_val=20, field_name="score")
    if error:
        return error

    try:
        with transaction.atomic():
            # enforce previous letter completion
            if letter != "A":
                prev_letter = chr(ord(letter) - 1)
                prev_passed = LetterProgress.objects.filter(
                    user=request.user,
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
                user=request.user,
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

    except Exception:
        logger.exception("letter_progress_save_failed request_id=%s", getattr(request, "request_id", ""))
        return _json_error("Database error", 500, request_id=getattr(request, "request_id", ""))


@require_POST
def save_letter_progress_api(request):
    if not request.user.is_authenticated:
        return _json_error("login_required", 401, detail="Please sign in to save letter progress.")

    data, error = parse_json_safely(request)
    if error:
        return error

    letter, error = validate_letter(data.get("letter"))
    if error:
        return error

    if letter not in FREE_LEVEL_ONE_LETTERS and not is_level_one_basic_user(request.user):
        return JsonResponse({
            "error": "basic_plan_required",
            "message": "التجربة المجانية متاحة لحرفي A و B فقط.",
            "allowed_letters": sorted(FREE_LEVEL_ONE_LETTERS),
        }, status=403)

    writing_score, error = validate_int(data.get("writing_score", 0), min_val=0, max_val=100, field_name="writing_score")
    if error:
        return error

    words_score, error = validate_int(data.get("words_score", 0), min_val=0, max_val=100, field_name="words_score")
    if error:
        return error

    quiz_score, error = validate_int(data.get("quiz_score", 0), min_val=0, max_val=100, field_name="quiz_score")
    if error:
        return error

    total_score, error = validate_int(data.get("total_score", 0), min_val=0, max_val=100, field_name="total_score")
    if error:
        return error

    completed = bool(data.get("completed"))
    words_practiced = safe_json_list(data.get("words_practiced"))
    mistakes = safe_json_dict(data.get("mistakes"))
    now = timezone.now()

    try:
        with transaction.atomic():
            progress, created = LetterProgress.objects.select_for_update().get_or_create(
                user=request.user,
                letter=letter,
                defaults={
                    "writing_score": writing_score,
                    "words_score": words_score,
                    "quiz_score": quiz_score,
                    "total_score": total_score,
                    "score": total_score,
                    "completed": completed,
                    "passed": completed,
                    "completed_at": now if completed else None,
                    "words_practiced_json": words_practiced,
                    "mistakes_json": mistakes,
                },
            )

            if not created:
                progress.writing_score = writing_score
                progress.words_score = words_score
                progress.quiz_score = quiz_score
                progress.total_score = total_score
                progress.score = total_score
                progress.completed = completed
                progress.passed = completed
                progress.words_practiced_json = words_practiced
                progress.mistakes_json = mistakes
                if completed and not progress.completed_at:
                    progress.completed_at = now
                if not completed:
                    progress.completed_at = None
                progress.save(update_fields=[
                    "writing_score",
                    "words_score",
                    "quiz_score",
                    "total_score",
                    "score",
                    "completed",
                    "passed",
                    "completed_at",
                    "words_practiced_json",
                    "mistakes_json",
                    "timestamp",
                    "last_updated_at",
                ])

        return JsonResponse({
            "status": "ok",
            "created": created,
            "progress": serialize_letter_progress(progress),
        })
    except Exception:
        logger.exception("account_letter_progress_save_failed request_id=%s", getattr(request, "request_id", ""))
        return _json_error("Failed to save letter progress", 500, request_id=getattr(request, "request_id", ""))


@login_required
@require_POST
def bird_tutor_progress_api(request):
    blocked = require_feature(request, "bird_tutor", UPGRADE_VIP_OR_FULL_MESSAGE)
    if blocked:
        return blocked

    data, error = parse_json_safely(request)
    if error:
        return error

    xp_delta, error = validate_int(data.get("xp_delta", 0), min_val=0, max_val=100, field_name="xp_delta")
    if error:
        return error

    question_type = (data.get("question_type") or "").strip()[:40]
    is_correct = bool(data.get("is_correct"))
    letter, error = validate_letter(data.get("letter"))
    if error:
        return error

    word = normalize_bird_word(data.get("word"))
    if not word:
        return _json_error("word is required", 400)

    now = timezone.now()

    try:
        with transaction.atomic():
            progress, _ = BirdTutorProgress.objects.select_for_update().get_or_create(user=request.user)
            progress.xp = F("xp") + xp_delta
            progress.total_questions = F("total_questions") + 1
            if is_correct:
                progress.correct_answers = F("correct_answers") + 1
            else:
                progress.wrong_answers = F("wrong_answers") + 1
            progress.last_used_at = now
            progress.save(update_fields=[
                "xp",
                "total_questions",
                "correct_answers",
                "wrong_answers",
                "last_used_at",
                "updated_at",
            ])
            progress.refresh_from_db()

        return JsonResponse({
            "status": "ok",
            "progress": {
                "xp": progress.xp,
                "total_questions": progress.total_questions,
                "correct_answers": progress.correct_answers,
                "wrong_answers": progress.wrong_answers,
                "last_used_at": progress.last_used_at.isoformat() if progress.last_used_at else None,
            },
        })
    except Exception:
        logger.exception("bird_tutor_progress_save_failed request_id=%s", getattr(request, "request_id", ""))
        return _json_error("Failed to save bird tutor progress", 500, request_id=getattr(request, "request_id", ""))


@login_required
@require_http_methods(["GET", "POST"])
def bird_tutor_review_api(request):
    blocked = require_feature(request, "bird_tutor", UPGRADE_VIP_OR_FULL_MESSAGE)
    if blocked:
        return blocked

    if request.method == "GET":
        items = (
            BirdReviewItem.objects
            .filter(user=request.user, mastered=False)
            .order_by("-updated_at", "letter", "word")[:50]
        )
        return JsonResponse({"items": [serialize_bird_review_item(item) for item in items]})

    data, error = parse_json_safely(request)
    if error:
        return error

    letter, error = validate_letter(data.get("letter"))
    if error:
        return error

    word = normalize_bird_word(data.get("word"))
    if not word:
        return _json_error("word is required", 400)

    question_type = (data.get("question_type") or "").strip()[:40]
    is_correct = bool(data.get("is_correct"))
    now = timezone.now()

    try:
        with transaction.atomic():
            item, _ = BirdReviewItem.objects.select_for_update().get_or_create(
                user=request.user,
                letter=letter,
                word=word,
                defaults={"question_type": question_type},
            )

            if question_type:
                item.question_type = question_type

            if is_correct:
                item.success_count += 1
                if item.success_count >= 2:
                    item.mastered = True
            else:
                item.mistakes_count += 1
                item.mastered = False

            item.last_reviewed_at = now
            item.save(update_fields=[
                "question_type",
                "mistakes_count",
                "success_count",
                "mastered",
                "last_reviewed_at",
                "updated_at",
            ])

        return JsonResponse({"status": "ok", "item": serialize_bird_review_item(item)})
    except Exception:
        logger.exception("bird_review_update_failed request_id=%s", getattr(request, "request_id", ""))
        return _json_error("Failed to update bird tutor review item", 500, request_id=getattr(request, "request_id", ""))


# ظ‡ط°ط§ endpoint ط®ط§ط±ط¬ظٹ (ظ„ط§ط­ظ‚ظ‹ط§ ط­ط·ظٹ API KEY)
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
            "accuracy": None,
            "correct": False,
            "message": "This endpoint is a compatibility placeholder. Current pronunciation practice uses browser Web Speech text recognition, not deep server-side audio analysis."
        })
    except Exception:
        logger.exception("speech_check_failed request_id=%s", getattr(request, "request_id", ""))
        return _json_error("Speech check failed", 500, request_id=getattr(request, "request_id", ""))


@require_GET
@login_required
def generate_certificate(request, student_id):
    """
    PDF certificate if completed A-Z
    """
    try:
        if not request.user.is_staff:
            raise Http404("Certificate not found")
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
        # ط¥ط°ط§ ظ…ط§ طھط¨ظٹظ† طھط­ظ…ظٹظ„ ظ…ط¨ط§ط´ط±طŒ ط´ظٹظ„ظٹ Content-Disposition
        response["Content-Disposition"] = f'attachment; filename="certificate_{student.name}.pdf"'

        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return _json_error("PDF generation failed", 500)

        response["Cache-Control"] = "private, no-store"
        response["Pragma"] = "no-cache"
        return response

    except Http404:
        raise
    except Exception:
        logger.exception("certificate_generation_failed request_id=%s", getattr(request, "request_id", ""))
        return _json_error("Certificate generation failed", 500, request_id=getattr(request, "request_id", ""))


# ============================================
# GENERAL PAGES
# ============================================


@sensitive_post_parameters("password1", "password2")
@never_cache
@require_http_methods(["GET", "POST"])
@rate_limit("register", limit_setting="RATE_LIMIT_REGISTER", default=5)
def register(request):
    if request.user.is_authenticated:
        return redirect("index")

    form = StudentRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            user = form.save()
        auth_login(request, user)
        messages.success(request, "تم إنشاء الحساب وتسجيل الدخول بنجاح.")
        return redirect("index")

    return render(request, "accounts/register.html", {"form": form})


@sensitive_post_parameters("password")
@never_cache
@require_http_methods(["GET", "POST"])
@rate_limit("login-ip", limit_setting="RATE_LIMIT_LOGIN", default=10)
@rate_limit("login-account", limit_setting="RATE_LIMIT_LOGIN", default=10, identity=login_identity)
def login_view(request):
    if request.user.is_authenticated:
        return redirect("index")

    form = SecureAuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        auth_login(request, form.get_user())
        messages.success(request, "تم تسجيل الدخول بنجاح.")
        next_url = request.GET.get("next") or ""
        if url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=not settings.DEBUG,
        ):
            return redirect(next_url)
        return redirect("index")

    return render(request, "accounts/login.html", {"form": form})


@login_required
@require_POST
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


@require_POST
def english_foundation_progress_api(request):
    blocked = require_feature(request, "level_four", UPGRADE_LEVEL_FOUR_MESSAGE)
    if blocked:
        return blocked

    if not request.user.is_authenticated:
        return JsonResponse({"authenticated": False, "message": "local_only"})

    data, error = parse_json_safely(request)
    if error:
        return error

    section = (data.get("section") or "").strip()
    if section not in ENGLISH_FOUNDATION_SECTION_MAP and section not in ENGLISH_FOUNDATION_EXTRA_PROGRESS_SECTIONS:
        return _json_error("Invalid English foundation section", 400)

    activity_type = (data.get("activity_type") or "open").strip()[:80]
    default_points = {
        "open": 1,
        "exercise": 5,
        "game": 7,
        "mic": 5,
        "worksheet": 10,
        "complete": 50,
    }.get(activity_type, 3)
    points, error = validate_int(data.get("points", default_points), min_val=0, max_val=100, field_name="points")
    if error:
        return error
    completed = bool(data.get("completed")) or activity_type == "complete"

    progress, _ = EnglishFoundationProgress.objects.get_or_create(
        user=request.user,
        section=section,
    )
    progress.points += points
    progress.actions_count += 1
    progress.completed = progress.completed or completed
    progress.last_activity_type = activity_type
    progress.last_activity_at = timezone.now()
    progress.save(update_fields=[
        "points",
        "actions_count",
        "completed",
        "last_activity_type",
        "last_activity_at",
        "updated_at",
    ])

    return JsonResponse({
        "authenticated": True,
        "status": "ok",
        "section": section,
        "points": progress.points,
        "actions_count": progress.actions_count,
        "completed": progress.completed,
    })


def english_foundation_context_for_user(user):
    progress_map = get_english_foundation_progress_map(user)
    sections = []
    for section in ENGLISH_FOUNDATION_SECTIONS:
        progress = progress_map.get(section["key"])
        sections.append({
            **section,
            "points": progress.points if progress else 0,
            "actions_count": progress.actions_count if progress else 0,
            "completed": progress.completed if progress else False,
        })
    return sections


def english_foundation_items(section_key):
    if section_key == "vocabulary":
        return [
            {"title": "classroom", "ar": "فصل دراسي", "example": "I study English in the classroom.", "type": "School"},
            {"title": "dictionary", "ar": "قاموس", "example": "I use a dictionary to find new words.", "type": "School"},
            {"title": "computer", "ar": "حاسوب", "example": "I use a computer to write my project.", "type": "Technology"},
            {"title": "worried", "ar": "قلق", "example": "I feel worried before the exam.", "type": "Feelings"},
            {"title": "airport", "ar": "مطار", "example": "We arrived early at the airport.", "type": "Travel"},
            {"title": "responsibility", "ar": "مسؤولية", "example": "Cleaning your desk is your responsibility.", "type": "Challenge"},
        ]
    if section_key == "grammar":
        return [
            {"title": "Subject Pronouns", "ar": "ضمائر الفاعل", "example": "I, you, he, she, it, we, they.", "type": "Pronouns"},
            {"title": "Verb to be", "ar": "فعل يكون", "example": "I am a student. She is happy.", "type": "Basics"},
            {"title": "Present Simple", "ar": "المضارع البسيط", "example": "She reads books.", "type": "Tenses"},
            {"title": "Present Continuous", "ar": "المضارع المستمر", "example": "They are watching TV.", "type": "Tenses"},
            {"title": "Question Words", "ar": "أدوات السؤال", "example": "Where do you live?", "type": "Questions"},
            {"title": "Can / Can't", "ar": "القدرة", "example": "I can swim. I can't fly.", "type": "Modal"},
        ]
    if section_key == "conversations":
        return [
            {"title": "At school", "ar": "في المدرسة", "example": "A: Good morning. B: Good morning.", "type": "School"},
            {"title": "At the restaurant", "ar": "في المطعم", "example": "A: I would like water, please.", "type": "Food"},
            {"title": "At the airport", "ar": "في المطار", "example": "A: Where is my gate?", "type": "Travel"},
            {"title": "At the market", "ar": "في السوق", "example": "A: How much is this?", "type": "Shopping"},
            {"title": "Meeting a new friend", "ar": "مقابلة صديق جديد", "example": "A: Nice to meet you.", "type": "Daily"},
        ]
    if section_key == "common_sentences":
        return [
            {"title": "Good morning.", "ar": "صباح الخير.", "example": "Good morning.", "type": "Polite Expressions"},
            {"title": "How are you today?", "ar": "كيف حالك اليوم؟", "example": "How are you today?", "type": "Daily Life"},
            {"title": "Can you help me, please?", "ar": "هل يمكنك مساعدتي من فضلك؟", "example": "Can you help me, please?", "type": "Polite Expressions"},
            {"title": "I want to improve my reading.", "ar": "أريد أن أحسن قراءتي.", "example": "I want to improve my reading.", "type": "Speaking Practice"},
            {"title": "Never give up.", "ar": "لا تستسلم أبدًا.", "example": "Never give up.", "type": "Speaking Practice"},
        ]
    if section_key == "worksheets":
        return [
            {"title": "Vocabulary Worksheet", "ar": "ورقة مفردات", "example": "Match the word with the meaning.", "type": "Printable"},
            {"title": "Grammar Worksheet", "ar": "ورقة قواعد", "example": "Choose the correct answer.", "type": "Printable"},
            {"title": "Conversation Worksheet", "ar": "ورقة محادثة", "example": "Complete the dialogue.", "type": "Printable"},
            {"title": "Common Sentences Worksheet", "ar": "ورقة الجمل الشائعة", "example": "Translate and reorder sentences.", "type": "Printable"},
        ]
    return [
        {"title": "Flashcards", "ar": "بطاقات", "example": "Flip the card and say the answer.", "type": "Game"},
        {"title": "Word Match", "ar": "مطابقة الكلمات", "example": "Match English with Arabic.", "type": "Game"},
        {"title": "Sentence Builder", "ar": "ترتيب الجملة", "example": "Build a correct sentence.", "type": "Game"},
        {"title": "Speak Challenge", "ar": "تحدي النطق", "example": "Read and compare your voice.", "type": "Game"},
    ]


@ensure_csrf_cookie
@require_GET
def english_foundation(request):
    blocked = require_feature(request, "level_four", UPGRADE_LEVEL_FOUR_MESSAGE)
    if blocked:
        return blocked

    return render(request, "english_foundation.html", {
        "sections": english_foundation_context_for_user(request.user),
    })


@ensure_csrf_cookie
@require_GET
def english_foundation_section(request, section_key):
    blocked = require_feature(request, "level_four", UPGRADE_LEVEL_FOUR_MESSAGE)
    if blocked:
        return blocked

    section = ENGLISH_FOUNDATION_SECTION_MAP[section_key]
    progress = get_english_foundation_progress_map(request.user).get(section_key)
    return render(request, "english_foundation_section.html", {
        "section": section,
        "items": english_foundation_items(section_key),
        "points": progress.points if progress else 0,
        "actions_count": progress.actions_count if progress else 0,
        "completed": progress.completed if progress else False,
        "all_sections": ENGLISH_FOUNDATION_SECTIONS,
    })


@ensure_csrf_cookie
@require_GET
def vocabulary_foundation(request):
    blocked = require_feature(request, "level_four", UPGRADE_LEVEL_FOUR_MESSAGE)
    if blocked:
        return blocked

    progress = get_english_foundation_progress_map(request.user).get("vocabulary")
    return render(request, "vocabulary_foundation.html", {
        "points": progress.points if progress else 0,
        "actions_count": progress.actions_count if progress else 0,
        "completed": progress.completed if progress else False,
    })


@ensure_csrf_cookie
@require_GET
def vocabulary_foundation_worksheet(request):
    blocked = require_feature(request, "level_four", UPGRADE_LEVEL_FOUR_MESSAGE)
    if blocked:
        return blocked

    return render(request, "worksheets/vocabulary_worksheet.html")


@ensure_csrf_cookie
@require_GET
def grammar_foundation(request):
    blocked = require_feature(request, "level_four", UPGRADE_LEVEL_FOUR_MESSAGE)
    if blocked:
        return blocked

    progress = get_english_foundation_progress_map(request.user).get("grammar")
    return render(request, "grammar_foundation.html", {
        "points": progress.points if progress else 0,
        "actions_count": progress.actions_count if progress else 0,
        "completed": progress.completed if progress else False,
    })


@ensure_csrf_cookie
@require_GET
def grammar_foundation_worksheet(request):
    blocked = require_feature(request, "level_four", UPGRADE_LEVEL_FOUR_MESSAGE)
    if blocked:
        return blocked

    return render(request, "worksheets/grammar_worksheet.html")


@ensure_csrf_cookie
@require_GET
def conversations(request):
    blocked = require_feature(request, "level_four", UPGRADE_LEVEL_FOUR_MESSAGE)
    if blocked:
        return blocked

    progress = get_english_foundation_progress_map(request.user).get("conversations")
    return render(request, "conversations.html", {
        "points": progress.points if progress else 0,
        "actions_count": progress.actions_count if progress else 0,
        "completed": progress.completed if progress else False,
    })


@ensure_csrf_cookie
@require_GET
def conversations_worksheet(request):
    blocked = require_feature(request, "level_four", UPGRADE_LEVEL_FOUR_MESSAGE)
    if blocked:
        return blocked

    return render(request, "worksheets/conversations_worksheet.html")


@ensure_csrf_cookie
@require_GET
def common_sentences(request):
    blocked = require_feature(request, "level_four", UPGRADE_LEVEL_FOUR_MESSAGE)
    if blocked:
        return blocked

    progress = get_english_foundation_progress_map(request.user).get("common_sentences")
    return render(request, "common_sentences.html", {
        "points": progress.points if progress else 0,
        "actions_count": progress.actions_count if progress else 0,
        "completed": progress.completed if progress else False,
    })


@ensure_csrf_cookie
@require_GET
def worksheets_center(request):
    blocked = require_feature(request, "level_four", UPGRADE_LEVEL_FOUR_MESSAGE)
    if blocked:
        return blocked

    progress = get_english_foundation_progress_map(request.user).get("worksheets")
    return render(request, "worksheets/worksheets_center.html", {
        "points": progress.points if progress else 0,
        "actions_count": progress.actions_count if progress else 0,
        "completed": progress.completed if progress else False,
    })


def english_worksheets(request):
    return worksheets_center(request)


@ensure_csrf_cookie
@require_GET
def mixed_review_worksheet(request):
    blocked = require_feature(request, "level_four", UPGRADE_LEVEL_FOUR_MESSAGE)
    if blocked:
        return blocked

    return render(request, "worksheets/mixed_review_worksheet.html")


@ensure_csrf_cookie
@require_GET
def phonics_foundation_worksheet(request):
    blocked = require_feature(request, "sounds_worksheets", "أوراق عمل الصوتيات متاحة في Silver أو باقة أعلى.")
    if blocked:
        return blocked

    return sounds_worksheet(request)


@ensure_csrf_cookie
@require_GET
def letters_mastery_worksheet(request):
    blocked = require_feature(request, "worksheets_level1", "أوراق عمل الحروف متاحة في Silver أو باقة أعلى.")
    if blocked:
        return blocked

    return render(request, "worksheets/letters_mastery_worksheet.html", {
        "letters": list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
    })


def letter_worksheet_book_items():
    letters = {letter: [] for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
    data_path = Path(settings.BASE_DIR) / "static" / "js" / "letters" / "letter_data.js"
    try:
        text = data_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        text = ""

    for block in re.finditer(r"^\s*([A-Z]):\s*\[(.*?)^\s*\]", text, flags=re.DOTALL | re.MULTILINE):
        letter = block.group(1)
        words = []
        for item in re.finditer(
            r'word:\s*"([^"]+)"\s*,\s*translation:\s*"([^"]*)"\s*,\s*emoji:\s*"([^"]*)"',
            block.group(2),
        ):
            words.append({
                "word": item.group(1),
                "translation": item.group(2),
                "emoji": item.group(3),
            })
        letters[letter] = words[:5]

    return [
        {
            "letter": letter,
            "lower": letter.lower(),
            "words": letters.get(letter) or [],
            "type": "Vowel" if letter in "AEIOU" else "Consonant",
        }
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ]


@ensure_csrf_cookie
@require_GET
def letters_worksheets_book(request):
    blocked = require_feature(request, "book_download_level1", UPGRADE_VIP_OR_FULL_MESSAGE)
    if blocked:
        return blocked

    return render(request, "letters_worksheets_book.html", {
        "letters": letter_worksheet_book_items(),
    })


def draw_centered_text(pdf, x, y, text, font="Helvetica-Bold", size=18, color=colors.black):
    pdf.setFillColor(color)
    pdf.setFont(font, size)
    pdf.drawCentredString(x, y, str(text))


def letters_book_emoji_font_path():
    candidates = [
        Path("C:/Windows/Fonts/seguiemj.ttf"),
        Path("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


@lru_cache(maxsize=128)
def letters_book_emoji_image(emoji):
    emoji = str(emoji or "").strip()
    if not emoji:
        return None
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        return None

    font_path = letters_book_emoji_font_path()
    if not font_path:
        return None

    try:
        image = Image.new("RGBA", (120, 120), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(str(font_path), 72)
        bbox = draw.textbbox((0, 0), emoji, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (120 - text_width) / 2 - bbox[0]
        y = (120 - text_height) / 2 - bbox[1] - 2
        draw.text((x, y), emoji, font=font, fill=(30, 41, 59, 255))
        output = BytesIO()
        image.save(output, format="PNG")
        output.seek(0)
        return ImageReader(output)
    except Exception:
        return None


def draw_letters_book_pdf(letters):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    blue = colors.HexColor("#4361ee")
    pink = colors.HexColor("#f72585")
    slate = colors.HexColor("#1e293b")
    muted = colors.HexColor("#64748b")
    line = colors.HexColor("#cbd5e1")
    soft_blue = colors.HexColor("#f0f9ff")
    soft_pink = colors.HexColor("#fff0f5")
    soft_gray = colors.HexColor("#f8fafc")

    def header(letter):
        pdf.setStrokeColor(blue)
        pdf.setLineWidth(2)
        pdf.roundRect(10 * mm, 10 * mm, width - 20 * mm, height - 20 * mm, 10 * mm, stroke=1, fill=0)
        pdf.setFillColor(blue)
        pdf.circle(28 * mm, height - 27 * mm, 9 * mm, stroke=0, fill=1)
        draw_centered_text(pdf, 28 * mm, height - 30 * mm, letter, size=24, color=colors.white)
        pdf.setFillColor(slate)
        pdf.setFont("Helvetica-Bold", 22)
        pdf.drawString(42 * mm, height - 25 * mm, f"Letter {letter} Worksheet")
        pdf.setFillColor(muted)
        pdf.setFont("Helvetica", 11)
        pdf.drawString(42 * mm, height - 31 * mm, f"Learn the letter {letter}")
        pdf.setStrokeColor(line)
        pdf.line(16 * mm, height - 39 * mm, width - 16 * mm, height - 39 * mm)
        pdf.setFont("Helvetica", 10)
        pdf.setFillColor(slate)
        pdf.drawRightString(width - 16 * mm, height - 25 * mm, "Name: ____________________")
        pdf.drawRightString(width - 16 * mm, height - 32 * mm, "Date: ____________________")

    def draw_picture_box(x, y, word, size=23 * mm):
        pdf.setStrokeColor(line)
        pdf.setFillColor(colors.white)
        pdf.roundRect(x, y, size, size, 6 * mm, stroke=1, fill=1)
        image = letters_book_emoji_image(word.get("emoji"))
        if image:
            pdf.drawImage(
                image,
                x + 4 * mm,
                y + 4 * mm,
                width=size - 8 * mm,
                height=size - 8 * mm,
                mask="auto",
                preserveAspectRatio=True,
                anchor="c",
            )
        else:
            pdf.setFillColor(blue)
            pdf.circle(x + size / 2, y + size / 2, size / 3, stroke=0, fill=1)
            draw_centered_text(
                pdf,
                x + size / 2,
                y + size / 2 - 4,
                str(word.get("word") or "?")[:1].upper(),
                size=18,
                color=colors.white,
            )

    def draw_word_box(x, y, word):
        pdf.setStrokeColor(line)
        pdf.setFillColor(soft_gray)
        pdf.roundRect(x, y, 74 * mm, 13 * mm, 4 * mm, stroke=1, fill=1)
        image = letters_book_emoji_image(word.get("emoji"))
        if image:
            pdf.drawImage(image, x + 3 * mm, y + 3 * mm, width=7 * mm, height=7 * mm, mask="auto")
            word_x = x + 13 * mm
        else:
            word_x = x + 5 * mm
        pdf.setFillColor(slate)
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(word_x, y + 4 * mm, str(word.get("word") or "").lower())
        pdf.setFillColor(colors.HexColor("#94a3b8"))
        pdf.setFont("Helvetica", 16)
        pdf.drawRightString(x + 69 * mm, y + 4 * mm, "________")

    # Cover
    pdf.setFillColor(colors.white)
    pdf.rect(0, 0, width, height, stroke=0, fill=1)
    pdf.setFillColor(blue)
    pdf.roundRect(width / 2 - 22 * mm, height - 78 * mm, 44 * mm, 44 * mm, 8 * mm, stroke=0, fill=1)
    draw_centered_text(pdf, width / 2, height - 61 * mm, "PGL", size=30, color=colors.white)
    draw_centered_text(pdf, width / 2, height - 95 * mm, "Phonics Game Lab", size=18, color=blue)
    draw_centered_text(pdf, width / 2, height - 118 * mm, "English Letters Worksheets Book", size=28, color=slate)
    draw_centered_text(pdf, width / 2, height - 135 * mm, "A-Z printable phonics workbook", font="Helvetica", size=18, color=muted)
    pdf.setFillColor(slate)
    pdf.setFont("Helvetica", 16)
    pdf.drawString(28 * mm, height - 180 * mm, "Student name: ______________________________")
    pdf.drawString(28 * mm, height - 194 * mm, "Class: _____________________________________")
    pdf.drawString(28 * mm, height - 208 * mm, "Date: ______________________________________")
    pdf.showPage()

    for item in letters:
        letter = item["letter"]
        lower = item["lower"]
        words = item.get("words") or []
        first = words[0] if words else {"word": lower, "emoji": ""}
        first_word = first["word"] if words else lower

        header(letter)

        y = height - 52 * mm
        pdf.setStrokeColor(line)
        pdf.setFillColor(soft_gray)
        pdf.roundRect(16 * mm, y - 38 * mm, 82 * mm, 38 * mm, 6 * mm, stroke=1, fill=1)
        pdf.setFillColor(pink)
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(22 * mm, y - 9 * mm, "Color:")
        draw_centered_text(pdf, 57 * mm, y - 31 * mm, f"{letter}  {lower}", size=54, color=slate)

        pdf.setFillColor(soft_blue)
        pdf.roundRect(106 * mm, y - 38 * mm, 88 * mm, 38 * mm, 6 * mm, stroke=1, fill=1)
        draw_picture_box(112 * mm, y - 32 * mm, first, size=24 * mm)
        draw_centered_text(pdf, 157 * mm, y - 17 * mm, first_word.upper(), font="Helvetica-Bold", size=27, color=colors.HexColor("#0284c7"))
        draw_centered_text(pdf, 157 * mm, y - 29 * mm, f"{first_word.lower()} starts with {letter}", font="Helvetica", size=10, color=colors.HexColor("#0284c7"))

        y -= 50 * mm
        pdf.setStrokeColor(line)
        pdf.setFillColor(colors.white)
        pdf.roundRect(16 * mm, y - 50 * mm, width - 32 * mm, 50 * mm, 6 * mm, stroke=1, fill=1)
        pdf.setFillColor(pink)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(22 * mm, y - 9 * mm, "Trace and Write:")
        trace_rows = [
            (letter, "   ".join([letter] * 7)),
            (lower, "   ".join([lower] * 7)),
            (f"{letter}{lower}", "   ".join([f"{letter}{lower}"] * 6)),
        ]
        row_y = y - 20 * mm
        for label, trace in trace_rows:
            pdf.setStrokeColor(colors.HexColor("#94a3b8"))
            pdf.line(28 * mm, row_y - 2 * mm, width - 24 * mm, row_y - 2 * mm)
            pdf.setFillColor(slate)
            pdf.setFont("Helvetica-Bold", 24)
            pdf.drawString(23 * mm, row_y, label)
            pdf.setFillColor(colors.HexColor("#cbd5e1"))
            pdf.setFont("Courier", 24)
            pdf.drawString(50 * mm, row_y, trace)
            row_y -= 12 * mm

        y -= 61 * mm
        pdf.setFillColor(pink)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(16 * mm, y, "Trace the Words:")
        word_y = y - 18 * mm
        for index, word in enumerate(words[:5]):
            x = 16 * mm if index % 2 == 0 else 106 * mm
            if index and index % 2 == 0:
                word_y -= 17 * mm
            draw_word_box(x, word_y, word)

        y = 62 * mm
        pdf.setStrokeColor(line)
        pdf.setFillColor(soft_pink)
        pdf.roundRect(16 * mm, y - 38 * mm, width - 32 * mm, 38 * mm, 6 * mm, stroke=1, fill=1)
        pdf.setFillColor(colors.HexColor("#db2777"))
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(22 * mm, y - 10 * mm, f"Find and Circle the letter '{letter}':")
        cloud = [letter, "B", letter, "D", lower, "m", letter, "s", lower, "T", "R", letter, "n", lower]
        pdf.setFillColor(colors.HexColor("#475569"))
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawCentredString(width / 2, y - 26 * mm, "   ".join(cloud))

        pdf.setFillColor(colors.HexColor("#94a3b8"))
        pdf.setFont("Helvetica", 9)
        pdf.drawCentredString(width / 2, 14 * mm, "Great Job! - Phonics Game Lab")
        pdf.showPage()

    pdf.save()
    return buffer.getvalue()


def docx_escape(value):
    return escape(str(value or ""), {'"': "&quot;"})


def docx_run(text, *, bold=False, size=22, color=None):
    props = [
        '<w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>',
        f'<w:sz w:val="{int(size)}"/>',
        f'<w:szCs w:val="{int(size)}"/>',
    ]
    if bold:
        props.append("<w:b/>")
    if color:
        props.append(f'<w:color w:val="{color}"/>')
    return (
        "<w:r><w:rPr>"
        + "".join(props)
        + f'</w:rPr><w:t xml:space="preserve">{docx_escape(text)}</w:t></w:r>'
    )


def docx_paragraph(text="", *, bold=False, size=22, color=None, align=None):
    paragraph_props = f'<w:pPr><w:jc w:val="{align}"/></w:pPr>' if align else ""
    return f"<w:p>{paragraph_props}{docx_run(text, bold=bold, size=size, color=color)}</w:p>"


def docx_page_break():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def docx_cell(content, *, width=4500, shade=None, valign="center"):
    shade_xml = f'<w:shd w:fill="{shade}"/>' if shade else ""
    return (
        "<w:tc>"
        f'<w:tcPr><w:tcW w:w="{width}" w:type="dxa"/><w:vAlign w:val="{valign}"/>{shade_xml}</w:tcPr>'
        f"{content}"
        "</w:tc>"
    )


def docx_table(rows, *, border_color="CBD5E1"):
    borders = "".join(
        f'<w:{edge} w:val="single" w:sz="8" w:space="0" w:color="{border_color}"/>'
        for edge in ["top", "left", "bottom", "right", "insideH", "insideV"]
    )
    row_xml = []
    for row in rows:
        row_xml.append("<w:tr>" + "".join(row) + "</w:tr>")
    return (
        "<w:tbl>"
        f'<w:tblPr><w:tblW w:w="0" w:type="auto"/><w:tblBorders>{borders}</w:tblBorders>'
        '<w:tblCellMar><w:top w:w="120" w:type="dxa"/><w:left w:w="160" w:type="dxa"/>'
        '<w:bottom w:w="120" w:type="dxa"/><w:right w:w="160" w:type="dxa"/></w:tblCellMar></w:tblPr>'
        + "".join(row_xml)
        + "</w:tbl>"
    )


def build_letters_book_docx(letters):
    body = []
    body.append(docx_paragraph("PGL", bold=True, size=64, color="4361EE", align="center"))
    body.append(docx_paragraph("Phonics Game Lab", bold=True, size=32, color="2563EB", align="center"))
    body.append(docx_paragraph("English Letters Worksheets Book", bold=True, size=44, color="111827", align="center"))
    body.append(docx_paragraph("A-Z printable phonics workbook", bold=True, size=28, color="64748B", align="center"))
    body.append(docx_paragraph(""))
    body.append(docx_paragraph("Student name: ______________________________", size=26))
    body.append(docx_paragraph("Class: _____________________________________", size=26))
    body.append(docx_paragraph("Date: ______________________________________", size=26))
    body.append(docx_page_break())

    for index, item in enumerate(letters):
        letter = item["letter"]
        lower = item["lower"]
        words = item.get("words") or []
        first = words[0] if words else {"word": lower, "emoji": ""}
        first_word = str(first.get("word") or lower).lower()

        body.append(docx_table([
            [
                docx_cell(docx_paragraph(letter, bold=True, size=34, color="FFFFFF", align="center"), width=900, shade="4361EE"),
                docx_cell(
                    docx_paragraph(f"Letter {letter} Worksheet", bold=True, size=30, color="111827")
                    + docx_paragraph(f"Learn the letter {letter}", size=18, color="64748B"),
                    width=5600,
                ),
                docx_cell(
                    docx_paragraph("Name: ____________________", size=16)
                    + docx_paragraph("Date: ____________________", size=16),
                    width=3000,
                ),
            ],
        ]))
        body.append(docx_paragraph(""))

        body.append(docx_table([
            [
                docx_cell(
                    docx_paragraph("Color:", bold=True, size=18, color="F72585")
                    + docx_paragraph(f"{letter}  {lower}", bold=True, size=70, color="111827", align="center"),
                    width=4600,
                    shade="F8FAFC",
                ),
                docx_cell(
                    docx_paragraph(str(first.get("emoji") or ""), size=42, align="center")
                    + docx_paragraph(first_word.upper(), bold=True, size=42, color="0284C7", align="center")
                    + docx_paragraph(f"{first_word} starts with {letter}", size=18, color="0284C7", align="center"),
                    width=4600,
                    shade="F0F9FF",
                ),
            ],
        ]))
        body.append(docx_paragraph(""))

        trace_rows = [
            (letter, "    ".join([letter] * 7)),
            (lower, "    ".join([lower] * 7)),
            (f"{letter}{lower}", "    ".join([f"{letter}{lower}"] * 5)),
        ]
        body.append(docx_paragraph("Trace and Write:", bold=True, size=20, color="F72585"))
        body.append(docx_table([
            [
                docx_cell(docx_paragraph(label, bold=True, size=30), width=900),
                docx_cell(docx_paragraph(trace, size=28, color="CBD5E1"), width=8200),
            ]
            for label, trace in trace_rows
        ]))
        body.append(docx_paragraph(""))

        body.append(docx_paragraph("Trace the Words:", bold=True, size=20, color="F72585"))
        word_rows = []
        for word_index in range(0, len(words[:5]), 2):
            row = []
            for word in words[word_index:word_index + 2]:
                label = f'{word.get("emoji") or ""}  {str(word.get("word") or "").lower()}      __________'
                row.append(docx_cell(docx_paragraph(label, bold=True, size=22), width=4600, shade="F8FAFC"))
            if len(row) == 1:
                row.append(docx_cell(docx_paragraph(""), width=4600, shade="F8FAFC"))
            word_rows.append(row)
        body.append(docx_table(word_rows))
        body.append(docx_paragraph(""))

        cloud = "   ".join([letter, "B", letter, "D", lower, "m", letter, "s", lower, "T", "R", letter, "n", lower])
        body.append(docx_table([
            [
                docx_cell(
                    docx_paragraph(f"Find and Circle the letter '{letter}':", bold=True, size=20, color="F72585")
                    + docx_paragraph(cloud, bold=True, size=28, color="475569", align="center"),
                    width=9200,
                    shade="FFF0F5",
                )
            ],
        ]))
        body.append(docx_paragraph("Great Job! - Phonics Game Lab", size=16, color="94A3B8", align="center"))
        if index < len(letters) - 1:
            body.append(docx_page_break())

    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {''.join(body)}
    <w:sectPr>
      <w:pgSz w:w="11906" w:h="16838"/>
      <w:pgMar w:top="720" w:right="720" w:bottom="720" w:left="720" w:header="360" w:footer="360" w:gutter="0"/>
      <w:pgBorders w:offsetFrom="page">
        <w:top w:val="single" w:sz="18" w:space="18" w:color="4361EE"/>
        <w:left w:val="single" w:sz="18" w:space="18" w:color="4361EE"/>
        <w:bottom w:val="single" w:sz="18" w:space="18" w:color="4361EE"/>
        <w:right w:val="single" w:sz="18" w:space="18" w:color="4361EE"/>
      </w:pgBorders>
    </w:sectPr>
  </w:body>
</w:document>"""

    styles_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/><w:sz w:val="22"/></w:rPr>
  </w:style>
</w:styles>"""

    buffer = BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>""")
        archive.writestr("_rels/.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>""")
        archive.writestr("word/_rels/document.xml.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>""")
        archive.writestr("word/document.xml", document_xml)
        archive.writestr("word/styles.xml", styles_xml)
    return buffer.getvalue()


@ensure_csrf_cookie
@require_GET
def letters_worksheets_book_pdf(request):
    blocked = require_feature(request, "book_download_level1", UPGRADE_VIP_OR_FULL_MESSAGE)
    if blocked:
        return blocked

    pdf_bytes = draw_letters_book_pdf(letter_worksheet_book_items())
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="english_letters_worksheets_book.pdf"'
    return response


@ensure_csrf_cookie
@require_GET
def letters_worksheets_book_word(request):
    blocked = require_feature(request, "book_download_level1", UPGRADE_VIP_OR_FULL_MESSAGE)
    if blocked:
        return blocked

    docx_bytes = build_letters_book_docx(letter_worksheet_book_items())
    response = HttpResponse(
        docx_bytes,
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    response["Content-Disposition"] = 'attachment; filename="english_letters_worksheets_book.docx"'
    return response


@ensure_csrf_cookie
@require_GET
def games_view(request):
    blocked = require_feature(request, "internal_games", "ألعاب الموقع الداخلية متاحة في Basic أو باقة أعلى.")
    if blocked:
        return blocked

    progress = get_english_foundation_progress_map(request.user).get("games")
    return render(request, "games.html", {
        "points": progress.points if progress else 0,
        "actions_count": progress.actions_count if progress else 0,
        "completed": progress.completed if progress else False,
    })


def english_games(request):
    return games_view(request)


@ensure_csrf_cookie
@require_GET
def level_four_view(request):
    return render_level_four_page(request, "overview")


LEVEL_FOUR_WORKSHEETS = [
    {
        "slug": "reading",
        "title": "Reading Worksheet",
        "ar": "ورقة عمل القراءة",
        "description": "قطعة قراءة قصيرة مع أسئلة فهم وكلمات ومعاني وسؤال كتابة.",
        "questions": 21,
        "time": "30 دقيقة",
        "url_name": "level_four_worksheet_reading",
        "blocks": [
            {"title": "Reading Passage", "text": "Omar visits the school library every week. He chooses a short English story, writes new words in his notebook, and talks about the story with his friend.", "questions": ["What does Omar visit every week?", "What does he write in his notebook?", "Who does he talk with?", "True or False: Omar reads English stories.", "Write one sentence about your favorite place at school."]},
            {"title": "Vocabulary", "questions": ["library = ____________", "story = ____________", "friend = ____________", "notebook = ____________", "week = ____________"]},
        ],
    },
    {
        "slug": "listening",
        "title": "Listening Worksheet",
        "ar": "ورقة عمل الاستماع",
        "description": "جمل يقرأها المعلم أو يشغلها بالنطق مع اختيار وإكمال وصح أو خطأ.",
        "questions": 10,
        "time": "20 دقيقة",
        "url_name": "level_four_worksheet_listening",
        "blocks": [
            {"title": "Teacher Script", "text": "Teacher reads: I finished my homework yesterday. The weather is sunny today. Can you help me, please?", "questions": ["What did the speaker finish?", "How is the weather?", "What does the speaker ask for?", "Complete: I finished my ______ yesterday.", "True or False: The speaker asks for help."]},
            {"title": "Listen and Choose", "questions": ["ticket / doctor / market", "sunny / rainy / cold", "help / shirt / water", "homework / breakfast / game", "airport / classroom / kitchen"]},
        ],
    },
    {
        "slug": "speaking",
        "title": "Speaking Worksheet",
        "ar": "ورقة عمل التحدث",
        "description": "مهام تحدث مع checklist للتقييم ومساحة ملاحظات للمعلم.",
        "questions": 6,
        "time": "25 دقيقة",
        "url_name": "level_four_worksheet_speaking",
        "blocks": [
            {"title": "Speaking Missions", "questions": ["Introduce yourself in four sentences.", "Talk about your school.", "Describe your favorite hobby.", "Ask a friend for help.", "Order food politely.", "Talk about a healthy habit."]},
            {"title": "Teacher Checklist", "questions": ["Clear voice", "Good word choice", "Enough words", "Good effort", "Teacher notes"]},
        ],
    },
    {
        "slug": "writing",
        "title": "Writing Worksheet",
        "ar": "ورقة عمل الكتابة",
        "description": "مهام كتابة قصيرة مع كلمات مساعدة وChecklist.",
        "questions": 5,
        "time": "30 دقيقة",
        "url_name": "level_four_worksheet_writing",
        "blocks": [
            {"title": "Writing Tasks", "questions": ["Write about yourself.", "Write about your school day.", "Write about your best friend.", "Write a short dialogue.", "Write about your future dream."]},
            {"title": "Checklist", "questions": ["Capital letter", "Full stop", "Enough words", "Clear meaning", "Target words used"]},
        ],
    },
    {
        "slug": "stories",
        "title": "Story Worksheet",
        "ar": "ورقة عمل القصص",
        "description": "قصة قصيرة مع ترتيب أحداث وأسئلة فهم ونهاية مختلفة.",
        "questions": 12,
        "time": "30 دقيقة",
        "url_name": "level_four_worksheet_stories",
        "blocks": [
            {"title": "Short Story", "text": "Sara lost her bag after school. Her friend helped her look in the classroom, the library, and the bus area. At last, they found it near the office.", "questions": ["Who lost the bag?", "Where did they look?", "Where did they find it?", "Order the events: found bag / looked in library / lost bag", "Write a different ending."]},
            {"title": "Important Words", "questions": ["lost", "helped", "classroom", "library", "office"]},
        ],
    },
    {
        "slug": "exam-review",
        "title": "Exam Review Worksheet",
        "ar": "ورقة مراجعة الاختبار",
        "description": "مراجعة نهائية للمفردات والقواعد والقراءة والاستماع والكتابة والتحدث.",
        "questions": 27,
        "time": "40 دقيقة",
        "url_name": "level_four_worksheet_exam_review",
        "blocks": [
            {"title": "Vocabulary and Grammar", "questions": ["honest means ______", "Choose: She ____ happy.", "Complete: I drink ____ every day.", "Correct: He play football.", "Choose: There ____ trees."]},
            {"title": "Reading, Listening, Writing, Speaking", "questions": ["Read a short text and answer five questions.", "Listen and answer five questions.", "Write about your school day.", "Introduce yourself and talk about your hobby.", "Final teacher rating."]},
        ],
    },
]


def level_four_worksheet_items():
    return [
        {
            **item,
            "url": reverse(item["url_name"]),
        }
        for item in LEVEL_FOUR_WORKSHEETS
    ]


def render_level_four_page(request, section_mode, **extra):
    blocked = require_feature(request, "level_four", UPGRADE_LEVEL_FOUR_MESSAGE)
    if blocked:
        return blocked

    context = {"section_mode": section_mode, **extra}
    return render(request, "level_four.html", context)


@ensure_csrf_cookie
@require_GET
def level_four_reading_view(request):
    return render_level_four_page(request, "reading")


@ensure_csrf_cookie
@require_GET
def level_four_listening_view(request):
    return render_level_four_page(request, "listening")


@ensure_csrf_cookie
@require_GET
def level_four_speaking_view(request):
    return render_level_four_page(request, "speaking")


@ensure_csrf_cookie
@require_GET
def level_four_writing_view(request):
    return render_level_four_page(request, "writing")


@ensure_csrf_cookie
@require_GET
def level_four_stories_view(request):
    return render_level_four_page(request, "stories")


@ensure_csrf_cookie
@require_GET
def level_four_exam_view(request):
    return render_level_four_page(request, "exam")


@ensure_csrf_cookie
@require_GET
def level_four_worksheets_view(request):
    return render_level_four_page(request, "worksheets", worksheets=level_four_worksheet_items())


@ensure_csrf_cookie
@require_GET
def level_four_worksheet_detail_view(request, worksheet_type):
    worksheet = next((item for item in level_four_worksheet_items() if item["slug"] == worksheet_type), None)
    if worksheet is None:
        raise Http404("Worksheet not found")
    return render_level_four_page(request, "worksheet_detail", worksheet=worksheet)


@ensure_csrf_cookie
@require_GET
def common_sentences_worksheet(request):
    blocked = require_feature(request, "level_four", UPGRADE_LEVEL_FOUR_MESSAGE)
    if blocked:
        return blocked

    return render(request, "worksheets/common_sentences_worksheet.html")


@login_required
@require_GET
def profile_dashboard(request):
    synchronize_user_subscription_compatibility(request.user)
    subscription_summary = subscription_dashboard_context(request.user)
    profile = get_or_create_student_profile(request.user)
    profile.is_vip = has_feature(request.user, "parent_report_detailed")
    bird_progress = getattr(request.user, "bird_tutor_progress", None)
    sound_progress = getattr(request.user, "sound_practice_progress", None)
    cvc_reading_progress = getattr(request.user, "cvc_reading_progress", None)
    letter_progress_qs = LetterProgress.objects.filter(user=request.user)
    completed_letters_qs = letter_progress_qs.filter(completed=True).order_by("-completed_at", "-last_updated_at")
    completed_letters_count = completed_letters_qs.count()
    recent_completed_letters = list(completed_letters_qs[:5])
    last_completed_letter = recent_completed_letters[0] if recent_completed_letters else None
    average_score = letter_progress_qs.aggregate(avg_score=models.Avg("total_score"))["avg_score"]
    review_items = []
    mastered_items = []

    if has_feature(request.user, "parent_report_detailed"):
        review_items = list(
            BirdReviewItem.objects
            .filter(user=request.user, mastered=False)
            .order_by("-updated_at", "letter", "word")[:20]
        )
        mastered_items = list(
            BirdReviewItem.objects
            .filter(user=request.user, mastered=True)
            .order_by("-updated_at", "letter", "word")[:20]
        )

    total_questions = bird_progress.total_questions if bird_progress else 0
    correct_answers = bird_progress.correct_answers if bird_progress else 0
    success_rate = round((correct_answers / total_questions) * 100) if total_questions else 0
    sound_completed_items = sound_progress.completed_items or [] if sound_progress else []
    sound_completed_count = len(sound_completed_items)
    sound_word_practice_count = len([item for item in sound_completed_items if str(item).startswith("word:")])
    sound_total_items = (
        sum(len(row["sounds"]) + len(row["words"]) for row in SOUND_SYLLABLE_ROWS)
        + len(SOUND_CVC_WORDS)
        + len(SOUND_QUIZ_QUESTIONS)
        + sound_pattern_total_units()
        + 6
    )
    sound_mastery_rate = round((sound_completed_count / sound_total_items) * 100) if sound_total_items else 0
    sound_quiz_rate = round((sound_progress.quiz_correct / sound_progress.quiz_attempts) * 100) if sound_progress and sound_progress.quiz_attempts else 0
    sound_mic_rate = round((sound_progress.mic_success / sound_progress.mic_attempts) * 100) if sound_progress and sound_progress.mic_attempts else 0
    vowel_quiz_rate = round((sound_progress.vowel_quiz_correct / sound_progress.vowel_quiz_attempts) * 100) if sound_progress and sound_progress.vowel_quiz_attempts else 0
    vowel_mic_rate = round((sound_progress.vowel_microphone_success / sound_progress.vowel_microphone_attempts) * 100) if sound_progress and sound_progress.vowel_microphone_attempts else 0
    cvc_words_total = CVCWord.objects.count()
    cvc_sentences_total = CVCSentence.objects.count()
    cvc_stories_total = CVCStory.objects.count()
    cvc_words_practiced_count = len(cvc_reading_progress.words_practiced or []) if cvc_reading_progress else 0
    cvc_words_mastered_count = len(cvc_reading_progress.words_mastered or []) if cvc_reading_progress else 0
    cvc_quiz_rate = round((cvc_reading_progress.quiz_correct / cvc_reading_progress.quiz_attempts) * 100) if cvc_reading_progress and cvc_reading_progress.quiz_attempts else 0
    cvc_mic_rate = round((cvc_reading_progress.mic_success / cvc_reading_progress.mic_attempts) * 100) if cvc_reading_progress and cvc_reading_progress.mic_attempts else 0
    cvc_sentences_mastered_count = len(cvc_reading_progress.sentences_mastered or []) if cvc_reading_progress else 0
    cvc_sentence_quiz_rate = round((cvc_reading_progress.sentence_quiz_correct / cvc_reading_progress.sentence_quiz_attempts) * 100) if cvc_reading_progress and cvc_reading_progress.sentence_quiz_attempts else 0
    cvc_sentence_mic_rate = round((cvc_reading_progress.sentence_microphone_success / cvc_reading_progress.sentence_microphone_attempts) * 100) if cvc_reading_progress and cvc_reading_progress.sentence_microphone_attempts else 0
    cvc_stories_started_count = len(cvc_reading_progress.stories_started or []) if cvc_reading_progress else 0
    cvc_story_quiz_rate = round((cvc_reading_progress.story_quiz_correct / cvc_reading_progress.story_quiz_attempts) * 100) if cvc_reading_progress and cvc_reading_progress.story_quiz_attempts else 0
    cvc_story_mic_rate = round((cvc_reading_progress.story_microphone_success / cvc_reading_progress.story_microphone_attempts) * 100) if cvc_reading_progress and cvc_reading_progress.story_microphone_attempts else 0
    cvc_pronouns_practiced_count = len(cvc_reading_progress.pronouns_practiced or []) if cvc_reading_progress else 0
    cvc_pronouns_mastered_count = len(cvc_reading_progress.pronouns_mastered or []) if cvc_reading_progress else 0
    cvc_pronoun_quiz_rate = round((cvc_reading_progress.pronoun_quiz_correct / cvc_reading_progress.pronoun_quiz_attempts) * 100) if cvc_reading_progress and cvc_reading_progress.pronoun_quiz_attempts else 0
    cvc_pronoun_mic_rate = round((cvc_reading_progress.pronoun_microphone_success / cvc_reading_progress.pronoun_microphone_attempts) * 100) if cvc_reading_progress and cvc_reading_progress.pronoun_microphone_attempts else 0
    sight_words_practiced_count = len(cvc_reading_progress.sight_words_practiced or []) if cvc_reading_progress else 0
    sight_words_mastered_count = len(cvc_reading_progress.sight_words_mastered or []) if cvc_reading_progress else 0
    sight_word_quiz_rate = round((cvc_reading_progress.sight_word_quiz_correct / cvc_reading_progress.sight_word_quiz_attempts) * 100) if cvc_reading_progress and cvc_reading_progress.sight_word_quiz_attempts else 0
    question_words_mastered_count = len(cvc_reading_progress.question_words_mastered or []) if cvc_reading_progress else 0
    action_verbs_mastered_count = len(cvc_reading_progress.action_verbs_mastered or []) if cvc_reading_progress else 0
    adjectives_mastered_count = len(cvc_reading_progress.adjectives_mastered or []) if cvc_reading_progress else 0
    english_foundation_sections = english_foundation_context_for_user(request.user)
    english_foundation_points = sum(section["points"] for section in english_foundation_sections)
    english_foundation_completed = len([section for section in english_foundation_sections if section["completed"]])

    payment_orders = list(PaymentOrder.objects.filter(user=request.user).order_by("-created_at")[:20])
    checkout_cutoff = timezone.now() - timedelta(
        minutes=getattr(settings, "MOYASAR_ORDER_REUSE_MINUTES", 30)
    )
    for payment_order in payment_orders:
        payment_order.reopen_checkout_url = ""
        if (
            payment_order.provider == PaymentOrder.Provider.MOYASAR
            and payment_order.status == PaymentOrder.Status.INITIATED
            and payment_order.created_at >= checkout_cutoff
            and payment_order.checkout_url
        ):
            try:
                payment_order.reopen_checkout_url = validate_moyasar_checkout_url(
                    payment_order.checkout_url
                )
            except MoyasarInvalidResponseError:
                pass

    return render(request, "accounts/profile_dashboard.html", {
        "profile": profile,
        "bird_progress": bird_progress,
        "sound_progress": sound_progress,
        "sound_mastery_rate": sound_mastery_rate,
        "sound_completed_count": sound_completed_count,
        "sound_word_practice_count": sound_word_practice_count,
        "sound_quiz_rate": sound_quiz_rate,
        "sound_mic_rate": sound_mic_rate,
        "vowel_mastery_rate": sound_progress.vowel_mastery_percentage if sound_progress else 0,
        "vowel_quiz_rate": vowel_quiz_rate,
        "vowel_mic_rate": vowel_mic_rate,
        "vowel_lessons_completed": sound_progress.vowel_lessons_completed if sound_progress else 0,
        "last_vowel_practiced": sound_progress.last_vowel_practiced if sound_progress else "",
        "cvc_reading_progress": cvc_reading_progress,
        "cvc_mastery_rate": cvc_reading_progress.cvc_mastery_percentage if cvc_reading_progress else 0,
        "cvc_words_total": cvc_words_total,
        "cvc_sentences_total": cvc_sentences_total,
        "cvc_stories_total": cvc_stories_total,
        "cvc_words_practiced_count": cvc_words_practiced_count,
        "cvc_words_mastered_count": cvc_words_mastered_count,
        "cvc_quiz_rate": cvc_quiz_rate,
        "cvc_mic_rate": cvc_mic_rate,
        "cvc_sentences_mastered_count": cvc_sentences_mastered_count,
        "cvc_sentence_quiz_rate": cvc_sentence_quiz_rate,
        "cvc_sentence_mic_rate": cvc_sentence_mic_rate,
        "cvc_stories_started_count": cvc_stories_started_count,
        "cvc_story_quiz_rate": cvc_story_quiz_rate,
        "cvc_story_mic_rate": cvc_story_mic_rate,
        "cvc_pronouns_practiced_count": cvc_pronouns_practiced_count,
        "cvc_pronouns_mastered_count": cvc_pronouns_mastered_count,
        "cvc_pronoun_quiz_rate": cvc_pronoun_quiz_rate,
        "cvc_pronoun_mic_rate": cvc_pronoun_mic_rate,
        "sight_words_practiced_count": sight_words_practiced_count,
        "sight_words_mastered_count": sight_words_mastered_count,
        "sight_word_quiz_rate": sight_word_quiz_rate,
        "question_words_mastered_count": question_words_mastered_count,
        "action_verbs_mastered_count": action_verbs_mastered_count,
        "adjectives_mastered_count": adjectives_mastered_count,
        "english_foundation_sections": english_foundation_sections,
        "english_foundation_points": english_foundation_points,
        "english_foundation_completed": english_foundation_completed,
        "review_items": review_items,
        "mastered_items": mastered_items,
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "wrong_answers": bird_progress.wrong_answers if bird_progress else 0,
        "bird_xp": bird_progress.xp if bird_progress else 0,
        "success_rate": success_rate,
        "letter_progress_count": completed_letters_count,
        "last_completed_letter": last_completed_letter,
        "average_letter_score": round(average_score or 0),
        "recent_completed_letters": recent_completed_letters,
        "has_letter_progress": letter_progress_qs.exists(),
        "payment_orders": payment_orders,
        "subscription_summary": subscription_summary,
    })


@ensure_csrf_cookie
@require_GET
def index(request):
    profile = get_or_create_student_profile(request.user)
    profile_payload = serialize_student_profile(profile)
    is_developer_vip_preview = False
    is_vip_user = has_feature(request.user, "bird_tutor")
    level_one_plan = get_subscription_plan(request.user)

    return render(request, "letters.html", {
        "is_authenticated": request.user.is_authenticated,
        "is_premium_user": has_feature(request.user, "letters_full"),
        "is_vip_user": is_vip_user,
        "level_one_plan": level_one_plan,
        "level_one_disabled_features": level_one_disabled_features(request.user),
        "is_developer_vip_preview": is_developer_vip_preview,
        "phonics_user_id": str(request.user.id) if request.user.is_authenticated else "",
        "phonics_user_email": request.user.email if request.user.is_authenticated else "",
        "student_profile_json": json.dumps(profile_payload, ensure_ascii=False),
        "bird_lottie_files_json": json.dumps(get_existing_bird_lottie_files(), ensure_ascii=False),
    })


SOUND_SYLLABLE_ROWS = [
    {"letter": "b", "arabic": "ب", "sounds": ["ba", "be", "bi", "bo", "bu"], "words": ["bat", "bed", "bin", "bug"]},
    {"letter": "c", "arabic": "ك", "sounds": ["ca", "ce", "ci", "co", "cu"], "words": ["cat", "cap", "cup", "cot"]},
    {"letter": "d", "arabic": "د", "sounds": ["da", "de", "di", "do", "du"], "words": ["dog", "dad", "dig", "dot"]},
    {"letter": "f", "arabic": "ف", "sounds": ["fa", "fe", "fi", "fo", "fu"], "words": ["fan", "fig", "fox", "fun"]},
    {"letter": "g", "arabic": "ج", "sounds": ["ga", "ge", "gi", "go", "gu"], "words": ["gap", "gum", "gas", "got"]},
    {"letter": "h", "arabic": "هـ", "sounds": ["ha", "he", "hi", "ho", "hu"], "words": ["hat", "hen", "hop", "hut"]},
    {"letter": "j", "arabic": "ج", "sounds": ["ja", "je", "ji", "jo", "ju"], "words": ["jam", "jet", "jug", "job"]},
    {"letter": "k", "arabic": "ك", "sounds": ["ka", "ke", "ki", "ko", "ku"], "words": ["kid", "kit", "key", "kiss"]},
    {"letter": "l", "arabic": "ل", "sounds": ["la", "le", "li", "lo", "lu"], "words": ["leg", "lip", "log", "lap"]},
    {"letter": "m", "arabic": "م", "sounds": ["ma", "me", "mi", "mo", "mu"], "words": ["man", "map", "mop", "mud"]},
    {"letter": "n", "arabic": "ن", "sounds": ["na", "ne", "ni", "no", "nu"], "words": ["net", "nap", "nut", "nod"]},
    {"letter": "p", "arabic": "ب", "sounds": ["pa", "pe", "pi", "po", "pu"], "words": ["pen", "pig", "pot", "pin"]},
    {"letter": "r", "arabic": "ر", "sounds": ["ra", "re", "ri", "ro", "ru"], "words": ["rat", "red", "run", "rug"]},
    {"letter": "s", "arabic": "س", "sounds": ["sa", "se", "si", "so", "su"], "words": ["sun", "sit", "sad", "sip"]},
    {"letter": "t", "arabic": "ت", "sounds": ["ta", "te", "ti", "to", "tu"], "words": ["top", "ten", "tap", "tub"]},
]


SOUND_CVC_WORDS = [
    {"word": "cat", "arabic": "قطة", "family": "-at", "image": "🐱", "sound": "short a", "prompt": "c-a-t"},
    {"word": "bat", "arabic": "خفاش", "family": "-at", "image": "🦇", "sound": "short a", "prompt": "b-a-t"},
    {"word": "mat", "arabic": "حصيرة", "family": "-at", "image": "▦", "sound": "short a", "prompt": "m-a-t"},
    {"word": "hat", "arabic": "قبعة", "family": "-at", "image": "🎩", "sound": "short a", "prompt": "h-a-t"},
    {"word": "sat", "arabic": "جلس", "family": "-at", "image": "🪑", "sound": "short a", "prompt": "s-a-t"},
    {"word": "fan", "arabic": "مروحة", "family": "-an", "image": "🌬️", "sound": "short a", "prompt": "f-a-n"},
    {"word": "man", "arabic": "رجل", "family": "-an", "image": "👨", "sound": "short a", "prompt": "m-a-n"},
    {"word": "pan", "arabic": "مقلاة", "family": "-an", "image": "🍳", "sound": "short a", "prompt": "p-a-n"},
    {"word": "can", "arabic": "علبة", "family": "-an", "image": "🥫", "sound": "short a", "prompt": "c-a-n"},
    {"word": "map", "arabic": "خريطة", "family": "-ap", "image": "🗺️", "sound": "short a", "prompt": "m-a-p"},
    {"word": "cap", "arabic": "قبعة", "family": "-ap", "image": "🧢", "sound": "short a", "prompt": "c-a-p"},
    {"word": "tap", "arabic": "ينقر", "family": "-ap", "image": "👆", "sound": "short a", "prompt": "t-a-p"},
    {"word": "nap", "arabic": "غفوة", "family": "-ap", "image": "💤", "sound": "short a", "prompt": "n-a-p"},
    {"word": "pen", "arabic": "قلم", "family": "-en", "image": "🖊️", "sound": "short e", "prompt": "p-e-n"},
    {"word": "hen", "arabic": "دجاجة", "family": "-en", "image": "🐔", "sound": "short e", "prompt": "h-e-n"},
    {"word": "ten", "arabic": "عشرة", "family": "-en", "image": "🔟", "sound": "short e", "prompt": "t-e-n"},
    {"word": "men", "arabic": "رجال", "family": "-en", "image": "👥", "sound": "short e", "prompt": "m-e-n"},
    {"word": "bed", "arabic": "سرير", "family": "-ed", "image": "🛏️", "sound": "short e", "prompt": "b-e-d"},
    {"word": "red", "arabic": "أحمر", "family": "-ed", "image": "🟥", "sound": "short e", "prompt": "r-e-d"},
    {"word": "leg", "arabic": "ساق", "family": "-eg", "image": "🦵", "sound": "short e", "prompt": "l-e-g"},
    {"word": "net", "arabic": "شبكة", "family": "-et", "image": "#", "sound": "short e", "prompt": "n-e-t"},
    {"word": "pet", "arabic": "حيوان أليف", "family": "-et", "image": "🐾", "sound": "short e", "prompt": "p-e-t"},
    {"word": "web", "arabic": "شبكة", "family": "-eb", "image": "🕸️", "sound": "short e", "prompt": "w-e-b"},
    {"word": "pig", "arabic": "خنزير", "family": "-ig", "image": "🐷", "sound": "short i", "prompt": "p-i-g"},
    {"word": "wig", "arabic": "شعر مستعار", "family": "-ig", "image": "🎭", "sound": "short i", "prompt": "w-i-g"},
    {"word": "dig", "arabic": "يحفر", "family": "-ig", "image": "⛏️", "sound": "short i", "prompt": "d-i-g"},
    {"word": "big", "arabic": "كبير", "family": "-ig", "image": "⬆️", "sound": "short i", "prompt": "b-i-g"},
    {"word": "sit", "arabic": "يجلس", "family": "-it", "image": "🪑", "sound": "short i", "prompt": "s-i-t"},
    {"word": "hit", "arabic": "يضرب", "family": "-it", "image": "🎯", "sound": "short i", "prompt": "h-i-t"},
    {"word": "pin", "arabic": "دبوس", "family": "-in", "image": "📌", "sound": "short i", "prompt": "p-i-n"},
    {"word": "fin", "arabic": "زعنفة", "family": "-in", "image": "🐟", "sound": "short i", "prompt": "f-i-n"},
    {"word": "lip", "arabic": "شفة", "family": "-ip", "image": "👄", "sound": "short i", "prompt": "l-i-p"},
    {"word": "zip", "arabic": "سحاب", "family": "-ip", "image": "🤐", "sound": "short i", "prompt": "z-i-p"},
    {"word": "dog", "arabic": "كلب", "family": "-og", "image": "🐶", "sound": "short o", "prompt": "d-o-g"},
    {"word": "log", "arabic": "جذع", "family": "-og", "image": "🪵", "sound": "short o", "prompt": "l-o-g"},
    {"word": "fog", "arabic": "ضباب", "family": "-og", "image": "🌫️", "sound": "short o", "prompt": "f-o-g"},
    {"word": "jog", "arabic": "يركض ببطء", "family": "-og", "image": "🏃", "sound": "short o", "prompt": "j-o-g"},
    {"word": "hot", "arabic": "حار", "family": "-ot", "image": "🔥", "sound": "short o", "prompt": "h-o-t"},
    {"word": "pot", "arabic": "قدر", "family": "-ot", "image": "🍲", "sound": "short o", "prompt": "p-o-t"},
    {"word": "box", "arabic": "صندوق", "family": "-ox", "image": "📦", "sound": "short o", "prompt": "b-o-x"},
    {"word": "fox", "arabic": "ثعلب", "family": "-ox", "image": "🦊", "sound": "short o", "prompt": "f-o-x"},
    {"word": "mop", "arabic": "ممسحة", "family": "-op", "image": "🧹", "sound": "short o", "prompt": "m-o-p"},
    {"word": "top", "arabic": "قمة", "family": "-op", "image": "🔝", "sound": "short o", "prompt": "t-o-p"},
    {"word": "sun", "arabic": "شمس", "family": "-un", "image": "☀️", "sound": "short u", "prompt": "s-u-n"},
    {"word": "run", "arabic": "يركض", "family": "-un", "image": "🏃", "sound": "short u", "prompt": "r-u-n"},
    {"word": "fun", "arabic": "مرح", "family": "-un", "image": "🎉", "sound": "short u", "prompt": "f-u-n"},
    {"word": "bun", "arabic": "خبز صغير", "family": "-un", "image": "🥯", "sound": "short u", "prompt": "b-u-n"},
    {"word": "cup", "arabic": "كوب", "family": "-up", "image": "☕", "sound": "short u", "prompt": "c-u-p"},
    {"word": "bus", "arabic": "حافلة", "family": "-us", "image": "🚌", "sound": "short u", "prompt": "b-u-s"},
    {"word": "bug", "arabic": "حشرة", "family": "-ug", "image": "🐞", "sound": "short u", "prompt": "b-u-g"},
    {"word": "rug", "arabic": "سجادة", "family": "-ug", "image": "🧶", "sound": "short u", "prompt": "r-u-g"},
    {"word": "mud", "arabic": "طين", "family": "-ud", "image": "🟫", "sound": "short u", "prompt": "m-u-d"},
    {"word": "nut", "arabic": "جوزة", "family": "-ut", "image": "🥜", "sound": "short u", "prompt": "n-u-t"},
]


SOUND_QUIZ_QUESTIONS = [
    {"id": "q1", "type": "sound_hunter", "question": "اختر الكلمة التي تحتوي على short a", "answer": "cat", "options": ["cat", "pen", "dog", "sun"]},
    {"id": "q2", "type": "family", "question": "أي كلمة تنتمي لعائلة -ig؟", "answer": "pig", "options": ["sun", "pig", "hat", "box"]},
    {"id": "q3", "type": "listen", "question": "استمع للكلمة ثم اختر عائلتها", "answer": "-og", "options": ["-at", "-og", "-un", "-en"], "listen": "dog"},
    {"id": "q4", "type": "build", "question": "رتب أصوات كلمة cup", "answer": "c-u-p", "options": ["c-u-p", "p-u-c", "c-a-p", "u-c-p"]},
    {"id": "q5", "type": "meaning", "question": "أي كلمة معناها شمس؟", "answer": "sun", "options": ["run", "sun", "sit", "fan"]},
    {"id": "q6", "type": "missing", "question": "أكمل الحرف الناقص: _ox", "answer": "f", "options": ["f", "m", "n", "p"]},
    {"id": "q7", "type": "odd", "question": "اختر الكلمة المختلفة صوتيًا", "answer": "dog", "options": ["cat", "hat", "mat", "dog"]},
]


VOWEL_LESSONS = [
    {
        "letter": "A",
        "name": "Letter A",
        "short_sound": "short a مثل cat",
        "long_sound": "long a مثل cake",
        "silent_note": "في كلمات مثل bread وsaid قد يكون صوت A ضعيفًا أو مختلفًا عن الاسم.",
        "badge": "A Master",
        "question": {
            "text": "ما صوت حرف A في كلمة cat؟",
            "answer": "short a",
            "options": ["short a", "long a", "silent"],
        },
        "examples": [
            {"word": "apple", "arabic": "تفاحة", "visual_hint": "🍎", "sound_type": "short", "position": "beginning", "vowel": "a", "question": "أين يقع A في apple؟"},
            {"word": "ant", "arabic": "نملة", "visual_hint": "🐜", "sound_type": "short", "position": "beginning", "vowel": "a", "question": "هل A في ant قصير؟"},
            {"word": "axe", "arabic": "فأس", "visual_hint": "🪓", "sound_type": "short", "position": "beginning", "vowel": "a", "question": "ما أول حرف علة في axe؟"},
            {"word": "cat", "arabic": "قطة", "visual_hint": "🐱", "sound_type": "short", "position": "middle", "vowel": "a", "question": "ما صوت A في cat؟"},
            {"word": "hat", "arabic": "قبعة", "visual_hint": "🎩", "sound_type": "short", "position": "middle", "vowel": "a", "question": "اختر صوت A في hat."},
            {"word": "map", "arabic": "خريطة", "visual_hint": "🗺️", "sound_type": "short", "position": "middle", "vowel": "a", "question": "أين يقع A في map؟"},
            {"word": "cake", "arabic": "كعكة", "visual_hint": "🎂", "sound_type": "long", "position": "middle", "vowel": "a", "silent": "e", "question": "ماذا يفعل Silent E في cake؟"},
            {"word": "name", "arabic": "اسم", "visual_hint": "🏷️", "sound_type": "long", "position": "middle", "vowel": "a", "silent": "e", "question": "هل A في name طويل؟"},
            {"word": "rain", "arabic": "مطر", "visual_hint": "🌧️", "sound_type": "long", "position": "middle", "vowel": "a", "question": "ما نوع صوت A في rain؟"},
            {"word": "play", "arabic": "يلعب", "visual_hint": "🎮", "sound_type": "long", "position": "middle", "vowel": "a", "question": "ما الصوت الطويل في play؟"},
            {"word": "train", "arabic": "قطار", "visual_hint": "🚆", "sound_type": "long", "position": "middle", "vowel": "a", "question": "استمع وحدد صوت A في train."},
            {"word": "bread", "arabic": "خبز", "visual_hint": "🍞", "sound_type": "silent-like", "position": "middle", "vowel": "a", "question": "هل A في bread يقول اسمه؟"},
            {"word": "head", "arabic": "رأس", "visual_hint": "🙂", "sound_type": "silent-like", "position": "middle", "vowel": "a", "question": "A في head صوتها ضعيف أم طويل؟"},
            {"word": "said", "arabic": "قال", "visual_hint": "💬", "sound_type": "silent-like", "position": "middle", "vowel": "a", "question": "استمع إلى said: هل A واضحة؟"},
            {"word": "again", "arabic": "مرة أخرى", "visual_hint": "🔁", "sound_type": "silent-like", "position": "middle", "vowel": "a", "question": "ما الصوت الأقرب لـ A في again؟"},
            {"word": "idea", "arabic": "فكرة", "visual_hint": "💡", "sound_type": "ending", "position": "ending", "vowel": "a", "question": "أين يقع A في idea؟"},
            {"word": "sofa", "arabic": "أريكة", "visual_hint": "🛋️", "sound_type": "ending", "position": "ending", "vowel": "a", "question": "هل A في نهاية sofa؟"},
            {"word": "banana", "arabic": "موز", "visual_hint": "🍌", "sound_type": "ending", "position": "ending", "vowel": "a", "question": "كم A تسمع في banana؟"},
        ],
    },
    {
        "letter": "E",
        "name": "Letter E",
        "short_sound": "short e مثل egg",
        "long_sound": "long e مثل tree",
        "silent_note": "Silent E في نهاية الكلمة غالبًا لا يُنطق، لكنه يجعل حرف العلة السابق طويلًا: cap تصبح cape.",
        "badge": "E Master",
        "question": {
            "text": "ماذا يفعل Silent E في كلمة cape؟",
            "answer": "يجعل a طويلًا",
            "options": ["يجعل a طويلًا", "ينطق بصوت e", "يحذف الحرف الأول"],
        },
        "magic_pairs": [
            {"from": "cap", "to": "cape"},
            {"from": "kit", "to": "kite"},
            {"from": "hop", "to": "hope"},
        ],
        "examples": [
            {"word": "egg", "arabic": "بيضة", "visual_hint": "🥚", "sound_type": "short", "position": "beginning", "vowel": "e", "question": "ما صوت E في egg؟"},
            {"word": "elephant", "arabic": "فيل", "visual_hint": "🐘", "sound_type": "short", "position": "beginning", "vowel": "e", "question": "أين يقع E في elephant؟"},
            {"word": "exit", "arabic": "خروج", "visual_hint": "🚪", "sound_type": "short", "position": "beginning", "vowel": "e", "question": "ما أول حرف علة في exit؟"},
            {"word": "pen", "arabic": "قلم", "visual_hint": "🖊️", "sound_type": "short", "position": "middle", "vowel": "e", "question": "هل E في pen قصيرة؟"},
            {"word": "bed", "arabic": "سرير", "visual_hint": "🛏️", "sound_type": "short", "position": "middle", "vowel": "e", "question": "اختر صوت E في bed."},
            {"word": "red", "arabic": "أحمر", "visual_hint": "🟥", "sound_type": "short", "position": "middle", "vowel": "e", "question": "ما حرف العلة في red؟"},
            {"word": "he", "arabic": "هو", "visual_hint": "👦", "sound_type": "long", "position": "ending", "vowel": "e", "question": "هل E في he طويلة؟"},
            {"word": "she", "arabic": "هي", "visual_hint": "👧", "sound_type": "long", "position": "ending", "vowel": "e", "question": "استمع إلى she وحدد الصوت."},
            {"word": "me", "arabic": "أنا", "visual_hint": "🙋", "sound_type": "long", "position": "ending", "vowel": "e", "question": "أين يقع E في me؟"},
            {"word": "tree", "arabic": "شجرة", "visual_hint": "🌳", "sound_type": "long", "position": "ending", "vowel": "e", "question": "ما الصوت الطويل في tree؟"},
            {"word": "green", "arabic": "أخضر", "visual_hint": "🟩", "sound_type": "long", "position": "middle", "vowel": "e", "question": "هل صوت ee طويل؟"},
            {"word": "cake", "arabic": "كعكة", "visual_hint": "🎂", "sound_type": "silent", "position": "ending", "vowel": "e", "silent": "e", "question": "أي حرف صامت في cake؟"},
            {"word": "bike", "arabic": "دراجة", "visual_hint": "🚲", "sound_type": "silent", "position": "ending", "vowel": "e", "silent": "e", "question": "ما الحرف الصامت في bike؟"},
            {"word": "home", "arabic": "منزل", "visual_hint": "🏠", "sound_type": "silent", "position": "ending", "vowel": "e", "silent": "e", "question": "هل E في home ينطق؟"},
            {"word": "name", "arabic": "اسم", "visual_hint": "🏷️", "sound_type": "silent", "position": "ending", "vowel": "e", "silent": "e", "question": "Silent E يجعل A ماذا؟"},
            {"word": "time", "arabic": "وقت", "visual_hint": "⏰", "sound_type": "silent", "position": "ending", "vowel": "e", "silent": "e", "question": "ضع خطًا تحت Silent E في time."},
        ],
    },
    {
        "letter": "I",
        "name": "Letter I",
        "short_sound": "short i مثل pig",
        "long_sound": "long i مثل ice",
        "silent_note": "قد يكون صوت I غير واضح في كلمات مثل business وfruit وbuild.",
        "badge": "I Master",
        "question": {
            "text": "ما صوت I في pig؟",
            "answer": "short i",
            "options": ["short i", "long i", "silent"],
        },
        "examples": [
            {"word": "igloo", "arabic": "بيت جليدي", "visual_hint": "🧊", "sound_type": "short", "position": "beginning", "vowel": "i", "question": "أين يقع I في igloo؟"},
            {"word": "insect", "arabic": "حشرة", "visual_hint": "🐞", "sound_type": "short", "position": "beginning", "vowel": "i", "question": "هل I في insect قصيرة؟"},
            {"word": "ink", "arabic": "حبر", "visual_hint": "🖋️", "sound_type": "short", "position": "beginning", "vowel": "i", "question": "ما أول حرف علة في ink؟"},
            {"word": "pig", "arabic": "خنزير", "visual_hint": "🐷", "sound_type": "short", "position": "middle", "vowel": "i", "question": "ما صوت I في pig؟"},
            {"word": "sit", "arabic": "يجلس", "visual_hint": "🪑", "sound_type": "short", "position": "middle", "vowel": "i", "question": "حدد حرف العلة في sit."},
            {"word": "fish", "arabic": "سمكة", "visual_hint": "🐟", "sound_type": "short", "position": "middle", "vowel": "i", "question": "هل I في fish قصيرة؟"},
            {"word": "lip", "arabic": "شفة", "visual_hint": "👄", "sound_type": "short", "position": "middle", "vowel": "i", "question": "أين يقع I في lip؟"},
            {"word": "ice", "arabic": "ثلج", "visual_hint": "🧊", "sound_type": "long", "position": "beginning", "vowel": "i", "question": "هل I في ice طويل؟"},
            {"word": "bike", "arabic": "دراجة", "visual_hint": "🚲", "sound_type": "long", "position": "middle", "vowel": "i", "silent": "e", "question": "ماذا يفعل Silent E في bike؟"},
            {"word": "time", "arabic": "وقت", "visual_hint": "⏰", "sound_type": "long", "position": "middle", "vowel": "i", "silent": "e", "question": "ما صوت I في time؟"},
            {"word": "five", "arabic": "خمسة", "visual_hint": "5️⃣", "sound_type": "long", "position": "middle", "vowel": "i", "silent": "e", "question": "هل I في five يقول اسمه؟"},
            {"word": "kite", "arabic": "طائرة ورقية", "visual_hint": "🪁", "sound_type": "long", "position": "middle", "vowel": "i", "silent": "e", "question": "ما الحرف الصامت في kite؟"},
            {"word": "business", "arabic": "عمل", "visual_hint": "💼", "sound_type": "silent-like", "position": "middle", "vowel": "i", "question": "هل كل I في business واضح؟"},
            {"word": "fruit", "arabic": "فاكهة", "visual_hint": "🍇", "sound_type": "silent-like", "position": "middle", "vowel": "i", "question": "استمع: هل I في fruit قوي؟"},
            {"word": "build", "arabic": "يبني", "visual_hint": "🏗️", "sound_type": "silent-like", "position": "middle", "vowel": "i", "question": "ما الحرف غير الواضح في build؟"},
            {"word": "ski", "arabic": "تزلج", "visual_hint": "🎿", "sound_type": "ending", "position": "ending", "vowel": "i", "question": "أين يقع I في ski؟"},
            {"word": "taxi", "arabic": "تاكسي", "visual_hint": "🚕", "sound_type": "ending", "position": "ending", "vowel": "i", "question": "ما آخر حرف علة في taxi؟"},
            {"word": "kiwi", "arabic": "كيوي", "visual_hint": "🥝", "sound_type": "ending", "position": "ending", "vowel": "i", "question": "هل I في نهاية kiwi؟"},
        ],
    },
    {
        "letter": "O",
        "name": "Letter O",
        "short_sound": "short o مثل dog",
        "long_sound": "long o مثل go",
        "silent_note": "قد لا يظهر صوت O واضحًا في كلمات خاصة مثل people وleopard وcolonel.",
        "badge": "O Master",
        "question": {
            "text": "ما صوت O في dog؟",
            "answer": "short o",
            "options": ["short o", "long o", "silent"],
        },
        "examples": [
            {"word": "octopus", "arabic": "أخطبوط", "visual_hint": "🐙", "sound_type": "short", "position": "beginning", "vowel": "o", "question": "أين يقع O في octopus؟"},
            {"word": "ox", "arabic": "ثور", "visual_hint": "🐂", "sound_type": "short", "position": "beginning", "vowel": "o", "question": "ما أول حرف علة في ox؟"},
            {"word": "orange", "arabic": "برتقال", "visual_hint": "🍊", "sound_type": "short", "position": "beginning", "vowel": "o", "question": "هل O في orange في البداية؟"},
            {"word": "dog", "arabic": "كلب", "visual_hint": "🐶", "sound_type": "short", "position": "middle", "vowel": "o", "question": "ما صوت O في dog؟"},
            {"word": "hot", "arabic": "حار", "visual_hint": "🔥", "sound_type": "short", "position": "middle", "vowel": "o", "question": "حدد حرف العلة في hot."},
            {"word": "box", "arabic": "صندوق", "visual_hint": "📦", "sound_type": "short", "position": "middle", "vowel": "o", "question": "هل O في box قصيرة؟"},
            {"word": "open", "arabic": "يفتح", "visual_hint": "🔓", "sound_type": "long", "position": "beginning", "vowel": "o", "question": "هل O في open طويلة؟"},
            {"word": "go", "arabic": "يذهب", "visual_hint": "➡️", "sound_type": "long", "position": "ending", "vowel": "o", "question": "أين يقع O في go؟"},
            {"word": "home", "arabic": "منزل", "visual_hint": "🏠", "sound_type": "long", "position": "middle", "vowel": "o", "silent": "e", "question": "ماذا يفعل Silent E في home؟"},
            {"word": "boat", "arabic": "قارب", "visual_hint": "⛵", "sound_type": "long", "position": "middle", "vowel": "o", "question": "ما الصوت الطويل في boat؟"},
            {"word": "snow", "arabic": "ثلج", "visual_hint": "❄️", "sound_type": "long", "position": "middle", "vowel": "o", "question": "هل O في snow طويلة؟"},
            {"word": "people", "arabic": "ناس", "visual_hint": "👥", "sound_type": "silent-like", "position": "middle", "vowel": "o", "question": "هل O في people واضح؟"},
            {"word": "leopard", "arabic": "فهد", "visual_hint": "🐆", "sound_type": "silent-like", "position": "middle", "vowel": "o", "question": "استمع إلى leopard وحدد O."},
            {"word": "colonel", "arabic": "عقيد", "visual_hint": "🎖️", "sound_type": "silent-like", "position": "middle", "vowel": "o", "question": "هل O في colonel ينطق كما يكتب؟"},
            {"word": "no", "arabic": "لا", "visual_hint": "🚫", "sound_type": "long", "position": "ending", "vowel": "o", "question": "أين يقع O في no؟"},
            {"word": "hero", "arabic": "بطل", "visual_hint": "🦸", "sound_type": "ending", "position": "ending", "vowel": "o", "question": "هل O في نهاية hero؟"},
        ],
    },
    {
        "letter": "U",
        "name": "Letter U",
        "short_sound": "short u مثل sun",
        "long_sound": "long u مثل use",
        "silent_note": "U بعد G أحيانًا لا يُنطق بوضوح مثل guess وguitar وguard.",
        "badge": "U Master",
        "question": {
            "text": "ما صوت U في cup؟",
            "answer": "short u",
            "options": ["short u", "long u", "silent"],
        },
        "examples": [
            {"word": "umbrella", "arabic": "مظلة", "visual_hint": "☂️", "sound_type": "short", "position": "beginning", "vowel": "u", "question": "أين يقع U في umbrella؟"},
            {"word": "up", "arabic": "أعلى", "visual_hint": "⬆️", "sound_type": "short", "position": "beginning", "vowel": "u", "question": "هل U في up قصيرة؟"},
            {"word": "under", "arabic": "تحت", "visual_hint": "⬇️", "sound_type": "short", "position": "beginning", "vowel": "u", "question": "ما أول حرف علة في under؟"},
            {"word": "sun", "arabic": "شمس", "visual_hint": "☀️", "sound_type": "short", "position": "middle", "vowel": "u", "question": "ما صوت U في sun؟"},
            {"word": "cup", "arabic": "كوب", "visual_hint": "☕", "sound_type": "short", "position": "middle", "vowel": "u", "question": "حدد حرف العلة في cup."},
            {"word": "bus", "arabic": "حافلة", "visual_hint": "🚌", "sound_type": "short", "position": "middle", "vowel": "u", "question": "هل U في bus قصيرة؟"},
            {"word": "use", "arabic": "يستخدم", "visual_hint": "🧰", "sound_type": "long", "position": "beginning", "vowel": "u", "silent": "e", "question": "هل U في use طويلة؟"},
            {"word": "cute", "arabic": "لطيف", "visual_hint": "😊", "sound_type": "long", "position": "middle", "vowel": "u", "silent": "e", "question": "ما الحرف الصامت في cute؟"},
            {"word": "music", "arabic": "موسيقى", "visual_hint": "🎵", "sound_type": "long", "position": "middle", "vowel": "u", "question": "هل U في music طويلة؟"},
            {"word": "student", "arabic": "طالب", "visual_hint": "🎒", "sound_type": "long", "position": "middle", "vowel": "u", "question": "استمع إلى U في student."},
            {"word": "cube", "arabic": "مكعب", "visual_hint": "🧊", "sound_type": "long", "position": "middle", "vowel": "u", "silent": "e", "question": "ماذا يفعل Silent E في cube؟"},
            {"word": "guess", "arabic": "يخمن", "visual_hint": "❓", "sound_type": "silent", "position": "middle", "vowel": "u", "question": "هل U بعد G واضحة في guess؟"},
            {"word": "guitar", "arabic": "قيثارة", "visual_hint": "🎸", "sound_type": "silent", "position": "middle", "vowel": "u", "question": "ما الحرف الضعيف بعد G في guitar؟"},
            {"word": "guard", "arabic": "حارس", "visual_hint": "🛡️", "sound_type": "silent", "position": "middle", "vowel": "u", "question": "هل U في guard واضحة؟"},
            {"word": "build", "arabic": "يبني", "visual_hint": "🏗️", "sound_type": "silent-like", "position": "middle", "vowel": "u", "question": "أي حرف لا يُنطق بوضوح في build؟"},
            {"word": "menu", "arabic": "قائمة", "visual_hint": "📋", "sound_type": "ending", "position": "ending", "vowel": "u", "question": "أين يقع U في menu؟"},
            {"word": "emu", "arabic": "طائر إيمو", "visual_hint": "🪶", "sound_type": "ending", "position": "ending", "vowel": "u", "question": "هل U في نهاية emu؟"},
            {"word": "flu", "arabic": "إنفلونزا", "visual_hint": "🤒", "sound_type": "ending", "position": "ending", "vowel": "u", "question": "ما آخر حرف علة في flu؟"},
        ],
    },
    {
        "letter": "Y",
        "name": "Letter Y as a vowel",
        "short_sound": "أحيانًا يعطي short i مثل gym",
        "long_sound": "أحيانًا يعطي long i مثل my أو long e مثل happy",
        "silent_note": "Y ليس حرف علة دائمًا، لكنه يعمل كحرف علة عندما لا توجد A/E/I/O/U أو في نهاية الكلمة.",
        "badge": "Y Vowel Star",
        "question": {
            "text": "ما صوت Y في fly؟",
            "answer": "long i",
            "options": ["long i", "long e", "short i"],
        },
        "examples": [
            {"word": "my", "arabic": "لي", "visual_hint": "🙋", "sound_type": "long i", "position": "ending", "vowel": "y", "question": "ما صوت Y في my؟"},
            {"word": "fly", "arabic": "يطير", "visual_hint": "✈️", "sound_type": "long i", "position": "ending", "vowel": "y", "question": "هل Y في fly يعطي long i؟"},
            {"word": "cry", "arabic": "يبكي", "visual_hint": "😢", "sound_type": "long i", "position": "ending", "vowel": "y", "question": "ما صوت Y في cry؟"},
            {"word": "sky", "arabic": "سماء", "visual_hint": "☁️", "sound_type": "long i", "position": "ending", "vowel": "y", "question": "أين يقع Y في sky؟"},
            {"word": "happy", "arabic": "سعيد", "visual_hint": "😊", "sound_type": "long e", "position": "ending", "vowel": "y", "question": "ما صوت Y في happy؟"},
            {"word": "baby", "arabic": "طفل", "visual_hint": "👶", "sound_type": "long e", "position": "ending", "vowel": "y", "question": "هل Y في baby يعطي long e؟"},
            {"word": "gym", "arabic": "نادي", "visual_hint": "🏋️", "sound_type": "short i", "position": "middle", "vowel": "y", "question": "ما صوت Y في gym؟"},
            {"word": "myth", "arabic": "أسطورة", "visual_hint": "📖", "sound_type": "short i", "position": "middle", "vowel": "y", "question": "هل Y في myth مثل short i؟"},
        ],
    },
]


VOWEL_ACTIVITIES = [
    {"id": "hunter", "title": "Vowel Hunter", "prompt": "cat: ما حرف العلة؟", "answer": "a", "options": ["a", "e", "i", "o"]},
    {"id": "long_short", "title": "Short or Long?", "prompt": "cake: اختر نوع الصوت.", "answer": "long a", "options": ["short a", "long a", "silent"]},
    {"id": "magic_e", "title": "Silent E Magic", "prompt": "cap → cape: ماذا حدث؟", "answer": "A صار طويلًا", "options": ["A صار طويلًا", "A اختفى", "E صار قصيرًا"], "note": "Silent E makes A say its name."},
    {"id": "listen_choose", "title": "Listen and Choose", "prompt": "استمع ثم اختر الكلمة الصحيحة.", "answer": "rain", "options": ["run", "rain", "red"], "listen": "rain"},
    {"id": "picture_quiz", "title": "Picture Vowel Quiz", "prompt": "🍎 اختر الكلمة.", "answer": "apple", "options": ["apple", "ant", "egg"]},
    {"id": "fill_vowel", "title": "Fill the Vowel", "prompt": "c_t: اختر الحرف الناقص.", "answer": "a", "options": ["a", "e", "i", "o", "u"]},
    {"id": "position", "title": "Beginning / Middle / End", "prompt": "apple: أين يقع حرف العلة الأول؟", "answer": "البداية", "options": ["البداية", "الوسط", "النهاية"]},
    {"id": "read_aloud", "title": "Read Aloud", "prompt": "اقرأ كلمة cake بالمايك.", "answer": "cake", "options": ["استمع", "ابدأ المايك", "تم"], "listen": "cake", "mic": True},
    {"id": "sorting", "title": "Vowel Sorting", "prompt": "ضع sun تحت أي مجموعة؟", "answer": "short u", "options": ["short a", "short e", "short i", "short o", "short u"]},
    {"id": "silent_letter", "title": "Find the Silent Letter", "prompt": "bike: اختر الحرف الصامت.", "answer": "e", "options": ["b", "i", "k", "e"]},
]


SOUND_PATTERN_GROUPS = [
    {
        "id": "digraphs",
        "title": "حرفان يعطيان صوتا واحدا",
        "subtitle": "Digraphs",
        "explanation": "عندما يجتمع حرفان قد نسمع صوتا جديدا لا يساوي نطق كل حرف وحده.",
        "patterns": [
            {
                "pattern": "sh",
                "sound": "/sh/",
                "arabic_sound": "ش",
                "rule": "s + h يصبحان صوت /sh/ مثل ship.",
                "examples": [
                    {"word": "ship", "arabic": "سفينة", "visual_hint": "🚢", "note": "sh في بداية الكلمة"},
                    {"word": "fish", "arabic": "سمكة", "visual_hint": "🐟", "note": "sh في نهاية الكلمة"},
                    {"word": "shop", "arabic": "متجر", "visual_hint": "🏬", "note": "استمع لصوت ش"},
                ],
            },
            {
                "pattern": "ch",
                "sound": "/ch/",
                "arabic_sound": "تش",
                "rule": "c + h يعطيان صوت /ch/ مثل chair.",
                "examples": [
                    {"word": "chair", "arabic": "كرسي", "visual_hint": "🪑", "note": "ch في البداية"},
                    {"word": "cheese", "arabic": "جبن", "visual_hint": "🧀", "note": "صوت تش واضح"},
                    {"word": "lunch", "arabic": "غداء", "visual_hint": "🥪", "note": "ch في النهاية"},
                ],
            },
            {
                "pattern": "th",
                "sound": "/th/",
                "arabic_sound": "ث / ذ",
                "rule": "th له صوتان: خفيف مثل three، ومهتز مثل this.",
                "examples": [
                    {"word": "three", "arabic": "ثلاثة", "visual_hint": "3️⃣", "note": "th خفيف مثل ث"},
                    {"word": "thumb", "arabic": "إبهام", "visual_hint": "👍", "note": "th خفيف"},
                    {"word": "this", "arabic": "هذا", "visual_hint": "👉", "note": "th مهتز مثل ذ"},
                ],
            },
            {
                "pattern": "ph",
                "sound": "/f/",
                "arabic_sound": "ف",
                "rule": "ph غالبا ينطق /f/ مثل phone.",
                "examples": [
                    {"word": "phone", "arabic": "هاتف", "visual_hint": "📱", "note": "ph = f"},
                    {"word": "photo", "arabic": "صورة", "visual_hint": "📷", "note": "لا ننطق p وحدها"},
                    {"word": "graph", "arabic": "رسم بياني", "visual_hint": "📈", "note": "ph في النهاية"},
                ],
            },
            {
                "pattern": "ck",
                "sound": "/k/",
                "arabic_sound": "ك",
                "rule": "ck يعطي صوت /k/ واحدا غالبا بعد حرف علة قصير.",
                "examples": [
                    {"word": "duck", "arabic": "بطة", "visual_hint": "🦆", "note": "ck في النهاية"},
                    {"word": "sock", "arabic": "جورب", "visual_hint": "🧦", "note": "صوت ك واحد"},
                    {"word": "back", "arabic": "خلف / ظهر", "visual_hint": "↩️", "note": "short a ثم ck"},
                ],
            },
            {
                "pattern": "ng",
                "sound": "/ng/",
                "arabic_sound": "نغ",
                "rule": "ng في نهاية الكلمة يعطي صوتا أنفيا مثل sing.",
                "examples": [
                    {"word": "sing", "arabic": "يغني", "visual_hint": "🎤", "note": "ng في النهاية"},
                    {"word": "ring", "arabic": "خاتم / يرن", "visual_hint": "💍", "note": "استمع للنهاية"},
                    {"word": "king", "arabic": "ملك", "visual_hint": "👑", "note": "g لا تنفصل هنا"},
                ],
            },
        ],
    },
    {
        "id": "trigraphs",
        "title": "ثلاثة أحرف تصنع صوتا واحدا",
        "subtitle": "Trigraphs",
        "explanation": "بعض الكلمات فيها ثلاثة أحرف متجاورة تعطي صوتا جديدا مثل igh في night.",
        "patterns": [
            {
                "pattern": "igh",
                "sound": "/ai/",
                "arabic_sound": "آي",
                "rule": "igh يعطي long i مثل night و light.",
                "examples": [
                    {"word": "night", "arabic": "ليل", "visual_hint": "🌙", "note": "igh = long i"},
                    {"word": "light", "arabic": "ضوء", "visual_hint": "💡", "note": "لا ننطق gh"},
                    {"word": "high", "arabic": "عال", "visual_hint": "⬆️", "note": "صوت آي"},
                ],
            },
            {
                "pattern": "tch",
                "sound": "/ch/",
                "arabic_sound": "تش",
                "rule": "tch يعطي صوت /ch/ بعد حرف علة قصير.",
                "examples": [
                    {"word": "watch", "arabic": "ساعة / يشاهد", "visual_hint": "⌚", "note": "tch في النهاية"},
                    {"word": "catch", "arabic": "يمسك", "visual_hint": "🤲", "note": "صوت تش"},
                    {"word": "match", "arabic": "مباراة / عود ثقاب", "visual_hint": "🔥", "note": "لا تفصل t عن ch"},
                ],
            },
            {
                "pattern": "dge",
                "sound": "/j/",
                "arabic_sound": "ج",
                "rule": "dge يعطي صوت /j/ مثل bridge.",
                "examples": [
                    {"word": "bridge", "arabic": "جسر", "visual_hint": "🌉", "note": "dge في النهاية"},
                    {"word": "badge", "arabic": "شارة", "visual_hint": "🏅", "note": "صوت ج"},
                    {"word": "edge", "arabic": "حافة", "visual_hint": "📐", "note": "e تساعد على صوت dge"},
                ],
            },
            {
                "pattern": "air",
                "sound": "/air/",
                "arabic_sound": "إير",
                "rule": "air يعطي صوتا واحدا مثل hair.",
                "examples": [
                    {"word": "air", "arabic": "هواء", "visual_hint": "💨", "note": "الكلمة كلها صوت واحد تقريبا"},
                    {"word": "hair", "arabic": "شعر", "visual_hint": "💇", "note": "air في النهاية"},
                    {"word": "chair", "arabic": "كرسي", "visual_hint": "🪑", "note": "ch ثم air"},
                ],
            },
            {
                "pattern": "ear",
                "sound": "/eer/",
                "arabic_sound": "إير",
                "rule": "ear غالبا يعطي صوت /eer/ مثل hear، وقد يتغير في كلمات أخرى.",
                "examples": [
                    {"word": "ear", "arabic": "أذن", "visual_hint": "👂", "note": "ear = eer"},
                    {"word": "hear", "arabic": "يسمع", "visual_hint": "👂", "note": "h ثم ear"},
                    {"word": "near", "arabic": "قريب", "visual_hint": "📍", "note": "صوت إير"},
                ],
            },
        ],
    },
    {
        "id": "four_letters",
        "title": "أربعة أحرف بصوت مختلف",
        "subtitle": "Four-letter patterns",
        "explanation": "هذه المقاطع تبدو طويلة في الكتابة لكنها تسمع كوحدة صوتية واحدة أو صوتين قصيرين.",
        "patterns": [
            {
                "pattern": "tion",
                "sound": "/shən/",
                "arabic_sound": "شن",
                "rule": "tion في نهاية الكلمة غالبا ينطق /shən/ مثل action.",
                "examples": [
                    {"word": "action", "arabic": "عمل / حركة", "visual_hint": "🎬", "note": "tion = شن"},
                    {"word": "station", "arabic": "محطة", "visual_hint": "🚉", "note": "استمع للنهاية"},
                    {"word": "nation", "arabic": "أمة", "visual_hint": "🌍", "note": "لا ننطق t وحدها"},
                ],
            },
            {
                "pattern": "sion",
                "sound": "/zhən/ أو /shən/",
                "arabic_sound": "جن / شن",
                "rule": "sion قد يكون /zhən/ مثل vision أو /shən/ مثل mission.",
                "examples": [
                    {"word": "vision", "arabic": "رؤية", "visual_hint": "👁️", "note": "sion بصوت zh"},
                    {"word": "mission", "arabic": "مهمة", "visual_hint": "🎯", "note": "sion بصوت sh"},
                    {"word": "decision", "arabic": "قرار", "visual_hint": "✅", "note": "استمع للاختلاف"},
                ],
            },
            {
                "pattern": "ough",
                "sound": "يتغير",
                "arabic_sound": "أو / أوف / آو",
                "rule": "ough من أصعب المقاطع: يتغير صوته حسب الكلمة.",
                "examples": [
                    {"word": "though", "arabic": "مع أن", "visual_hint": "💭", "note": "ough مثل long o"},
                    {"word": "through", "arabic": "من خلال", "visual_hint": "➡️", "note": "ough = oo"},
                    {"word": "rough", "arabic": "خشن", "visual_hint": "🪨", "note": "ough = uff"},
                ],
            },
            {
                "pattern": "eigh",
                "sound": "/ay/",
                "arabic_sound": "إي",
                "rule": "eigh غالبا يعطي صوت long a مثل eight.",
                "examples": [
                    {"word": "eight", "arabic": "ثمانية", "visual_hint": "8️⃣", "note": "eigh = long a"},
                    {"word": "weight", "arabic": "وزن", "visual_hint": "⚖️", "note": "w + eigh"},
                    {"word": "neighbor", "arabic": "جار", "visual_hint": "🏘️", "note": "eigh في وسط الكلمة"},
                ],
            },
            {
                "pattern": "augh",
                "sound": "/aw/",
                "arabic_sound": "أو",
                "rule": "augh غالبا يعطي صوت /aw/ مثل caught.",
                "examples": [
                    {"word": "caught", "arabic": "أمسك / وقع في الفخ", "visual_hint": "🪤", "note": "augh = aw"},
                    {"word": "taught", "arabic": "علّم", "visual_hint": "👩‍🏫", "note": "استمع للصوت الأوسط"},
                    {"word": "daughter", "arabic": "ابنة", "visual_hint": "👧", "note": "augh في وسط الكلمة"},
                ],
            },
        ],
    },
    {
        "id": "silent_letters",
        "title": "الحروف الصامتة",
        "subtitle": "Silent letters",
        "explanation": "بعض الحروف تكتب ولا تنطق. المهم أن يسمع المتعلم الكلمة كاملة ثم يلاحظ الحرف الصامت.",
        "patterns": [
            {
                "pattern": "kn",
                "sound": "k صامت",
                "arabic_sound": "ن",
                "rule": "في بداية kn غالبا لا ننطق k.",
                "examples": [
                    {"word": "knee", "arabic": "ركبة", "visual_hint": "🦵", "note": "k صامت"},
                    {"word": "knife", "arabic": "سكين", "visual_hint": "🔪", "note": "تبدأ بصوت n"},
                    {"word": "know", "arabic": "يعرف", "visual_hint": "🧠", "note": "لا نسمع k"},
                ],
            },
            {
                "pattern": "wr",
                "sound": "w صامت",
                "arabic_sound": "ر",
                "rule": "في بداية wr غالبا لا ننطق w.",
                "examples": [
                    {"word": "write", "arabic": "يكتب", "visual_hint": "✍️", "note": "w صامت"},
                    {"word": "wrong", "arabic": "خطأ", "visual_hint": "❌", "note": "تبدأ بصوت r"},
                    {"word": "wrist", "arabic": "معصم", "visual_hint": "⌚", "note": "لا نسمع w"},
                ],
            },
            {
                "pattern": "mb",
                "sound": "b صامت",
                "arabic_sound": "م",
                "rule": "في نهاية mb غالبا لا ننطق b.",
                "examples": [
                    {"word": "lamb", "arabic": "حمل صغير", "visual_hint": "🐑", "note": "b صامت"},
                    {"word": "comb", "arabic": "مشط", "visual_hint": "🪮", "note": "تنتهي بصوت m"},
                    {"word": "thumb", "arabic": "إبهام", "visual_hint": "👍", "note": "b لا ينطق"},
                ],
            },
            {
                "pattern": "gh",
                "sound": "gh صامت أحيانا",
                "arabic_sound": "لا صوت",
                "rule": "gh قد يكون صامتا مثل light و night.",
                "examples": [
                    {"word": "light", "arabic": "ضوء", "visual_hint": "💡", "note": "gh صامت"},
                    {"word": "night", "arabic": "ليل", "visual_hint": "🌙", "note": "igh يعطي long i"},
                    {"word": "right", "arabic": "يمين / صحيح", "visual_hint": "➡️", "note": "gh لا ينطق"},
                ],
            },
            {
                "pattern": "gn",
                "sound": "g صامت",
                "arabic_sound": "ن",
                "rule": "في بداية gn غالبا لا ننطق g.",
                "examples": [
                    {"word": "gnome", "arabic": "قزم", "visual_hint": "🏡", "note": "g صامت"},
                    {"word": "sign", "arabic": "علامة", "visual_hint": "🪧", "note": "g صامت في النهاية"},
                    {"word": "design", "arabic": "تصميم", "visual_hint": "🎨", "note": "لا نسمع g"},
                ],
            },
        ],
    },
]


SOUND_PATTERN_ACTIVITIES = [
    {
        "id": "digraph_hunter",
        "title": "Digraph Hunter",
        "prompt": "أي كلمة تبدأ بصوت /sh/?",
        "answer": "ship",
        "options": ["ship", "cat", "dog", "sun"],
        "listen": "ship",
    },
    {
        "id": "three_letter_sound",
        "title": "Three-letter Sound",
        "prompt": "اختر الكلمة التي فيها igh بصوت long i.",
        "answer": "night",
        "options": ["night", "not", "net", "nut"],
        "listen": "night",
    },
    {
        "id": "four_letter_sound",
        "title": "Four-letter Pattern",
        "prompt": "tion في action ينطق مثل:",
        "answer": "shən",
        "options": ["shən", "tee-on", "ton", "k"],
        "listen": "action",
    },
    {
        "id": "silent_hunter",
        "title": "Silent Letter Hunter",
        "prompt": "ما الحرف الصامت في write؟",
        "answer": "w",
        "options": ["w", "r", "i", "t"],
        "listen": "write",
    },
    {
        "id": "listen_choose_pattern",
        "title": "Listen and Choose",
        "prompt": "استمع ثم اختر النمط الموجود في الكلمة.",
        "answer": "ph",
        "options": ["ph", "sh", "ch", "th"],
        "listen": "phone",
    },
    {
        "id": "pattern_read_aloud",
        "title": "Read Aloud",
        "prompt": "اقرأ كلمة bridge بالمايك.",
        "answer": "bridge",
        "options": ["استمع", "ابدأ المايك", "dge", "تم"],
        "listen": "bridge",
        "mic": True,
    },
]


# Canonical Level 2 phonics sprint order:
# Digraphs -> Ending Sounds -> Trigraphs -> Advanced patterns preview.
SOUND_PATTERN_GROUPS = [
    {
        "id": "digraphs",
        "title": "الأصوات الثنائية",
        "subtitle": "Digraphs",
        "stage": "بعد CVC",
        "explanation": "حرفان يأتيان معا ليصنعا صوتا واحدا جديدا.",
        "patterns": [
            {
                "pattern": "sh",
                "sound": "/sh/",
                "arabic_sound": "ش",
                "rule": "s + h يعطيان صوت ش.",
                "examples": [
                    {"word": "ship", "arabic": "سفينة", "visual_hint": "🚢", "note": "sh في البداية", "position": "beginning"},
                    {"word": "shop", "arabic": "متجر", "visual_hint": "🏬", "note": "sh في البداية", "position": "beginning"},
                    {"word": "fish", "arabic": "سمكة", "visual_hint": "🐟", "note": "sh في النهاية", "position": "ending"},
                    {"word": "dish", "arabic": "طبق", "visual_hint": "🍽️", "note": "sh في النهاية", "position": "ending"},
                    {"word": "shut", "arabic": "يغلق", "visual_hint": "🚪", "note": "صوت ش واضح", "position": "beginning"},
                ],
            },
            {
                "pattern": "ch",
                "sound": "/ch/",
                "arabic_sound": "تش",
                "rule": "c + h يعطيان صوت تش.",
                "examples": [
                    {"word": "chair", "arabic": "كرسي", "visual_hint": "🪑", "note": "ch في البداية", "position": "beginning"},
                    {"word": "cheese", "arabic": "جبن", "visual_hint": "🧀", "note": "صوت تش", "position": "beginning"},
                    {"word": "chick", "arabic": "كتكوت", "visual_hint": "🐥", "note": "ch في البداية", "position": "beginning"},
                    {"word": "chip", "arabic": "رقاقة", "visual_hint": "🍟", "note": "ch في البداية", "position": "beginning"},
                    {"word": "lunch", "arabic": "غداء", "visual_hint": "🥪", "note": "ch في النهاية", "position": "ending"},
                ],
            },
            {
                "pattern": "th",
                "sound": "/th/",
                "arabic_sound": "ث / ذ",
                "rule": "th له صوت خفيف مثل thin وصوت مهتز مثل this.",
                "examples": [
                    {"word": "thin", "arabic": "نحيف", "visual_hint": "📏", "note": "th خفيف", "position": "beginning"},
                    {"word": "think", "arabic": "يفكر", "visual_hint": "💭", "note": "th خفيف", "position": "beginning"},
                    {"word": "three", "arabic": "ثلاثة", "visual_hint": "3️⃣", "note": "th خفيف", "position": "beginning"},
                    {"word": "this", "arabic": "هذا", "visual_hint": "👉", "note": "th مهتز", "position": "beginning"},
                    {"word": "that", "arabic": "ذلك", "visual_hint": "👈", "note": "th مهتز", "position": "beginning"},
                    {"word": "mother", "arabic": "أم", "visual_hint": "👩", "note": "th في الوسط", "position": "middle"},
                ],
            },
            {
                "pattern": "ph",
                "sound": "/f/",
                "arabic_sound": "ف",
                "rule": "ph ينطق غالبا مثل f.",
                "examples": [
                    {"word": "phone", "arabic": "هاتف", "visual_hint": "📱", "note": "ph = f", "position": "beginning"},
                    {"word": "photo", "arabic": "صورة", "visual_hint": "📷", "note": "ph = f", "position": "beginning"},
                    {"word": "graph", "arabic": "رسم بياني", "visual_hint": "📈", "note": "ph في النهاية", "position": "ending"},
                    {"word": "dolphin", "arabic": "دلفين", "visual_hint": "🐬", "note": "ph في الوسط", "position": "middle"},
                ],
            },
            {
                "pattern": "wh",
                "sound": "/w/",
                "arabic_sound": "و / هوا",
                "rule": "wh يبدأ غالبا بصوت w في كلمات السؤال.",
                "examples": [
                    {"word": "what", "arabic": "ماذا", "visual_hint": "❓", "note": "wh في البداية", "position": "beginning"},
                    {"word": "when", "arabic": "متى", "visual_hint": "⏰", "note": "wh في البداية", "position": "beginning"},
                    {"word": "where", "arabic": "أين", "visual_hint": "📍", "note": "wh في البداية", "position": "beginning"},
                    {"word": "white", "arabic": "أبيض", "visual_hint": "⚪", "note": "wh في البداية", "position": "beginning"},
                    {"word": "whale", "arabic": "حوت", "visual_hint": "🐋", "note": "wh في البداية", "position": "beginning"},
                ],
            },
            {
                "pattern": "ck",
                "sound": "/k/",
                "arabic_sound": "ك",
                "rule": "ck يعطي صوت ك واحدا، وغالبا يأتي في نهاية الكلمة بعد حرف علة قصير.",
                "examples": [
                    {"word": "duck", "arabic": "بطة", "visual_hint": "🦆", "note": "ck في النهاية", "position": "ending"},
                    {"word": "sock", "arabic": "جورب", "visual_hint": "🧦", "note": "ck في النهاية", "position": "ending"},
                    {"word": "back", "arabic": "خلف / ظهر", "visual_hint": "↩️", "note": "ck في النهاية", "position": "ending"},
                    {"word": "neck", "arabic": "رقبة", "visual_hint": "🧣", "note": "ck في النهاية", "position": "ending"},
                    {"word": "kick", "arabic": "يركل", "visual_hint": "🦶", "note": "ck في النهاية", "position": "ending"},
                ],
            },
        ],
    },
    {
        "id": "ending_sounds",
        "title": "الأصوات النهائية",
        "subtitle": "Ending Sounds",
        "stage": "بعد Digraphs",
        "explanation": "نركز هنا على الصوت الذي يظهر في آخر الكلمة حتى يقرأ المتعلم النهاية بثبات.",
        "patterns": [
            {
                "pattern": "ck",
                "sound": "/k/",
                "arabic_sound": "ك",
                "rule": "ck في نهاية الكلمة يعطي صوت ك واحدا.",
                "examples": [
                    {"word": "duck", "arabic": "بطة", "visual_hint": "🦆", "note": "نهاية ck", "position": "ending"},
                    {"word": "sock", "arabic": "جورب", "visual_hint": "🧦", "note": "نهاية ck", "position": "ending"},
                    {"word": "back", "arabic": "خلف / ظهر", "visual_hint": "↩️", "note": "نهاية ck", "position": "ending"},
                    {"word": "kick", "arabic": "يركل", "visual_hint": "🦶", "note": "نهاية ck", "position": "ending"},
                ],
            },
            {
                "pattern": "ng",
                "sound": "/ng/",
                "arabic_sound": "نغ",
                "rule": "ng في النهاية يعطي صوتا أنفيا.",
                "examples": [
                    {"word": "ring", "arabic": "خاتم / يرن", "visual_hint": "💍", "note": "نهاية ng", "position": "ending"},
                    {"word": "sing", "arabic": "يغني", "visual_hint": "🎤", "note": "نهاية ng", "position": "ending"},
                    {"word": "king", "arabic": "ملك", "visual_hint": "👑", "note": "نهاية ng", "position": "ending"},
                    {"word": "wing", "arabic": "جناح", "visual_hint": "🪽", "note": "نهاية ng", "position": "ending"},
                ],
            },
            {
                "pattern": "nk",
                "sound": "/nk/",
                "arabic_sound": "نك",
                "rule": "nk في نهاية الكلمة يمزج n ثم k.",
                "examples": [
                    {"word": "bank", "arabic": "بنك", "visual_hint": "🏦", "note": "نهاية nk", "position": "ending"},
                    {"word": "pink", "arabic": "وردي", "visual_hint": "🌸", "note": "نهاية nk", "position": "ending"},
                    {"word": "sink", "arabic": "حوض", "visual_hint": "🚰", "note": "نهاية nk", "position": "ending"},
                    {"word": "tank", "arabic": "خزان / دبابة", "visual_hint": "🛢️", "note": "نهاية nk", "position": "ending"},
                ],
            },
            {
                "pattern": "ll",
                "sound": "/l/",
                "arabic_sound": "ل",
                "rule": "ll في النهاية يثبت صوت l.",
                "examples": [
                    {"word": "bell", "arabic": "جرس", "visual_hint": "🔔", "note": "نهاية ll", "position": "ending"},
                    {"word": "hill", "arabic": "تل", "visual_hint": "⛰️", "note": "نهاية ll", "position": "ending"},
                    {"word": "ball", "arabic": "كرة", "visual_hint": "⚽", "note": "نهاية ll", "position": "ending"},
                    {"word": "doll", "arabic": "دمية", "visual_hint": "🧸", "note": "نهاية ll", "position": "ending"},
                ],
            },
            {
                "pattern": "ss",
                "sound": "/s/",
                "arabic_sound": "س",
                "rule": "ss في النهاية يعطي صوت s واضحا.",
                "examples": [
                    {"word": "kiss", "arabic": "قبلة", "visual_hint": "💋", "note": "نهاية ss", "position": "ending"},
                    {"word": "mess", "arabic": "فوضى", "visual_hint": "🧺", "note": "نهاية ss", "position": "ending"},
                    {"word": "class", "arabic": "صف", "visual_hint": "🏫", "note": "نهاية ss", "position": "ending"},
                    {"word": "bus", "arabic": "حافلة", "visual_hint": "🚌", "note": "s نهائية مفردة", "position": "ending"},
                ],
            },
            {
                "pattern": "ff",
                "sound": "/f/",
                "arabic_sound": "ف",
                "rule": "ff في النهاية يعطي صوت f واضحا.",
                "examples": [
                    {"word": "off", "arabic": "مغلق / بعيد", "visual_hint": "🔌", "note": "نهاية ff", "position": "ending"},
                    {"word": "puff", "arabic": "ينفخ", "visual_hint": "💨", "note": "نهاية ff", "position": "ending"},
                    {"word": "staff", "arabic": "طاقم", "visual_hint": "👥", "note": "نهاية ff", "position": "ending"},
                    {"word": "cliff", "arabic": "جرف", "visual_hint": "🪨", "note": "نهاية ff", "position": "ending"},
                ],
            },
            {
                "pattern": "zz",
                "sound": "/z/",
                "arabic_sound": "ز",
                "rule": "zz في النهاية يعطي صوت z مهتز.",
                "examples": [
                    {"word": "buzz", "arabic": "طنين", "visual_hint": "🐝", "note": "نهاية zz", "position": "ending"},
                    {"word": "fizz", "arabic": "فوران", "visual_hint": "🥤", "note": "نهاية zz", "position": "ending"},
                ],
            },
        ],
    },
    {
        "id": "trigraphs",
        "title": "الأصوات الثلاثية",
        "subtitle": "Trigraphs",
        "stage": "بعد Ending Sounds",
        "explanation": "بعد الأصوات الثنائية والنهايات، يتعلم المتعلم أن ثلاثة أحرف قد تأتي معا لتكوين صوت أو نمط قراءة جديد.",
        "patterns": [
            {
                "pattern": "tch",
                "sound": "/ch/",
                "arabic_sound": "تش",
                "rule": "tch يعطي غالبا صوت ch ويأتي كثيرا بعد حرف علة قصير في نهاية الكلمة.",
                "examples": [
                    {"word": "catch", "arabic": "يمسك", "visual_hint": "🎣", "note": "نهاية tch", "position": "ending"},
                    {"word": "watch", "arabic": "ساعة / يشاهد", "visual_hint": "⌚", "note": "نهاية tch", "position": "ending"},
                    {"word": "match", "arabic": "عود ثقاب / مباراة", "visual_hint": "🔥", "note": "نهاية tch", "position": "ending"},
                    {"word": "pitch", "arabic": "يرمي / ملعب", "visual_hint": "⚾", "note": "نهاية tch", "position": "ending"},
                    {"word": "stitch", "arabic": "غرزة", "visual_hint": "🧵", "note": "نهاية tch", "position": "ending"},
                ],
            },
            {
                "pattern": "dge",
                "sound": "/j/",
                "arabic_sound": "ج",
                "rule": "dge يعطي صوت j غالبا في نهاية الكلمة بعد حرف علة قصير.",
                "examples": [
                    {"word": "bridge", "arabic": "جسر", "visual_hint": "🌉", "note": "نهاية dge", "position": "ending"},
                    {"word": "badge", "arabic": "شارة", "visual_hint": "🏷️", "note": "نهاية dge", "position": "ending"},
                    {"word": "judge", "arabic": "قاض / يحكم", "visual_hint": "⚖️", "note": "نهاية dge", "position": "ending"},
                    {"word": "edge", "arabic": "حافة", "visual_hint": "📏", "note": "نهاية dge", "position": "ending"},
                    {"word": "fridge", "arabic": "ثلاجة", "visual_hint": "🧊", "note": "نهاية dge", "position": "ending"},
                ],
            },
            {
                "pattern": "str",
                "sound": "/str/",
                "arabic_sound": "ستر",
                "rule": "str بداية قوية تجمع s + t + r.",
                "examples": [
                    {"word": "street", "arabic": "شارع", "visual_hint": "🛣️", "note": "بداية str", "position": "beginning"},
                    {"word": "strong", "arabic": "قوي", "visual_hint": "💪", "note": "بداية str", "position": "beginning"},
                    {"word": "string", "arabic": "خيط", "visual_hint": "🧵", "note": "بداية str", "position": "beginning"},
                    {"word": "stripe", "arabic": "خط / شريط", "visual_hint": "⭐", "note": "بداية str", "position": "beginning"},
                    {"word": "stride", "arabic": "خطوة واسعة", "visual_hint": "🚶", "note": "بداية str", "position": "beginning"},
                ],
            },
            {
                "pattern": "spr",
                "sound": "/spr/",
                "arabic_sound": "سبر",
                "rule": "spr بداية ثلاثية تبدأ بـ s ثم p ثم r.",
                "examples": [
                    {"word": "spring", "arabic": "ربيع / يقفز", "visual_hint": "🌱", "note": "بداية spr", "position": "beginning"},
                    {"word": "spray", "arabic": "يرش", "visual_hint": "💦", "note": "بداية spr", "position": "beginning"},
                    {"word": "spread", "arabic": "ينشر", "visual_hint": "🧺", "note": "بداية spr", "position": "beginning"},
                    {"word": "sprint", "arabic": "يركض بسرعة", "visual_hint": "🏃", "note": "بداية spr", "position": "beginning"},
                    {"word": "sprout", "arabic": "برعم", "visual_hint": "🌿", "note": "بداية spr", "position": "beginning"},
                ],
            },
            {
                "pattern": "shr",
                "sound": "/shr/",
                "arabic_sound": "شر",
                "rule": "shr يبدأ بصوت sh ثم r.",
                "examples": [
                    {"word": "shrimp", "arabic": "روبيان", "visual_hint": "🦐", "note": "بداية shr", "position": "beginning"},
                    {"word": "shrub", "arabic": "شجيرة", "visual_hint": "🌿", "note": "بداية shr", "position": "beginning"},
                    {"word": "shrink", "arabic": "ينكمش", "visual_hint": "📉", "note": "بداية shr", "position": "beginning"},
                    {"word": "shrug", "arabic": "يهز كتفيه", "visual_hint": "🤷", "note": "بداية shr", "position": "beginning"},
                    {"word": "shrill", "arabic": "حاد الصوت", "visual_hint": "🔊", "note": "بداية shr", "position": "beginning"},
                ],
            },
            {
                "pattern": "spl",
                "sound": "/spl/",
                "arabic_sound": "سبل",
                "rule": "spl بداية ثلاثية تبدأ بـ s ثم p ثم l.",
                "examples": [
                    {"word": "splash", "arabic": "يرش الماء", "visual_hint": "💦", "note": "بداية spl", "position": "beginning"},
                    {"word": "split", "arabic": "يقسم", "visual_hint": "✂️", "note": "بداية spl", "position": "beginning"},
                    {"word": "splat", "arabic": "صوت ارتطام", "visual_hint": "🟦", "note": "بداية spl", "position": "beginning"},
                    {"word": "splinter", "arabic": "شظية", "visual_hint": "🪵", "note": "بداية spl", "position": "beginning"},
                    {"word": "splashy", "arabic": "مبلل / كثير الرش", "visual_hint": "🐸", "note": "بداية spl", "position": "beginning"},
                ],
            },
        ],
    },
    {
        "id": "advanced_patterns",
        "title": "أصوات متقدمة لاحقًا",
        "subtitle": "Advanced Patterns",
        "stage": "خريطة طريق",
        "locked": True,
        "preview_only": True,
        "explanation": "هذه الأنماط تظهر في كلمات أطول، وتناسب المتعلم بعد إتقان CVC والأصوات الثنائية والنهايات والأصوات الثلاثية. استعرض الأمثلة فقط الآن؛ التدريب الكامل سيفتح في مستوى أعلى.",
        "patterns": [
            {
                "pattern": "tion",
                "sound": "/shən/",
                "arabic_sound": "شن",
                "rule": "غالبًا tion في نهاية الكلمة يعطي صوت \"شن\" في كلمات أطول.",
                "note": "tion غالبًا يظهر في نهاية كلمات طويلة.",
                "examples": [
                    {"word": "action", "arabic": "عمل / حركة", "visual_hint": "🎬", "note": "نهاية tion", "position": "ending"},
                    {"word": "station", "arabic": "محطة", "visual_hint": "🚉", "note": "نهاية tion", "position": "ending"},
                    {"word": "motion", "arabic": "حركة", "visual_hint": "🌀", "note": "نهاية tion", "position": "ending"},
                    {"word": "celebration", "arabic": "احتفال", "visual_hint": "🎉", "note": "نهاية tion", "position": "ending"},
                    {"word": "education", "arabic": "تعليم", "visual_hint": "📚", "note": "نهاية tion", "position": "ending"},
                ],
            },
            {
                "pattern": "ture",
                "sound": "/cher/",
                "arabic_sound": "تشر",
                "rule": "ture غالبًا ينطق مثل \"تشر\" في كلمات كثيرة.",
                "note": "ture يظهر غالبًا في نهاية الكلمة.",
                "examples": [
                    {"word": "picture", "arabic": "صورة", "visual_hint": "🖼️", "note": "نهاية ture", "position": "ending"},
                    {"word": "nature", "arabic": "طبيعة", "visual_hint": "🌿", "note": "نهاية ture", "position": "ending"},
                    {"word": "future", "arabic": "مستقبل", "visual_hint": "🔮", "note": "نهاية ture", "position": "ending"},
                    {"word": "adventure", "arabic": "مغامرة", "visual_hint": "🧳", "note": "نهاية ture", "position": "ending"},
                    {"word": "structure", "arabic": "تركيب / بنية", "visual_hint": "🏗️", "note": "نهاية ture", "position": "ending"},
                ],
            },
            {
                "pattern": "sion",
                "sound": "/zhən/ أو /shən/",
                "arabic_sound": "جن / شن",
                "rule": "sion له أكثر من نطق حسب الكلمة؛ أحيانًا قريب من \"جن\" وأحيانًا قريب من \"شن\".",
                "note": "sion ليس صوتًا واحدًا دائمًا.",
                "examples": [
                    {"word": "television", "arabic": "تلفاز", "visual_hint": "📺", "note": "نهاية sion", "position": "ending"},
                    {"word": "decision", "arabic": "قرار", "visual_hint": "✅", "note": "نهاية sion", "position": "ending"},
                    {"word": "vision", "arabic": "رؤية", "visual_hint": "👀", "note": "نهاية sion", "position": "ending"},
                    {"word": "explosion", "arabic": "انفجار", "visual_hint": "💥", "note": "نهاية sion", "position": "ending"},
                ],
            },
            {
                "pattern": "ssion",
                "sound": "/shən/",
                "arabic_sound": "شن",
                "rule": "ssion غالبًا يعطي صوت \"شن\" في نهاية الكلمة.",
                "note": "ssion يظهر غالبًا في نهاية كلمات أطول.",
                "examples": [
                    {"word": "mission", "arabic": "مهمة", "visual_hint": "🎯", "note": "نهاية ssion", "position": "ending"},
                    {"word": "passion", "arabic": "شغف", "visual_hint": "❤️", "note": "نهاية ssion", "position": "ending"},
                    {"word": "discussion", "arabic": "نقاش", "visual_hint": "💬", "note": "نهاية ssion", "position": "ending"},
                    {"word": "expression", "arabic": "تعبير", "visual_hint": "📝", "note": "نهاية ssion", "position": "ending"},
                    {"word": "session", "arabic": "جلسة", "visual_hint": "📌", "note": "نهاية ssion", "position": "ending"},
                ],
            },
            {
                "pattern": "ough",
                "sound": "متغير",
                "arabic_sound": "يتغير",
                "rule": "ough من أصعب الأنماط؛ لأنه لا ينطق دائمًا بنفس الطريقة.",
                "note": "ough ليس له صوت واحد ثابت، لذلك يدرس لاحقًا في مستوى متقدم.",
                "examples": [
                    {"word": "though", "arabic": "مع ذلك", "visual_hint": "🤔", "note": "نطق متغير", "position": "ending"},
                    {"word": "through", "arabic": "خلال / عبر", "visual_hint": "🚇", "note": "نطق متغير", "position": "ending"},
                    {"word": "rough", "arabic": "خشن", "visual_hint": "🪨", "note": "نطق متغير", "position": "ending"},
                    {"word": "thought", "arabic": "فكرة / اعتقد", "visual_hint": "🧠", "note": "نطق متغير", "position": "middle"},
                    {"word": "bough", "arabic": "غصن", "visual_hint": "🌿", "note": "نطق متغير", "position": "ending"},
                ],
            },
            {
                "pattern": "augh",
                "sound": "/aw/ أو /af/",
                "arabic_sound": "أو / آف",
                "rule": "augh يظهر في كلمات متقدمة وله نطق مختلف حسب الكلمة.",
                "note": "augh معاينة اختيارية ضمن خريطة الطريق.",
                "examples": [
                    {"word": "laugh", "arabic": "يضحك", "visual_hint": "😂", "note": "نطق /af/", "position": "middle"},
                    {"word": "daughter", "arabic": "ابنة", "visual_hint": "👧", "note": "نطق /aw/", "position": "middle"},
                    {"word": "taught", "arabic": "علّم / تم تعليمه", "visual_hint": "📚", "note": "نطق /aw/", "position": "middle"},
                    {"word": "caught", "arabic": "أمسك / وقع في", "visual_hint": "🧤", "note": "نطق /aw/", "position": "middle"},
                ],
            },
        ],
    },
]


SOUND_PATTERN_ACTIVITIES = [
    {
        "id": "digraph_listen_choose",
        "category": "digraphs",
        "title": "Listen and Choose",
        "prompt": "استمع إلى ship ثم اختر الصوت.",
        "answer": "sh",
        "options": ["sh", "ch", "th", "ph"],
        "listen": "ship",
    },
    {
        "id": "digraph_drag",
        "category": "digraphs",
        "mode": "drag",
        "title": "Drag to Sound",
        "prompt": "اسحب كل كلمة إلى صوتها الصحيح.",
        "targets": ["sh", "ch", "th", "ph", "wh", "ck"],
        "items": [
            {"word": "ship", "answer": "sh"},
            {"word": "chair", "answer": "ch"},
            {"word": "thin", "answer": "th"},
            {"word": "phone", "answer": "ph"},
            {"word": "what", "answer": "wh"},
            {"word": "duck", "answer": "ck"},
        ],
    },
    {
        "id": "digraph_circle",
        "category": "digraphs",
        "title": "Circle the Sound",
        "prompt": "ما الصوت الموجود في fish؟",
        "answer": "sh",
        "options": ["sh", "ch", "th", "wh"],
        "listen": "fish",
    },
    {
        "id": "digraph_complete_ship",
        "category": "digraphs",
        "title": "Complete the Word",
        "prompt": "أكمل الكلمة: __ip = ship",
        "answer": "sh",
        "options": ["sh", "ch", "th"],
        "listen": "ship",
    },
    {
        "id": "digraph_complete_lunch",
        "category": "digraphs",
        "title": "Complete the Word",
        "prompt": "أكمل الكلمة: lu__ = lunch",
        "answer": "ch",
        "options": ["ch", "sh", "ck"],
        "listen": "lunch",
    },
    {
        "id": "digraph_complete_duck",
        "category": "digraphs",
        "title": "Complete the Word",
        "prompt": "أكمل الكلمة: du__ = duck",
        "answer": "ck",
        "options": ["ck", "ph", "wh"],
        "listen": "duck",
    },
    {
        "id": "digraph_sort_words",
        "category": "digraphs",
        "mode": "drag",
        "title": "Sort the Words",
        "prompt": "صنف الكلمات حسب الصوت الثنائي.",
        "targets": ["sh", "ch", "th", "ph", "wh", "ck"],
        "items": [
            {"word": "fish", "answer": "sh"},
            {"word": "dish", "answer": "sh"},
            {"word": "chick", "answer": "ch"},
            {"word": "lunch", "answer": "ch"},
            {"word": "three", "answer": "th"},
            {"word": "this", "answer": "th"},
            {"word": "photo", "answer": "ph"},
            {"word": "whale", "answer": "wh"},
            {"word": "sock", "answer": "ck"},
        ],
    },
    {
        "id": "digraph_odd_one",
        "category": "digraphs",
        "title": "Odd One Out",
        "prompt": "اختر الكلمة المختلفة في الصوت: ship / shop / chair / fish",
        "answer": "chair",
        "options": ["ship", "shop", "chair", "fish"],
        "listen": "chair",
    },
    {
        "id": "digraph_position",
        "category": "digraphs",
        "title": "Beginning or Ending",
        "prompt": "أين صوت sh في fish؟",
        "answer": "ending",
        "options": ["beginning", "middle", "ending"],
        "listen": "fish",
    },
    {
        "id": "digraph_read_aloud",
        "category": "digraphs",
        "title": "Read Aloud",
        "prompt": "اقرأ كلمة chair بالمايك.",
        "answer": "chair",
        "options": ["استمع", "ابدأ المايك", "ch", "تم"],
        "listen": "chair",
        "mic": True,
    },
    {
        "id": "ending_ng",
        "category": "ending_sounds",
        "title": "Ending Sound",
        "prompt": "أي كلمة تنتهي بـ ng؟",
        "answer": "ring",
        "options": ["ring", "ship", "duck", "bell"],
        "listen": "ring",
    },
    {
        "id": "ending_position",
        "category": "ending_sounds",
        "title": "Where is ck?",
        "prompt": "أين صوت ck في duck؟",
        "answer": "ending",
        "options": ["beginning", "middle", "ending"],
        "listen": "duck",
    },
    {
        "id": "ending_drag",
        "category": "ending_sounds",
        "mode": "drag",
        "title": "Sort Endings",
        "prompt": "صنف الكلمات حسب نهاية الصوت.",
        "targets": ["ck", "ng", "nk", "ll", "ss", "ff"],
        "items": [
            {"word": "back", "answer": "ck"},
            {"word": "sing", "answer": "ng"},
            {"word": "bank", "answer": "nk"},
            {"word": "bell", "answer": "ll"},
            {"word": "kiss", "answer": "ss"},
            {"word": "off", "answer": "ff"},
        ],
    },
    {
        "id": "trigraph_listen_choose",
        "category": "trigraphs",
        "title": "Listen and Choose",
        "prompt": "استمع إلى catch ثم اختر النمط.",
        "answer": "tch",
        "options": ["tch", "dge", "str", "spr"],
        "listen": "catch",
    },
    {
        "id": "trigraph_drag",
        "category": "trigraphs",
        "mode": "drag",
        "title": "Drag to Trigraph",
        "prompt": "اسحب الكلمة إلى النمط الثلاثي الصحيح.",
        "targets": ["tch", "dge", "str", "spr", "spl", "shr"],
        "items": [
            {"word": "catch", "answer": "tch"},
            {"word": "bridge", "answer": "dge"},
            {"word": "street", "answer": "str"},
            {"word": "spring", "answer": "spr"},
            {"word": "splash", "answer": "spl"},
            {"word": "shrimp", "answer": "shr"},
        ],
    },
    {
        "id": "trigraph_complete_catch",
        "category": "trigraphs",
        "title": "Complete the Word",
        "prompt": "أكمل الكلمة: ca__ = catch",
        "answer": "tch",
        "options": ["tch", "dge", "str"],
        "listen": "catch",
    },
    {
        "id": "trigraph_complete_bridge",
        "category": "trigraphs",
        "title": "Complete the Word",
        "prompt": "أكمل الكلمة: bri__ = bridge",
        "answer": "dge",
        "options": ["dge", "tch", "spl"],
        "listen": "bridge",
    },
    {
        "id": "trigraph_complete_street",
        "category": "trigraphs",
        "title": "Complete the Word",
        "prompt": "أكمل الكلمة: __eet = street",
        "answer": "str",
        "options": ["str", "spr", "shr"],
        "listen": "street",
    },
    {
        "id": "trigraph_complete_splash",
        "category": "trigraphs",
        "title": "Complete the Word",
        "prompt": "أكمل الكلمة: __ash = splash",
        "answer": "spl",
        "options": ["spl", "spr", "str"],
        "listen": "splash",
    },
    {
        "id": "trigraph_position_tch",
        "category": "trigraphs",
        "title": "Beginning or Ending",
        "prompt": "أين نمط tch في catch؟",
        "answer": "ending",
        "options": ["beginning", "middle", "ending"],
        "listen": "catch",
    },
    {
        "id": "trigraph_position_str",
        "category": "trigraphs",
        "title": "Beginning or Ending",
        "prompt": "أين نمط str في street؟",
        "answer": "beginning",
        "options": ["beginning", "middle", "ending"],
        "listen": "street",
    },
    {
        "id": "trigraph_sort_words",
        "category": "trigraphs",
        "mode": "drag",
        "title": "Sort the Words",
        "prompt": "صنف الكلمات حسب النمط الثلاثي.",
        "targets": ["tch", "dge", "str", "spr", "spl", "shr"],
        "items": [
            {"word": "watch", "answer": "tch"},
            {"word": "match", "answer": "tch"},
            {"word": "badge", "answer": "dge"},
            {"word": "judge", "answer": "dge"},
            {"word": "strong", "answer": "str"},
            {"word": "string", "answer": "str"},
            {"word": "spray", "answer": "spr"},
            {"word": "sprint", "answer": "spr"},
            {"word": "split", "answer": "spl"},
            {"word": "splat", "answer": "spl"},
            {"word": "shrub", "answer": "shr"},
            {"word": "shrink", "answer": "shr"},
        ],
    },
    {
        "id": "trigraph_odd_one",
        "category": "trigraphs",
        "title": "Odd One Out",
        "prompt": "اختر الكلمة المختلفة في النمط: catch / watch / bridge / match",
        "answer": "bridge",
        "options": ["catch", "watch", "bridge", "match"],
        "listen": "bridge",
    },
    {
        "id": "trigraph_build_word",
        "category": "trigraphs",
        "title": "Build the Word",
        "prompt": "اختر الكلمة المبنية من: bri + dge",
        "answer": "bridge",
        "options": ["bridge", "catch", "street", "splash"],
        "listen": "bridge",
    },
    {
        "id": "trigraph_read_aloud",
        "category": "trigraphs",
        "title": "Read Aloud",
        "prompt": "اقرأ كلمة bridge بالمايك.",
        "answer": "bridge",
        "options": ["استمع", "ابدأ المايك", "dge", "تم"],
        "listen": "bridge",
        "mic": True,
    },
    {
        "id": "advanced_pattern_match",
        "category": "advanced_patterns",
        "title": "Pattern Match",
        "prompt": "معاينة: صل النمط بالكلمة المناسبة. station يحتوي على:",
        "answer": "tion",
        "options": ["tion", "ture", "sion", "ssion", "ough"],
        "listen": "station",
        "preview": True,
    },
    {
        "id": "advanced_find_pattern_picture",
        "category": "advanced_patterns",
        "title": "Find the Pattern",
        "prompt": "اكتشف النمط المتقدم داخل picture.",
        "answer": "ture",
        "options": ["ture", "tion", "ough"],
        "listen": "picture",
        "preview": True,
    },
    {
        "id": "advanced_listen_notice_mission",
        "category": "advanced_patterns",
        "title": "Listen and Notice",
        "prompt": "استمع إلى mission ثم اختر النمط المكتوب فيها.",
        "answer": "ssion",
        "options": ["ssion", "sion", "ough"],
        "listen": "mission",
        "preview": True,
    },
    {
        "id": "advanced_sort_by_ending",
        "category": "advanced_patterns",
        "mode": "drag",
        "title": "Sort by Ending",
        "prompt": "معاينة: صنف الكلمات حسب النهاية المتقدمة.",
        "targets": ["tion", "ture", "sion", "ssion", "ough"],
        "items": [
            {"word": "action", "answer": "tion"},
            {"word": "station", "answer": "tion"},
            {"word": "picture", "answer": "ture"},
            {"word": "nature", "answer": "ture"},
            {"word": "television", "answer": "sion"},
            {"word": "decision", "answer": "sion"},
            {"word": "mission", "answer": "ssion"},
            {"word": "discussion", "answer": "ssion"},
            {"word": "through", "answer": "ough"},
            {"word": "rough", "answer": "ough"},
        ],
        "preview": True,
    },
    {
        "id": "advanced_basic_or_advanced",
        "category": "advanced_patterns",
        "title": "Advanced or Basic?",
        "prompt": "هل station كلمة Basic أم Advanced؟",
        "answer": "Advanced",
        "options": ["Basic", "Advanced", "Digraph"],
        "listen": "station",
        "preview": True,
    },
    {
        "id": "advanced_word_detective",
        "category": "advanced_patterns",
        "title": "Word Detective",
        "prompt": "اكتشف النمط المتقدم في education.",
        "answer": "tion",
        "options": ["tion", "ture", "ssion", "ough"],
        "listen": "education",
        "preview": True,
    },
]


ANIMAL_VOCABULARY_GROUPS = [
    {
        "id": "pets",
        "title_ar": "حيوانات أليفة",
        "title_en": "Pets",
        "icon": "🐾",
        "habitat": "house",
        "words": [
            {"word": "cat", "arabic": "قط", "icon": "🐱", "example": "The cat is small.", "example_ar": "القط صغير."},
            {"word": "dog", "arabic": "كلب", "icon": "🐶", "example": "The dog can run.", "example_ar": "الكلب يستطيع الركض."},
            {"word": "rabbit", "arabic": "أرنب", "icon": "🐰", "example": "The rabbit is white.", "example_ar": "الأرنب أبيض."},
            {"word": "bird", "arabic": "طائر", "icon": "🐦", "example": "I see a bird.", "example_ar": "أرى طائرًا."},
            {"word": "fish", "arabic": "سمكة", "icon": "🐟", "example": "The fish is blue.", "example_ar": "السمكة زرقاء."},
            {"word": "hamster", "arabic": "هامستر", "icon": "🐹", "example": "The hamster is cute.", "example_ar": "الهامستر لطيف."},
        ],
    },
    {
        "id": "farm",
        "title_ar": "حيوانات المزرعة",
        "title_en": "Farm Animals",
        "icon": "🚜",
        "habitat": "farm",
        "words": [
            {"word": "cow", "arabic": "بقرة", "icon": "🐄", "example": "The cow gives milk.", "example_ar": "البقرة تعطينا الحليب."},
            {"word": "horse", "arabic": "حصان", "icon": "🐴", "example": "The horse is fast.", "example_ar": "الحصان سريع."},
            {"word": "sheep", "arabic": "خروف", "icon": "🐑", "example": "The sheep is soft.", "example_ar": "الخروف ناعم."},
            {"word": "goat", "arabic": "ماعز", "icon": "🐐", "example": "The goat is on the farm.", "example_ar": "الماعز في المزرعة."},
            {"word": "chicken", "arabic": "دجاجة", "icon": "🐔", "example": "The chicken is small.", "example_ar": "الدجاجة صغيرة."},
            {"word": "duck", "arabic": "بطة", "icon": "🦆", "example": "The duck can swim.", "example_ar": "البطة تستطيع السباحة."},
        ],
    },
    {
        "id": "wild",
        "title_ar": "حيوانات برية",
        "title_en": "Wild Animals",
        "icon": "🌿",
        "habitat": "forest",
        "words": [
            {"word": "lion", "arabic": "أسد", "icon": "🦁", "example": "The lion is strong.", "example_ar": "الأسد قوي."},
            {"word": "tiger", "arabic": "نمر", "icon": "🐯", "example": "The tiger is fast.", "example_ar": "النمر سريع."},
            {"word": "elephant", "arabic": "فيل", "icon": "🐘", "example": "The elephant is big.", "example_ar": "الفيل كبير."},
            {"word": "monkey", "arabic": "قرد", "icon": "🐒", "example": "The monkey can climb.", "example_ar": "القرد يستطيع التسلق."},
            {"word": "giraffe", "arabic": "زرافة", "icon": "🦒", "example": "The giraffe has a long neck.", "example_ar": "الزرافة لها رقبة طويلة."},
            {"word": "bear", "arabic": "دب", "icon": "🐻", "example": "The bear is big.", "example_ar": "الدب كبير."},
            {"word": "fox", "arabic": "ثعلب", "icon": "🦊", "example": "The fox is clever.", "example_ar": "الثعلب ذكي."},
            {"word": "wolf", "arabic": "ذئب", "icon": "🐺", "example": "The wolf is wild.", "example_ar": "الذئب بري."},
        ],
    },
    {
        "id": "sea",
        "title_ar": "حيوانات البحر",
        "title_en": "Sea Animals",
        "icon": "🌊",
        "habitat": "sea",
        "words": [
            {"word": "whale", "arabic": "حوت", "icon": "🐋", "example": "The whale is huge.", "example_ar": "الحوت ضخم."},
            {"word": "dolphin", "arabic": "دولفين", "icon": "🐬", "example": "The dolphin is smart.", "example_ar": "الدولفين ذكي."},
            {"word": "shark", "arabic": "قرش", "icon": "🦈", "example": "The shark is in the sea.", "example_ar": "القرش في البحر."},
            {"word": "turtle", "arabic": "سلحفاة", "icon": "🐢", "example": "The turtle is slow.", "example_ar": "السلحفاة بطيئة."},
            {"word": "crab", "arabic": "سلطعون", "icon": "🦀", "example": "The crab walks sideways.", "example_ar": "السلطعون يمشي جانبًا."},
            {"word": "octopus", "arabic": "أخطبوط", "icon": "🐙", "example": "The octopus has eight arms.", "example_ar": "الأخطبوط له ثمانية أذرع."},
        ],
    },
    {
        "id": "insects",
        "title_ar": "حشرات وكائنات صغيرة",
        "title_en": "Insects & Small Creatures",
        "icon": "🐝",
        "habitat": "garden",
        "words": [
            {"word": "bee", "arabic": "نحلة", "icon": "🐝", "example": "The bee makes honey.", "example_ar": "النحلة تصنع العسل."},
            {"word": "butterfly", "arabic": "فراشة", "icon": "🦋", "example": "The butterfly is beautiful.", "example_ar": "الفراشة جميلة."},
            {"word": "ant", "arabic": "نملة", "icon": "🐜", "example": "The ant is tiny.", "example_ar": "النملة صغيرة جدًا."},
            {"word": "spider", "arabic": "عنكبوت", "icon": "🕷️", "example": "The spider makes a web.", "example_ar": "العنكبوت يصنع شبكة."},
            {"word": "frog", "arabic": "ضفدع", "icon": "🐸", "example": "The frog can jump.", "example_ar": "الضفدع يستطيع القفز."},
        ],
    },
]


for animal_group in ANIMAL_VOCABULARY_GROUPS:
    for animal_word in animal_group["words"]:
        animal_word.update({
            "group_id": animal_group["id"],
            "group_ar": animal_group["title_ar"],
            "group_en": animal_group["title_en"],
            "habitat": animal_group["habitat"],
        })


ANIMAL_VOCABULARY_WORDS = [
    animal_word
    for animal_group in ANIMAL_VOCABULARY_GROUPS
    for animal_word in animal_group["words"]
]


ANIMAL_DAILY_SENTENCES = [
    {"sentence": "I see a cat.", "arabic": "أرى قطًا.", "target": "cat"},
    {"sentence": "I have a dog.", "arabic": "لدي كلب.", "target": "dog"},
    {"sentence": "The bird can fly.", "arabic": "الطائر يستطيع الطيران.", "target": "bird"},
    {"sentence": "The fish can swim.", "arabic": "السمكة تستطيع السباحة.", "target": "fish"},
    {"sentence": "The lion is strong.", "arabic": "الأسد قوي.", "target": "lion"},
    {"sentence": "The cow gives milk.", "arabic": "البقرة تعطينا الحليب.", "target": "cow"},
    {"sentence": "The horse is fast.", "arabic": "الحصان سريع.", "target": "horse"},
    {"sentence": "The rabbit is white.", "arabic": "الأرنب أبيض.", "target": "rabbit"},
    {"sentence": "The dolphin is smart.", "arabic": "الدولفين ذكي.", "target": "dolphin"},
    {"sentence": "The bee makes honey.", "arabic": "النحلة تصنع العسل.", "target": "bee"},
]


ANIMAL_MINI_STORY = {
    "title_ar": "قصة قصيرة مع الحيوانات",
    "title_en": "Animal Mini Story",
    "english": [
        "I see a cat.",
        "The cat is small.",
        "I see a dog.",
        "The dog can run.",
        "I see a bird.",
        "The bird can fly.",
    ],
    "arabic": [
        "أرى قطًا.",
        "القط صغير.",
        "أرى كلبًا.",
        "الكلب يستطيع الركض.",
        "أرى طائرًا.",
        "الطائر يستطيع الطيران.",
    ],
    "question": "What animal can run?",
    "options": ["dog", "fish", "cow"],
    "answer": "dog",
}


FOOD_VOCABULARY_GROUPS = [
    {
        "id": "fruits",
        "title_ar": "الفواكه",
        "title_en": "Fruits",
        "icon": "🍎",
        "food_type": "Fruit",
        "words": [
            {"word": "apple", "arabic": "تفاحة", "icon": "🍎", "example": "I like apples.", "example_ar": "أحب التفاح."},
            {"word": "banana", "arabic": "موزة", "icon": "🍌", "example": "The banana is yellow.", "example_ar": "الموزة صفراء."},
            {"word": "orange", "arabic": "برتقالة", "icon": "🍊", "example": "I eat an orange.", "example_ar": "آكل برتقالة."},
            {"word": "grapes", "arabic": "عنب", "icon": "🍇", "example": "The grapes are sweet.", "example_ar": "العنب حلو."},
            {"word": "strawberry", "arabic": "فراولة", "icon": "🍓", "example": "The strawberry is red.", "example_ar": "الفراولة حمراء."},
            {"word": "watermelon", "arabic": "بطيخ", "icon": "🍉", "example": "I like watermelon.", "example_ar": "أحب البطيخ."},
            {"word": "lemon", "arabic": "ليمون", "icon": "🍋", "example": "The lemon is sour.", "example_ar": "الليمون حامض."},
        ],
    },
    {
        "id": "vegetables",
        "title_ar": "الخضروات",
        "title_en": "Vegetables",
        "icon": "🥕",
        "food_type": "Vegetable",
        "words": [
            {"word": "carrot", "arabic": "جزر", "icon": "🥕", "example": "The carrot is orange.", "example_ar": "الجزر برتقالي."},
            {"word": "tomato", "arabic": "طماطم", "icon": "🍅", "example": "I eat a tomato.", "example_ar": "آكل طماطم."},
            {"word": "potato", "arabic": "بطاطس", "icon": "🥔", "example": "The potato is hot.", "example_ar": "البطاطس ساخنة."},
            {"word": "cucumber", "arabic": "خيار", "icon": "🥒", "example": "The cucumber is green.", "example_ar": "الخيار أخضر."},
            {"word": "corn", "arabic": "ذرة", "icon": "🌽", "example": "I like corn.", "example_ar": "أحب الذرة."},
            {"word": "lettuce", "arabic": "خس", "icon": "🥬", "example": "The lettuce is fresh.", "example_ar": "الخس طازج."},
            {"word": "onion", "arabic": "بصل", "icon": "🧅", "example": "The onion is strong.", "example_ar": "البصل قوي الرائحة."},
        ],
    },
    {
        "id": "daily-meals",
        "title_ar": "وجبات يومية",
        "title_en": "Daily Meals",
        "icon": "🍽️",
        "food_type": "Meal",
        "words": [
            {"word": "bread", "arabic": "خبز", "icon": "🍞", "example": "I eat bread.", "example_ar": "آكل الخبز."},
            {"word": "rice", "arabic": "أرز", "icon": "🍚", "example": "I eat rice for lunch.", "example_ar": "آكل الأرز في الغداء."},
            {"word": "egg", "arabic": "بيضة", "icon": "🥚", "example": "I eat an egg.", "example_ar": "آكل بيضة."},
            {"word": "cheese", "arabic": "جبن", "icon": "🧀", "example": "I like cheese.", "example_ar": "أحب الجبن."},
            {"word": "chicken", "arabic": "دجاج", "icon": "🍗", "example": "I eat chicken.", "example_ar": "آكل الدجاج."},
            {"word": "fish", "arabic": "سمك", "icon": "🐟", "example": "Fish is healthy.", "example_ar": "السمك صحي."},
            {"word": "meat", "arabic": "لحم", "icon": "🥩", "example": "I eat meat.", "example_ar": "آكل اللحم."},
            {"word": "soup", "arabic": "شوربة", "icon": "🍲", "example": "The soup is hot.", "example_ar": "الشوربة ساخنة."},
        ],
    },
    {
        "id": "snacks",
        "title_ar": "أطعمة خفيفة",
        "title_en": "Snacks",
        "icon": "🥪",
        "food_type": "Snack",
        "words": [
            {"word": "sandwich", "arabic": "شطيرة", "icon": "🥪", "example": "I have a sandwich.", "example_ar": "لدي شطيرة."},
            {"word": "pizza", "arabic": "بيتزا", "icon": "🍕", "example": "I like pizza.", "example_ar": "أحب البيتزا."},
            {"word": "burger", "arabic": "برجر", "icon": "🍔", "example": "The burger is big.", "example_ar": "البرجر كبير."},
            {"word": "fries", "arabic": "بطاطس مقلية", "icon": "🍟", "example": "The fries are hot.", "example_ar": "البطاطس المقلية ساخنة."},
            {"word": "popcorn", "arabic": "فشار", "icon": "🍿", "example": "I eat popcorn.", "example_ar": "آكل الفشار."},
            {"word": "chips", "arabic": "رقائق بطاطس", "icon": "🥔", "example": "I eat chips.", "example_ar": "آكل رقائق البطاطس."},
        ],
    },
    {
        "id": "sweets",
        "title_ar": "حلويات",
        "title_en": "Sweets",
        "icon": "🍰",
        "food_type": "Sweet",
        "words": [
            {"word": "cake", "arabic": "كعكة", "icon": "🍰", "example": "The cake is sweet.", "example_ar": "الكعكة حلوة."},
            {"word": "cookie", "arabic": "بسكويت", "icon": "🍪", "example": "I eat a cookie.", "example_ar": "آكل بسكويتة."},
            {"word": "chocolate", "arabic": "شوكولاتة", "icon": "🍫", "example": "I like chocolate.", "example_ar": "أحب الشوكولاتة."},
            {"word": "ice cream", "arabic": "آيس كريم", "icon": "🍦", "example": "The ice cream is cold.", "example_ar": "الآيس كريم بارد."},
            {"word": "candy", "arabic": "حلوى", "icon": "🍬", "example": "The candy is sweet.", "example_ar": "الحلوى حلوة."},
            {"word": "donut", "arabic": "دونات", "icon": "🍩", "example": "I see a donut.", "example_ar": "أرى دونات."},
        ],
    },
    {
        "id": "healthy-food",
        "title_ar": "أطعمة صحية",
        "title_en": "Healthy Food",
        "icon": "🥗",
        "food_type": "Healthy Food",
        "words": [
            {"word": "salad", "arabic": "سلطة", "icon": "🥗", "example": "Salad is healthy.", "example_ar": "السلطة صحية."},
            {"word": "milk", "arabic": "حليب", "icon": "🥛", "example": "I drink milk.", "example_ar": "أشرب الحليب."},
            {"word": "yogurt", "arabic": "زبادي", "icon": "🥣", "example": "I eat yogurt.", "example_ar": "آكل الزبادي."},
            {"word": "nuts", "arabic": "مكسرات", "icon": "🥜", "example": "Nuts are healthy.", "example_ar": "المكسرات صحية."},
            {"word": "beans", "arabic": "فاصوليا", "icon": "🫘", "example": "I eat beans.", "example_ar": "آكل الفاصوليا."},
            {"word": "honey", "arabic": "عسل", "icon": "🍯", "example": "Honey is sweet.", "example_ar": "العسل حلو."},
        ],
    },
]


for food_group in FOOD_VOCABULARY_GROUPS:
    for food_word in food_group["words"]:
        food_word.update({
            "group_id": food_group["id"],
            "group_ar": food_group["title_ar"],
            "group_en": food_group["title_en"],
            "food_type": food_group["food_type"],
        })


FOOD_VOCABULARY_WORDS = [
    food_word
    for food_group in FOOD_VOCABULARY_GROUPS
    for food_word in food_group["words"]
]


FOOD_DAILY_SENTENCES = [
    {"sentence": "I like apples.", "arabic": "أحب التفاح.", "target": "apple"},
    {"sentence": "I eat rice.", "arabic": "آكل الأرز.", "target": "rice"},
    {"sentence": "I drink milk.", "arabic": "أشرب الحليب.", "target": "milk"},
    {"sentence": "The banana is yellow.", "arabic": "الموزة صفراء.", "target": "banana"},
    {"sentence": "The carrot is orange.", "arabic": "الجزر برتقالي.", "target": "carrot"},
    {"sentence": "The cake is sweet.", "arabic": "الكعكة حلوة.", "target": "cake"},
    {"sentence": "The soup is hot.", "arabic": "الشوربة ساخنة.", "target": "soup"},
    {"sentence": "The ice cream is cold.", "arabic": "الآيس كريم بارد.", "target": "ice cream"},
    {"sentence": "Pizza is yummy.", "arabic": "البيتزا لذيذة.", "target": "pizza"},
    {"sentence": "Salad is healthy.", "arabic": "السلطة صحية.", "target": "salad"},
    {"sentence": "I have a sandwich.", "arabic": "لدي شطيرة.", "target": "sandwich"},
    {"sentence": "I eat chicken.", "arabic": "آكل الدجاج.", "target": "chicken"},
]


FOOD_MINI_STORY = {
    "title_ar": "قصة قصيرة مع الأطعمة",
    "title_en": "Food Mini Story",
    "english": [
        "I am hungry.",
        "I eat bread.",
        "I eat an apple.",
        "I drink milk.",
        "The apple is sweet.",
        "The milk is white.",
    ],
    "arabic": [
        "أنا جائع.",
        "آكل الخبز.",
        "آكل تفاحة.",
        "أشرب الحليب.",
        "التفاحة حلوة.",
        "الحليب أبيض.",
    ],
    "questions": [
        {
            "question": "What fruit do I eat?",
            "options": ["apple", "rice", "chicken"],
            "answer": "apple",
        },
        {
            "question": "What do I drink?",
            "options": ["milk", "pizza", "cake"],
            "answer": "milk",
        },
    ],
}


CALENDAR_VOCABULARY_GROUPS = [
    {
        "id": "days",
        "title_ar": "الأيام",
        "title_en": "Days",
        "icon": "📆",
        "time_type": "Day",
        "words": [
            {"word": "Monday", "arabic": "الاثنين", "icon": "1", "example": "Monday is a school day.", "example_ar": "الاثنين يوم دراسي."},
            {"word": "Tuesday", "arabic": "الثلاثاء", "icon": "2", "example": "Tuesday comes after Monday.", "example_ar": "الثلاثاء يأتي بعد الاثنين."},
            {"word": "Wednesday", "arabic": "الأربعاء", "icon": "3", "example": "Wednesday is in the middle.", "example_ar": "الأربعاء في منتصف الأسبوع."},
            {"word": "Thursday", "arabic": "الخميس", "icon": "4", "example": "Thursday comes before Friday.", "example_ar": "الخميس يأتي قبل الجمعة."},
            {"word": "Friday", "arabic": "الجمعة", "icon": "5", "example": "Friday is a weekend day.", "example_ar": "الجمعة يوم عطلة."},
            {"word": "Saturday", "arabic": "السبت", "icon": "6", "example": "Saturday is a weekend day.", "example_ar": "السبت يوم عطلة."},
            {"word": "Sunday", "arabic": "الأحد", "icon": "7", "example": "Sunday starts a new week.", "example_ar": "الأحد يبدأ أسبوعًا جديدًا."},
        ],
    },
    {
        "id": "months",
        "title_ar": "الأشهر",
        "title_en": "Months",
        "icon": "🗓️",
        "time_type": "Month",
        "words": [
            {"word": "January", "arabic": "يناير", "icon": "Jan", "example": "January is the first month.", "example_ar": "يناير هو الشهر الأول."},
            {"word": "February", "arabic": "فبراير", "icon": "Feb", "example": "February is a short month.", "example_ar": "فبراير شهر قصير."},
            {"word": "March", "arabic": "مارس", "icon": "Mar", "example": "My birthday is in March.", "example_ar": "عيد ميلادي في مارس."},
            {"word": "April", "arabic": "أبريل", "icon": "Apr", "example": "April has nice weather.", "example_ar": "أبريل طقسه جميل."},
            {"word": "May", "arabic": "مايو", "icon": "May", "example": "May is before June.", "example_ar": "مايو قبل يونيو."},
            {"word": "June", "arabic": "يونيو", "icon": "Jun", "example": "Summer starts in June.", "example_ar": "يبدأ الصيف في يونيو."},
            {"word": "July", "arabic": "يوليو", "icon": "Jul", "example": "July is hot.", "example_ar": "يوليو حار."},
            {"word": "August", "arabic": "أغسطس", "icon": "Aug", "example": "August is in summer.", "example_ar": "أغسطس في الصيف."},
            {"word": "September", "arabic": "سبتمبر", "icon": "Sep", "example": "School starts in September.", "example_ar": "تبدأ المدرسة في سبتمبر."},
            {"word": "October", "arabic": "أكتوبر", "icon": "Oct", "example": "October is in autumn.", "example_ar": "أكتوبر في الخريف."},
            {"word": "November", "arabic": "نوفمبر", "icon": "Nov", "example": "November is before December.", "example_ar": "نوفمبر قبل ديسمبر."},
            {"word": "December", "arabic": "ديسمبر", "icon": "Dec", "example": "December is the last month.", "example_ar": "ديسمبر هو الشهر الأخير."},
        ],
    },
]


for calendar_group in CALENDAR_VOCABULARY_GROUPS:
    for calendar_word in calendar_group["words"]:
        calendar_word.update({
            "group_id": calendar_group["id"],
            "group_ar": calendar_group["title_ar"],
            "group_en": calendar_group["title_en"],
            "time_type": calendar_group["time_type"],
        })


CALENDAR_VOCABULARY_WORDS = [
    calendar_word
    for calendar_group in CALENDAR_VOCABULARY_GROUPS
    for calendar_word in calendar_group["words"]
]


CALENDAR_DAILY_SENTENCES = [
    {"sentence": "Today is Monday.", "arabic": "اليوم هو الاثنين.", "target": "Monday"},
    {"sentence": "Tomorrow is Tuesday.", "arabic": "غدًا هو الثلاثاء.", "target": "Tuesday"},
    {"sentence": "Friday is a weekend day.", "arabic": "الجمعة يوم عطلة.", "target": "Friday"},
    {"sentence": "Sunday starts a new week.", "arabic": "الأحد يبدأ أسبوعًا جديدًا.", "target": "Sunday"},
    {"sentence": "January is the first month.", "arabic": "يناير هو الشهر الأول.", "target": "January"},
    {"sentence": "My birthday is in March.", "arabic": "عيد ميلادي في مارس.", "target": "March"},
    {"sentence": "Summer starts in June.", "arabic": "يبدأ الصيف في يونيو.", "target": "June"},
    {"sentence": "School starts in September.", "arabic": "تبدأ المدرسة في سبتمبر.", "target": "September"},
    {"sentence": "December is the last month.", "arabic": "ديسمبر هو الشهر الأخير.", "target": "December"},
    {"sentence": "There are twelve months in a year.", "arabic": "هناك اثنا عشر شهرًا في السنة.", "target": "months"},
]


CALENDAR_MINI_STORY = {
    "title_ar": "قصة قصيرة مع الأيام والأشهر",
    "title_en": "Calendar Mini Story",
    "english": [
        "Today is Monday.",
        "I go to school.",
        "My birthday is in March.",
        "Summer starts in June.",
        "December is the last month.",
    ],
    "arabic": [
        "اليوم هو الاثنين.",
        "أذهب إلى المدرسة.",
        "عيد ميلادي في مارس.",
        "يبدأ الصيف في يونيو.",
        "ديسمبر هو الشهر الأخير.",
    ],
    "questions": [
        {
            "question": "What day is today?",
            "options": ["Monday", "Friday", "Sunday"],
            "answer": "Monday",
        },
        {
            "question": "What month is my birthday?",
            "options": ["March", "June", "December"],
            "answer": "March",
        },
    ],
}


LEVEL_TWO_GRAMMAR_LESSONS = [
    {
        "id": "demonstratives",
        "title_ar": "أسماء الإشارة",
        "title_en": "Demonstratives",
        "icon": "👉",
        "worksheet": "demonstratives",
        "summary_ar": "نستخدم this وthat وthese وthose لنشير إلى شيء قريب أو بعيد، مفرد أو جمع.",
        "rule_en": "Use this/these for near things and that/those for far things.",
        "structure": "this/that + singular, these/those + plural",
        "groups": [
            {
                "id": "near",
                "title_ar": "قريب",
                "title_en": "Near",
                "entries": [
                    {"term": "this", "arabic": "هذا / هذه", "use_ar": "قريب ومفرد", "example": "This is my pen.", "example_ar": "هذا قلمي."},
                    {"term": "these", "arabic": "هؤلاء / هذه", "use_ar": "قريب وجمع", "example": "These are my books.", "example_ar": "هذه كتبي."},
                ],
            },
            {
                "id": "far",
                "title_ar": "بعيد",
                "title_en": "Far",
                "entries": [
                    {"term": "that", "arabic": "ذلك / تلك", "use_ar": "بعيد ومفرد", "example": "That is your bag.", "example_ar": "تلك حقيبتك."},
                    {"term": "those", "arabic": "أولئك / تلك", "use_ar": "بعيد وجمع", "example": "Those are my shoes.", "example_ar": "تلك أحذيتي."},
                ],
            },
        ],
        "activities": [
            {"title": "اختر الكلمة", "prompt": "____ is my pen.", "answer": "This", "options": ["This", "These", "Those"], "listen": "This is my pen."},
            {"title": "مفرد أم جمع؟", "prompt": "These", "answer": "plural", "options": ["singular", "plural"]},
            {"title": "قريب أم بعيد؟", "prompt": "that", "answer": "far", "options": ["near", "far"]},
            {"title": "اقرأ بالمايك", "prompt": "Those are my shoes.", "answer": "Those are my shoes.", "options": [], "mic": "Those are my shoes."},
        ],
    },
    {
        "id": "pronouns",
        "title_ar": "الضمائر",
        "title_en": "Pronouns",
        "icon": "👤",
        "worksheet": "pronouns",
        "summary_ar": "الضمير يحل محل الاسم حتى لا نكرر اسم الشخص أو الشيء في كل جملة.",
        "rule_en": "Pronouns replace nouns. Subject pronouns do the action; object pronouns receive the action.",
        "structure": "subject pronoun + verb / verb + object pronoun",
        "groups": [
            {
                "id": "subject",
                "title_ar": "ضمائر الفاعل",
                "title_en": "Subject Pronouns",
                "entries": [
                    {"term": "I", "arabic": "أنا", "use_ar": "المتكلم", "example": "I am a student.", "example_ar": "أنا طالب."},
                    {"term": "you", "arabic": "أنت / أنتم", "use_ar": "المخاطب", "example": "You are kind.", "example_ar": "أنت لطيف."},
                    {"term": "he", "arabic": "هو", "use_ar": "مذكر مفرد", "example": "He plays football.", "example_ar": "هو يلعب كرة القدم."},
                    {"term": "she", "arabic": "هي", "use_ar": "مؤنث مفرد", "example": "She reads books.", "example_ar": "هي تقرأ الكتب."},
                    {"term": "it", "arabic": "هو / هي لغير العاقل", "use_ar": "شيء أو حيوان", "example": "It is blue.", "example_ar": "إنه أزرق."},
                    {"term": "we", "arabic": "نحن", "use_ar": "المتكلمون", "example": "We study English.", "example_ar": "نحن ندرس الإنجليزية."},
                    {"term": "they", "arabic": "هم / هن", "use_ar": "جمع", "example": "They are happy.", "example_ar": "هم سعداء."},
                ],
            },
            {
                "id": "object",
                "title_ar": "ضمائر المفعول",
                "title_en": "Object Pronouns",
                "entries": [
                    {"term": "me", "arabic": "ني / لي", "use_ar": "بعد الفعل", "example": "The teacher helped me.", "example_ar": "ساعدني المعلم."},
                    {"term": "him", "arabic": "ه / له", "use_ar": "مذكر بعد الفعل", "example": "I called him.", "example_ar": "اتصلت به."},
                    {"term": "her", "arabic": "ها / لها", "use_ar": "مؤنث بعد الفعل", "example": "They invited her.", "example_ar": "دعَوها."},
                    {"term": "us", "arabic": "نا / لنا", "use_ar": "نحن بعد الفعل", "example": "She saw us.", "example_ar": "هي رأتنا."},
                    {"term": "them", "arabic": "هم / لهم", "use_ar": "جمع بعد الفعل", "example": "We like them.", "example_ar": "نحن نحبهم."},
                ],
            },
        ],
        "activities": [
            {"title": "اختر الضمير", "prompt": "____ am a student.", "answer": "I", "options": ["I", "Me", "My"], "listen": "I am a student."},
            {"title": "فاعل أم مفعول؟", "prompt": "him", "answer": "object", "options": ["subject", "object"]},
            {"title": "أكمل الجملة", "prompt": "The teacher helped ____.", "answer": "me", "options": ["I", "me", "my"]},
            {"title": "اقرأ بالمايك", "prompt": "She reads books.", "answer": "She reads books.", "options": [], "mic": "She reads books."},
        ],
    },
    {
        "id": "possessive-nouns",
        "title_ar": "أسماء الملكية",
        "title_en": "Possessive Nouns",
        "icon": "🔑",
        "worksheet": "possessive-nouns",
        "summary_ar": "نضيف apostrophe + s للاسم حتى نقول إن الشيء يخص شخصًا أو شيئًا.",
        "rule_en": "Add 's to a singular noun. Add an apostrophe after plural nouns ending in s.",
        "structure": "owner + 's + noun / plural owner + ' + noun",
        "groups": [
            {
                "id": "singular-owner",
                "title_ar": "مالك مفرد",
                "title_en": "Singular Owner",
                "entries": [
                    {"term": "Ali's bag", "arabic": "حقيبة علي", "use_ar": "مالك واحد", "example": "Ali's bag is blue.", "example_ar": "حقيبة علي زرقاء."},
                    {"term": "Sara's book", "arabic": "كتاب سارة", "use_ar": "مالك واحد", "example": "Sara's book is new.", "example_ar": "كتاب سارة جديد."},
                    {"term": "the boy's pencil", "arabic": "قلم الولد", "use_ar": "اسم مفرد + 's", "example": "The boy's pencil is red.", "example_ar": "قلم الولد أحمر."},
                    {"term": "the teacher's desk", "arabic": "مكتب المعلم", "use_ar": "اسم مفرد + 's", "example": "The teacher's desk is clean.", "example_ar": "مكتب المعلم نظيف."},
                ],
            },
            {
                "id": "plural-owner",
                "title_ar": "مالك جمع",
                "title_en": "Plural Owner",
                "entries": [
                    {"term": "the students' books", "arabic": "كتب الطلاب", "use_ar": "جمع ينتهي بـ s", "example": "The students' books are open.", "example_ar": "كتب الطلاب مفتوحة."},
                    {"term": "the girls' room", "arabic": "غرفة البنات", "use_ar": "جمع ينتهي بـ s", "example": "The girls' room is tidy.", "example_ar": "غرفة البنات مرتبة."},
                    {"term": "the teachers' lounge", "arabic": "استراحة المعلمين", "use_ar": "جمع ينتهي بـ s", "example": "The teachers' lounge is quiet.", "example_ar": "استراحة المعلمين هادئة."},
                ],
            },
        ],
        "activities": [
            {"title": "اختر الملكية", "prompt": "The bag belongs to Ali.", "answer": "Ali's bag", "options": ["Ali's bag", "Ali bag", "Alis bag"], "listen": "Ali's bag is blue."},
            {"title": "مفرد أم جمع؟", "prompt": "the students' books", "answer": "plural owner", "options": ["singular owner", "plural owner"]},
            {"title": "صحح الخطأ", "prompt": "Sara book is new.", "answer": "Sara's book is new.", "options": ["Sara's book is new.", "Saras book is new.", "Sara book's is new."]},
            {"title": "اقرأ بالمايك", "prompt": "The teacher's desk is clean.", "answer": "The teacher's desk is clean.", "options": [], "mic": "The teacher's desk is clean."},
        ],
    },
]


FOUNDATION_VOCABULARY_CATEGORIES = [
    {
        "id": "colors",
        "title_ar": "الألوان",
        "title_en": "Colors",
        "icon": "🎨",
        "worksheet": "colors",
        "words": [
            {"word": "red", "arabic": "أحمر", "icon": "🔴", "example": "red apple", "example_ar": "تفاحة حمراء"},
            {"word": "blue", "arabic": "أزرق", "icon": "🔵", "example": "blue bag", "example_ar": "حقيبة زرقاء"},
            {"word": "green", "arabic": "أخضر", "icon": "🟢", "example": "green tree", "example_ar": "شجرة خضراء"},
            {"word": "yellow", "arabic": "أصفر", "icon": "🟡", "example": "yellow sun", "example_ar": "شمس صفراء"},
            {"word": "black", "arabic": "أسود", "icon": "⚫", "example": "black pen", "example_ar": "قلم أسود"},
            {"word": "white", "arabic": "أبيض", "icon": "⚪", "example": "white milk", "example_ar": "حليب أبيض"},
            {"word": "orange", "arabic": "برتقالي", "icon": "🟠", "example": "orange ball", "example_ar": "كرة برتقالية"},
            {"word": "purple", "arabic": "بنفسجي", "icon": "🟣", "example": "purple flower", "example_ar": "زهرة بنفسجية"},
            {"word": "pink", "arabic": "وردي", "icon": "🌸", "example": "pink dress", "example_ar": "فستان وردي"},
            {"word": "brown", "arabic": "بني", "icon": "🟤", "example": "brown box", "example_ar": "صندوق بني"},
        ],
    },
    {
        "id": "animals",
        "title_ar": "الحيوانات",
        "title_en": "Animals",
        "icon": "🐾",
        "worksheet": "animals",
        "words": [
            {"word": "cat", "arabic": "قط", "icon": "🐱", "example": "The cat is small.", "example_ar": "القط صغير"},
            {"word": "dog", "arabic": "كلب", "icon": "🐶", "example": "The dog can run.", "example_ar": "الكلب يستطيع الركض"},
            {"word": "bird", "arabic": "طائر", "icon": "🐦", "example": "I see a bird.", "example_ar": "أرى طائرًا"},
            {"word": "fish", "arabic": "سمكة", "icon": "🐟", "example": "The fish is blue.", "example_ar": "السمكة زرقاء"},
            {"word": "cow", "arabic": "بقرة", "icon": "🐄", "example": "The cow is big.", "example_ar": "البقرة كبيرة"},
            {"word": "horse", "arabic": "حصان", "icon": "🐴", "example": "The horse is fast.", "example_ar": "الحصان سريع"},
            {"word": "lion", "arabic": "أسد", "icon": "🦁", "example": "The lion is strong.", "example_ar": "الأسد قوي"},
            {"word": "tiger", "arabic": "نمر", "icon": "🐯", "example": "The tiger is orange.", "example_ar": "النمر برتقالي"},
            {"word": "elephant", "arabic": "فيل", "icon": "🐘", "example": "The elephant is big.", "example_ar": "الفيل كبير"},
            {"word": "rabbit", "arabic": "أرنب", "icon": "🐰", "example": "The rabbit can jump.", "example_ar": "الأرنب يستطيع القفز"},
        ],
    },
    {
        "id": "family",
        "title_ar": "العائلة",
        "title_en": "Family",
        "icon": "👨‍👩‍👧‍👦",
        "worksheet": "family",
        "words": [
            {"word": "father", "arabic": "أب", "icon": "👨", "example": "This is my father.", "example_ar": "هذا أبي"},
            {"word": "mother", "arabic": "أم", "icon": "👩", "example": "This is my mother.", "example_ar": "هذه أمي"},
            {"word": "brother", "arabic": "أخ", "icon": "👦", "example": "He is my brother.", "example_ar": "هو أخي"},
            {"word": "sister", "arabic": "أخت", "icon": "👧", "example": "She is my sister.", "example_ar": "هي أختي"},
            {"word": "baby", "arabic": "طفل صغير", "icon": "👶", "example": "The baby is sleeping.", "example_ar": "الطفل الصغير نائم"},
            {"word": "grandfather", "arabic": "جد", "icon": "👴", "example": "My grandfather is kind.", "example_ar": "جدي لطيف"},
            {"word": "grandmother", "arabic": "جدة", "icon": "👵", "example": "My grandmother smiles.", "example_ar": "جدتي تبتسم"},
            {"word": "family", "arabic": "عائلة", "icon": "👨‍👩‍👧‍👦", "example": "I love my family.", "example_ar": "أحب عائلتي"},
            {"word": "uncle", "arabic": "عم / خال", "icon": "👨", "example": "My uncle is here.", "example_ar": "عمي أو خالي هنا"},
            {"word": "aunt", "arabic": "عمة / خالة", "icon": "👩", "example": "My aunt is happy.", "example_ar": "عمتي أو خالتي سعيدة"},
        ],
    },
    {
        "id": "feelings",
        "title_ar": "المشاعر",
        "title_en": "Feelings",
        "icon": "🙂",
        "worksheet": "feelings",
        "words": [
            {"word": "happy", "arabic": "سعيد", "icon": "🙂", "example": "I am happy.", "example_ar": "أنا سعيد"},
            {"word": "sad", "arabic": "حزين", "icon": "😢", "example": "She is sad.", "example_ar": "هي حزينة"},
            {"word": "angry", "arabic": "غاضب", "icon": "😡", "example": "He is angry.", "example_ar": "هو غاضب"},
            {"word": "tired", "arabic": "متعب", "icon": "😴", "example": "I am tired.", "example_ar": "أنا متعب"},
            {"word": "scared", "arabic": "خائف", "icon": "😨", "example": "I am scared.", "example_ar": "أنا خائف"},
            {"word": "excited", "arabic": "متحمس", "icon": "🤩", "example": "We are excited.", "example_ar": "نحن متحمسون"},
            {"word": "hungry", "arabic": "جائع", "icon": "😋", "example": "I am hungry.", "example_ar": "أنا جائع"},
            {"word": "thirsty", "arabic": "عطشان", "icon": "🥤", "example": "I am thirsty.", "example_ar": "أنا عطشان"},
            {"word": "sick", "arabic": "مريض", "icon": "🤒", "example": "He is sick.", "example_ar": "هو مريض"},
            {"word": "sleepy", "arabic": "نعسان", "icon": "😪", "example": "She is sleepy.", "example_ar": "هي نعسانة"},
        ],
    },
    {
        "id": "daily-verbs",
        "title_ar": "الأفعال اليومية",
        "title_en": "Daily Verbs",
        "icon": "🏃",
        "worksheet": "daily-verbs",
        "words": [
            {"word": "eat", "arabic": "يأكل", "icon": "🍽️", "example": "I eat an apple.", "example_ar": "أنا آكل تفاحة"},
            {"word": "drink", "arabic": "يشرب", "icon": "🥤", "example": "I drink water.", "example_ar": "أنا أشرب الماء"},
            {"word": "read", "arabic": "يقرأ", "icon": "📖", "example": "I read a book.", "example_ar": "أنا أقرأ كتابًا"},
            {"word": "write", "arabic": "يكتب", "icon": "✏️", "example": "I write my name.", "example_ar": "أنا أكتب اسمي"},
            {"word": "sleep", "arabic": "ينام", "icon": "🛌", "example": "I sleep at night.", "example_ar": "أنا أنام ليلًا"},
            {"word": "run", "arabic": "يركض", "icon": "🏃", "example": "I can run.", "example_ar": "أستطيع الركض"},
            {"word": "walk", "arabic": "يمشي", "icon": "🚶", "example": "We walk to school.", "example_ar": "نحن نمشي إلى المدرسة"},
            {"word": "play", "arabic": "يلعب", "icon": "⚽", "example": "We play football.", "example_ar": "نحن نلعب كرة القدم"},
            {"word": "listen", "arabic": "يستمع", "icon": "👂", "example": "Listen carefully.", "example_ar": "استمع جيدًا"},
            {"word": "speak", "arabic": "يتحدث", "icon": "🗣️", "example": "I speak English.", "example_ar": "أنا أتحدث الإنجليزية"},
        ],
    },
    {
        "id": "foods",
        "title_ar": "الأطعمة",
        "title_en": "Foods",
        "icon": "🍎",
        "worksheet": "foods",
        "words": [
            {"word": "apple", "arabic": "تفاحة", "icon": "🍎", "example": "I like apples.", "example_ar": "أحب التفاح"},
            {"word": "banana", "arabic": "موزة", "icon": "🍌", "example": "The banana is yellow.", "example_ar": "الموزة صفراء"},
            {"word": "bread", "arabic": "خبز", "icon": "🍞", "example": "This is bread.", "example_ar": "هذا خبز"},
            {"word": "rice", "arabic": "أرز", "icon": "🍚", "example": "I eat rice.", "example_ar": "آكل الأرز"},
            {"word": "egg", "arabic": "بيضة", "icon": "🥚", "example": "The egg is white.", "example_ar": "البيضة بيضاء"},
            {"word": "cheese", "arabic": "جبن", "icon": "🧀", "example": "I like cheese.", "example_ar": "أحب الجبن"},
            {"word": "chicken", "arabic": "دجاج", "icon": "🍗", "example": "Chicken is food.", "example_ar": "الدجاج طعام"},
            {"word": "fish", "arabic": "سمك", "icon": "🐟", "example": "I eat fish.", "example_ar": "آكل السمك"},
            {"word": "cake", "arabic": "كعكة", "icon": "🍰", "example": "The cake is sweet.", "example_ar": "الكعكة حلوة"},
            {"word": "pizza", "arabic": "بيتزا", "icon": "🍕", "example": "I like pizza.", "example_ar": "أحب البيتزا"},
        ],
    },
    {
        "id": "drinks",
        "title_ar": "المشروبات",
        "title_en": "Drinks",
        "icon": "🥤",
        "worksheet": "drinks",
        "words": [
            {"word": "water", "arabic": "ماء", "icon": "💧", "example": "I drink water.", "example_ar": "أشرب الماء"},
            {"word": "milk", "arabic": "حليب", "icon": "🥛", "example": "Milk is white.", "example_ar": "الحليب أبيض"},
            {"word": "juice", "arabic": "عصير", "icon": "🧃", "example": "I like juice.", "example_ar": "أحب العصير"},
            {"word": "tea", "arabic": "شاي", "icon": "🍵", "example": "Tea is hot.", "example_ar": "الشاي ساخن"},
            {"word": "coffee", "arabic": "قهوة", "icon": "☕", "example": "Coffee is a drink.", "example_ar": "القهوة مشروب"},
            {"word": "soda", "arabic": "مشروب غازي", "icon": "🥤", "example": "Soda is cold.", "example_ar": "المشروب الغازي بارد"},
            {"word": "lemonade", "arabic": "عصير ليمون", "icon": "🍋", "example": "Lemonade is yellow.", "example_ar": "عصير الليمون أصفر"},
            {"word": "hot chocolate", "arabic": "شوكولاتة ساخنة", "icon": "🍫", "example": "Hot chocolate is sweet.", "example_ar": "الشوكولاتة الساخنة حلوة"},
            {"word": "smoothie", "arabic": "عصير مخفوق", "icon": "🥤", "example": "The smoothie is pink.", "example_ar": "العصير المخفوق وردي"},
            {"word": "soup", "arabic": "شوربة", "icon": "🍲", "example": "Soup is hot.", "example_ar": "الشوربة ساخنة"},
        ],
    },
    {
        "id": "numbers",
        "title_ar": "الأرقام",
        "title_en": "Numbers",
        "icon": "🔢",
        "worksheet": "numbers",
        "words": [
            {"word": "one", "arabic": "واحد", "icon": "1", "example": "I have one pen.", "example_ar": "لدي قلم واحد"},
            {"word": "two", "arabic": "اثنان", "icon": "2", "example": "I see two cats.", "example_ar": "أرى قطتين"},
            {"word": "three", "arabic": "ثلاثة", "icon": "3", "example": "Three birds fly.", "example_ar": "ثلاثة طيور تطير"},
            {"word": "four", "arabic": "أربعة", "icon": "4", "example": "Four dogs run.", "example_ar": "أربعة كلاب تركض"},
            {"word": "five", "arabic": "خمسة", "icon": "5", "example": "There are five apples.", "example_ar": "هناك خمس تفاحات"},
            {"word": "six", "arabic": "ستة", "icon": "6", "example": "Six fish swim.", "example_ar": "ست سمكات تسبح"},
            {"word": "seven", "arabic": "سبعة", "icon": "7", "example": "I count seven.", "example_ar": "أعد إلى سبعة"},
            {"word": "eight", "arabic": "ثمانية", "icon": "8", "example": "Eight is a number.", "example_ar": "ثمانية رقم"},
            {"word": "nine", "arabic": "تسعة", "icon": "9", "example": "Nine pens are here.", "example_ar": "تسعة أقلام هنا"},
            {"word": "ten", "arabic": "عشرة", "icon": "10", "example": "Ten is after nine.", "example_ar": "عشرة بعد تسعة"},
            {"word": "eleven", "arabic": "أحد عشر", "icon": "11", "example": "Eleven is a number.", "example_ar": "أحد عشر رقم"},
            {"word": "twelve", "arabic": "اثنا عشر", "icon": "12", "example": "Twelve months make a year.", "example_ar": "اثنا عشر شهرًا تكوّن سنة"},
            {"word": "twenty", "arabic": "عشرون", "icon": "20", "example": "Twenty is two tens.", "example_ar": "عشرون تساوي عشرتين"},
            {"word": "thirty", "arabic": "ثلاثون", "icon": "30", "example": "Thirty is three tens.", "example_ar": "ثلاثون تساوي ثلاث عشرات"},
            {"word": "one hundred", "arabic": "مئة", "icon": "100", "example": "One hundred is 100.", "example_ar": "مئة هي 100"},
        ],
    },
]


FOUNDATION_VOCABULARY_CATEGORIES.append({
    "id": "calendar",
    "title_ar": "الأيام والأشهر",
    "title_en": "Days & Months",
    "icon": "📅",
    "worksheet": "calendar",
    "groups": CALENDAR_VOCABULARY_GROUPS,
    "words": CALENDAR_VOCABULARY_WORDS,
    "sentences": CALENDAR_DAILY_SENTENCES,
    "story": CALENDAR_MINI_STORY,
})


for foundation_category in FOUNDATION_VOCABULARY_CATEGORIES:
    if foundation_category["id"] == "animals":
        foundation_category.update({
            "title_ar": "الحيوانات",
            "icon": "🐾",
            "groups": ANIMAL_VOCABULARY_GROUPS,
            "words": ANIMAL_VOCABULARY_WORDS,
            "sentences": ANIMAL_DAILY_SENTENCES,
            "story": ANIMAL_MINI_STORY,
        })
    elif foundation_category["id"] == "foods":
        foundation_category.update({
            "title_ar": "الأطعمة",
            "icon": "🍽️",
            "groups": FOOD_VOCABULARY_GROUPS,
            "words": FOOD_VOCABULARY_WORDS,
            "sentences": FOOD_DAILY_SENTENCES,
            "story": FOOD_MINI_STORY,
        })


def foundation_vocabulary_total_words():
    return sum(len(category["words"]) for category in FOUNDATION_VOCABULARY_CATEGORIES)


def sound_pattern_total_units():
    active_groups = [group for group in SOUND_PATTERN_GROUPS if not group.get("locked")]
    active_group_ids = {group["id"] for group in active_groups}
    pattern_count = sum(len(group["patterns"]) for group in active_groups)
    example_count = sum(
        len(pattern["examples"])
        for group in active_groups
        for pattern in group["patterns"]
    )
    active_activity_count = sum(
        1 for activity in SOUND_PATTERN_ACTIVITIES if activity.get("category") in active_group_ids
    )
    return pattern_count + example_count + active_activity_count


def vowel_total_units():
    return len(VOWEL_LESSONS)


PAYMENT_METHODS = {
    "moyasar": {
        "method": PaymentOrder.Method.MOYASAR_CARD,
        "provider": PaymentOrder.Provider.MOYASAR,
        "status": PaymentOrder.Status.PENDING,
        "title": "الدفع عبر ميسر",
    },
    "stcpay": {
        "method": PaymentOrder.Method.MOYASAR_STCPAY,
        "provider": PaymentOrder.Provider.MOYASAR,
        "status": PaymentOrder.Status.PENDING,
        "title": "الدفع عبر STC Pay",
    },
    "bank_transfer": {
        "method": PaymentOrder.Method.BANK_TRANSFER,
        "provider": PaymentOrder.Provider.MANUAL_BANK,
        "status": PaymentOrder.Status.AWAITING_BANK_REVIEW,
        "title": "التحويل البنكي",
    },
}


def get_checkout_plan_or_404(plan_code):
    normalized_code = normalize_plan_code(plan_code)
    plan = CHECKOUT_PLANS.get(normalized_code)
    if not plan:
        raise Http404("Subscription plan not found.")
    return plan


def plan_amount_halalas(plan):
    return int((plan["price_sar"] * Decimal("100")).to_integral_value())


def bank_transfer_context():
    return {
        "enabled": getattr(settings, "BANK_TRANSFER_ENABLED", False),
        "account_name": getattr(settings, "BANK_ACCOUNT_NAME", ""),
        "bank_name": getattr(settings, "BANK_NAME", ""),
        "iban": getattr(settings, "BANK_IBAN", ""),
        "account_number": getattr(settings, "BANK_ACCOUNT_NUMBER", ""),
        "instructions": getattr(settings, "BANK_TRANSFER_INSTRUCTIONS", ""),
    }


def moyasar_context():
    publishable_key = getattr(settings, "MOYASAR_PUBLISHABLE_KEY", "")
    return {
        "enabled": bool(getattr(settings, "MOYASAR_ENABLED", False)),
        "publishable_key_configured": bool(publishable_key),
        "secret_key_configured": bool(getattr(settings, "MOYASAR_SECRET_KEY", "")),
        "callback_url_configured": bool(getattr(settings, "MOYASAR_CALLBACK_URL", "")),
        "environment": getattr(settings, "MOYASAR_ENVIRONMENT", "test"),
    }


def create_payment_order_for_plan(user, plan, method_slug, *, quote=None):
    method_config = PAYMENT_METHODS.get(method_slug)
    if not method_config:
        raise Http404("Payment method not found.")
    quote = quote or quote_plan_purchase(user, plan["code"])

    order = PaymentOrder(
        user=user,
        plan_code=plan["code"],
        plan_name=plan["name_ar"],
        duration_days=plan["duration_days"],
        operation_type=quote.operation_type,
        from_plan_code=quote.from_plan_code,
        to_plan_code=quote.target_plan_code,
        original_price=quote.original_price,
        target_price=quote.target_price,
        amount_due=quote.amount_due,
        current_expires_at=quote.current_expires_at,
        amount_halalas=int((quote.amount_due * Decimal("100")).to_integral_value()),
        amount_sar=quote.amount_due,
        currency="SAR",
        status=method_config["status"],
        method=method_config["method"],
        provider=method_config["provider"],
        payment_environment=(
            getattr(settings, "MOYASAR_ENVIRONMENT", PaymentOrder.Environment.TEST)
            if method_config["provider"] == PaymentOrder.Provider.MOYASAR
            else PaymentOrder.Environment.TEST
        ),
        provider_status="created_locally",
        metadata={
            "schema_version": 2,
            "user_id": user.id,
            "plan_code": plan["code"],
            "method": method_slug,
            "operation_type": quote.operation_type,
        },
    )
    order.full_clean()
    order.save()
    order.metadata = {
        **order.metadata,
        "payment_order_id": order.id,
        "quote_reference": str(order.idempotency_key),
    }
    order.save(update_fields=["metadata", "updated_at"])
    return order


def _moyasar_checkout_urls(request, order, plan):
    success_url = request.build_absolute_uri(
        f"{reverse('moyasar_callback')}?order={order.id}"
    )
    back_url = request.build_absolute_uri(reverse("checkout", args=[plan["code"]]))
    callback_url = getattr(settings, "MOYASAR_CALLBACK_URL", "").strip()
    return success_url, back_url, callback_url


def _record_moyasar_failure(order_id, creation_token, exc):
    if isinstance(exc, MoyasarConfigurationError):
        failure_code = "configuration_error"
    elif isinstance(exc, MoyasarNetworkError):
        failure_code = "network_error"
    elif isinstance(exc, MoyasarAPIError):
        failure_code = f"api_{exc.status_code}"
    else:
        failure_code = "invalid_provider_response"
    ambiguous = isinstance(exc, (MoyasarNetworkError, MoyasarInvalidResponseError))
    if isinstance(exc, MoyasarAPIError) and exc.status_code >= 500:
        ambiguous = True
    configuration_error = isinstance(exc, MoyasarConfigurationError)
    retryable = False
    if isinstance(exc, MoyasarAPIError) and exc.status_code == 429:
        retryable = True

    with transaction.atomic():
        order = PaymentOrder.objects.select_for_update().get(pk=order_id)
        if order.invoice_creation_token != creation_token or order.status != PaymentOrder.Status.CREATING_INVOICE:
            return order, "redirect" if order.moyasar_invoice_id and order.checkout_url else "pending"
        if ambiguous:
            order.status = PaymentOrder.Status.INVOICE_CREATION_UNKNOWN
            outcome = "unknown"
        elif configuration_error or retryable:
            order.status = PaymentOrder.Status.PENDING
            order.invoice_creation_token = None
            outcome = "error" if configuration_error else "pending"
        else:
            order.status = PaymentOrder.Status.FAILED
            order.invoice_creation_token = None
            order.failed_at = timezone.now()
            outcome = "error"
        order.provider_status = failure_code
        order.failure_code = failure_code
        order.failure_message = (
            "جاري التحقق من عملية الدفع."
            if ambiguous else "تعذر فتح صفحة الدفع حاليًا. حاول مرة أخرى."
        )
        order.save(update_fields=[
            "status", "invoice_creation_token", "provider_status", "failure_code",
            "failure_message", "failed_at", "updated_at",
        ])
    payment_logger.warning(
        "moyasar_invoice_start_failed payment_order_id=%s error_type=%s status_code=%s provider_request_id=%s",
        order_id,
        type(exc).__name__,
        getattr(exc, "status_code", "none"),
        getattr(exc, "request_id", "") or "missing",
    )
    return order, outcome


def start_moyasar_invoice_checkout(request, plan, method_slug):
    now = timezone.now()
    cutoff = now - timedelta(
        minutes=max(1, int(getattr(settings, "MOYASAR_ORDER_REUSE_MINUTES", 30)))
    )
    unknown_retry_cutoff = now - timedelta(
        minutes=max(1, int(getattr(settings, "MOYASAR_UNKNOWN_RETRY_MINUTES", 30)))
    )
    stale_creation_cutoff = now - timedelta(
        minutes=max(1, int(getattr(settings, "MOYASAR_INVOICE_CREATION_STALE_MINUTES", 5)))
    )

    # Phase one: short DB transaction. The user lock is only used to serialize the
    # no-existing-order case; no provider call occurs while this lock is held.
    with transaction.atomic():
        from django.contrib.auth import get_user_model
        get_user_model().objects.select_for_update().get(pk=request.user.pk)
        quote = quote_plan_purchase(request.user, plan["code"], now=now, lock=True)
        review_order = (
            PaymentOrder.objects.select_for_update()
            .filter(
                user=request.user,
                status=PaymentOrder.Status.PAID_REQUIRES_REVIEW,
            )
            .filter(Q(to_plan_code=plan["code"]) | Q(to_plan_code="", plan_code=plan["code"]))
            .order_by("-created_at")
            .first()
        )
        if review_order:
            return review_order, "pending"
        quoted_halalas = int((quote.amount_due * Decimal("100")).to_integral_value())
        recent_orders = list(
            PaymentOrder.objects.select_for_update()
            .filter(
                Q(to_plan_code=quote.target_plan_code) | Q(to_plan_code="", plan_code=plan["code"]),
                user=request.user,
                plan_code=plan["code"],
                operation_type=quote.operation_type,
                amount_halalas=quoted_halalas,
                currency="SAR",
                method=PAYMENT_METHODS[method_slug]["method"],
                provider=PaymentOrder.Provider.MOYASAR,
                created_at__gte=cutoff,
            )
            .order_by("-created_at")
        )

        paid_order = next((o for o in recent_orders if o.status == PaymentOrder.Status.PAID), None)
        if paid_order:
            return paid_order, "paid"

        for existing in recent_orders:
            if (
                existing.status == PaymentOrder.Status.INITIATED
                and existing.moyasar_invoice_id
                and existing.checkout_url
            ):
                try:
                    validate_moyasar_checkout_url(existing.checkout_url)
                    return existing, "redirect"
                except MoyasarInvalidResponseError:
                    existing.status = PaymentOrder.Status.FAILED
                    existing.provider_status = "unsafe_saved_checkout_url"
                    existing.failure_code = "unsafe_checkout_url"
                    existing.failure_message = "تعذر فتح صفحة الدفع حاليًا. حاول مرة أخرى."
                    existing.failed_at = timezone.now()
                    existing.save(update_fields=[
                        "status", "provider_status", "failure_code", "failure_message", "failed_at", "updated_at"
                    ])

        unknown_order = next(
            (o for o in recent_orders if o.status == PaymentOrder.Status.INVOICE_CREATION_UNKNOWN),
            None,
        )
        if unknown_order:
            if unknown_order.invoice_creation_started_at and unknown_order.invoice_creation_started_at > unknown_retry_cutoff:
                return unknown_order, "unknown"
            # No documented remote invoice idempotency exists. Retry only after the
            # configured waiting period and keep the same local PaymentOrder.
            unknown_order.status = PaymentOrder.Status.PENDING
            unknown_order.invoice_creation_token = None
            unknown_order.save(update_fields=["status", "invoice_creation_token", "updated_at"])

        creating_order = next(
            (o for o in recent_orders if o.status == PaymentOrder.Status.CREATING_INVOICE),
            None,
        )
        if creating_order:
            if (
                creating_order.invoice_creation_started_at
                and creating_order.invoice_creation_started_at <= stale_creation_cutoff
            ):
                creating_order.status = PaymentOrder.Status.INVOICE_CREATION_UNKNOWN
                creating_order.provider_status = "invoice_creation_stale"
                creating_order.failure_code = "invoice_creation_stale"
                creating_order.failure_message = "جاري التحقق من عملية الدفع."
                creating_order.save(update_fields=[
                    "status", "provider_status", "failure_code", "failure_message", "updated_at"
                ])
                return creating_order, "unknown"
            return creating_order, "pending"

        order = next(
            (
                o for o in recent_orders
                if o.status == PaymentOrder.Status.PENDING and not o.moyasar_invoice_id
            ),
            None,
        )
        if order is None:
            order = create_payment_order_for_plan(request.user, plan, method_slug, quote=quote)
        creation_token = uuid.uuid4()
        order.status = PaymentOrder.Status.CREATING_INVOICE
        order.provider_status = "creating_invoice"
        order.invoice_creation_token = creation_token
        order.invoice_creation_started_at = now
        order.failure_code = None
        order.failure_message = None
        order.save(update_fields=[
            "status", "provider_status", "invoice_creation_token", "invoice_creation_started_at",
            "failure_code", "failure_message", "updated_at",
        ])

    # External call: deliberately outside every transaction and row lock.
    try:
        if not getattr(settings, "MOYASAR_ENABLED", False):
            raise MoyasarConfigurationError("Moyasar payment is not enabled.")
        success_url, back_url, callback_url = _moyasar_checkout_urls(request, order, plan)
        invoice = create_moyasar_invoice(
            payment_order_id=order.id,
            user_id=request.user.id,
            plan_code=order.to_plan_code or order.plan_code,
            operation_type=order.operation_type,
            quote_reference=str(order.idempotency_key),
            amount_sar=order.amount_sar,
            amount_halalas=order.amount_halalas,
            currency=order.currency,
            description=f"ABCZ {order.plan_name} subscription - {order.reference}",
            success_url=success_url,
            back_url=back_url,
            callback_url=callback_url,
        )
    except (MoyasarConfigurationError, MoyasarNetworkError, MoyasarAPIError, MoyasarInvalidResponseError, ValueError) as exc:
        return _record_moyasar_failure(order.id, creation_token, exc)

    # Phase two: short transaction that only commits the result for this attempt.
    try:
        with transaction.atomic():
            locked = PaymentOrder.objects.select_for_update().get(pk=order.id)
            if locked.invoice_creation_token != creation_token or locked.status != PaymentOrder.Status.CREATING_INVOICE:
                if locked.moyasar_invoice_id and locked.checkout_url:
                    return locked, "redirect"
                return locked, "pending"
            locked.moyasar_invoice_id = invoice.invoice_id
            locked.checkout_url = invoice.checkout_url
            locked.payment_environment = PaymentOrder.Environment.TEST
            locked.provider = PaymentOrder.Provider.MOYASAR
            locked.status = PaymentOrder.Status.INITIATED
            locked.provider_status = invoice.status or "initiated"
            locked.failure_code = None
            locked.failure_message = None
            locked.failed_at = None
            locked.invoice_creation_token = None
            locked.full_clean()
            locked.save(update_fields=[
                "moyasar_invoice_id", "checkout_url", "payment_environment", "provider", "status",
                "provider_status", "failure_code", "failure_message", "failed_at",
                "invoice_creation_token", "updated_at",
            ])
    except (ValidationError, IntegrityError) as exc:
        payment_logger.warning(
            "moyasar_invoice_storage_rejected payment_order_id=%s error_type=%s",
            order.id,
            type(exc).__name__,
        )
        return _record_moyasar_failure(
            order.id,
            creation_token,
            MoyasarInvalidResponseError("Moyasar invoice could not be stored safely."),
        )
    return locked, "redirect"


def flatten_validation_errors(error):
    if hasattr(error, "message_dict"):
        messages_list = []
        for field_errors in error.message_dict.values():
            messages_list.extend(field_errors)
        return messages_list
    return list(getattr(error, "messages", [str(error)]))


def get_owned_payment_order_or_404(request, order_id):
    return get_object_or_404(PaymentOrder, pk=order_id, user=request.user)


def readable_payment_status_text(order, status_type):
    if order and order.status in {PaymentOrder.Status.PAID, PaymentOrder.Status.BANK_APPROVED}:
        return (
            "تم الدفع بنجاح",
            "تم تفعيل الاشتراك إذا كانت حالة الدفع مؤكدة من مزود الدفع.",
        )
    if order and order.status in {PaymentOrder.Status.FAILED, PaymentOrder.Status.BANK_REJECTED}:
        return (
            "لم تكتمل عملية الدفع",
            "يمكنك المحاولة مرة أخرى أو اختيار طريقة دفع أخرى.",
        )

    if order and order.status == PaymentOrder.Status.CANCELED:
        return (
            "تم إلغاء عملية الدفع",
            "لم يتم تنفيذ الدفع أو تفعيل الاشتراك. يمكنك المحاولة مرة أخرى.",
        )

    if order and order.provider_status == "callback_received_pending_provider_verification":
        return (
            "تم الرجوع من ميسر",
            "لم يتم تفعيل الاشتراك من بيانات الرابط فقط. يجب التحقق من حالة الدفع من ميسر قبل أي تفعيل.",
        )

    if (
        order
        and order.method == PaymentOrder.Method.BANK_TRANSFER
        and order.status == PaymentOrder.Status.AWAITING_BANK_REVIEW
    ):
        return (
            "التحويل البنكي قيد المراجعة",
            "تم رفع الإيصال والطلب قيد المراجعة. سيتم تفعيل الاشتراك بعد الاعتماد الإداري.",
        )

    return (
        "جاري التحقق من عملية الدفع",
        "لم يتم تأكيد الدفع بعد. لا يتم تفعيل الاشتراك إلا بعد التحقق النهائي من مزود الدفع.",
    )


def payment_status_payload(order, status_type, title, message):
    if order:
        title, message = readable_payment_status_text(order, status_type)
    if order and order.status in {PaymentOrder.Status.PAID, PaymentOrder.Status.BANK_APPROVED}:
        status_type = "success"
    elif order and order.status in {
        PaymentOrder.Status.FAILED,
        PaymentOrder.Status.EXPIRED,
        PaymentOrder.Status.BANK_REJECTED,
    }:
        status_type = "failed"
    elif order and order.status == PaymentOrder.Status.CANCELED:
        status_type = "canceled"
    elif order:
        status_type = "pending"
    return {
        "order": order,
        "status_type": status_type,
        "title": title,
        "message": message,
        "plan": CHECKOUT_PLANS.get(order.plan_code) if order else None,
    }


@require_GET
def pricing(request):
    if request.user.is_authenticated:
        options = purchase_options_for_user(request.user)
        snapshot = get_user_entitlements(request.user)
        current_main_plan = (
            CHECKOUT_PLANS.get(snapshot.main_subscription.plan_code)
            if snapshot.main_subscription else None
        )
    else:
        options = {
            code: {"allowed": True, "state": "purchase", "label": "اشترك الآن"}
            for code in CHECKOUT_PLANS
        }
        current_main_plan = None
    return render(request, "pricing.html", {
        "current_main_plan": current_main_plan,
        "basic_action": options[PLAN_BASIC],
        "silver_action": options[PLAN_SILVER],
        "vip_action": options[PLAN_VIP],
        "diamond_action": options[PLAN_DIAMOND],
        "level_3_action": options[PLAN_LEVEL_THREE],
        "level_4_action": options[PLAN_LEVEL_FOUR],
        "moyasar": moyasar_context(),
    })


@login_required
@require_GET
def checkout(request, plan_code):
    plan = get_checkout_plan_or_404(plan_code)
    try:
        quote = quote_plan_purchase(request.user, plan["code"])
        purchase_option = {
            "allowed": True,
            "state": quote.ui_state,
            "label": quote.ui_label,
            "amount_due": quote.amount_due,
            "operation_type": quote.operation_type,
        }
    except PurchaseNotAllowed as exc:
        if exc.code == "included_in_diamond":
            label = "مشمولة في باقتك الحالية"
        elif exc.code == "active_subscription":
            label = "مشترك حاليًا"
        else:
            label = "غير متاحة"
        purchase_option = {
            "allowed": False,
            "state": exc.code,
            "label": label,
            "message": str(exc),
        }
    return render(request, "checkout.html", {
        "plan": plan,
        "purchase_option": purchase_option,
        "moyasar": moyasar_context(),
        "bank_transfer": bank_transfer_context(),
        "payment_methods": PAYMENT_METHODS,
    })


@login_required
@require_POST
@rate_limit("payment-start", limit_setting="RATE_LIMIT_PAYMENT", default=10)
def create_payment_order(request, plan_code, method_slug):
    plan = get_checkout_plan_or_404(plan_code)
    if method_slug not in PAYMENT_METHODS:
        raise Http404("Payment method not found.")

    if method_slug == "bank_transfer" and not getattr(settings, "BANK_TRANSFER_ENABLED", False):
        try:
            quote_plan_purchase(request.user, plan["code"])
        except PurchaseNotAllowed as exc:
            raise PermissionDenied(str(exc)) from exc
        messages.error(request, "التحويل البنكي غير متاح حاليًا. اختر طريقة دفع أخرى.")
        return redirect("checkout", plan_code=plan["code"])

    if method_slug == "bank_transfer":
        try:
            with transaction.atomic():
                from django.contrib.auth import get_user_model
                get_user_model().objects.select_for_update().get(pk=request.user.pk)
                quote = quote_plan_purchase(request.user, plan["code"], lock=True)
                order = create_payment_order_for_plan(request.user, plan, method_slug, quote=quote)
        except PurchaseNotAllowed as exc:
            raise PermissionDenied(str(exc)) from exc
        messages.info(request, "تم إنشاء طلب التحويل البنكي. ارفع الإيصال بعد إتمام التحويل.")
        return redirect("bank_transfer_proof", order_id=order.id)

    try:
        order, outcome = start_moyasar_invoice_checkout(request, plan, method_slug)
    except PurchaseNotAllowed as exc:
        raise PermissionDenied(str(exc)) from exc
    if outcome == "redirect":
        return redirect(order.checkout_url)
    if outcome == "paid":
        return redirect(f"{reverse('payment_success')}?order={order.id}")
    if outcome in {"pending", "unknown"}:
        messages.info(request, "جاري التحقق من عملية الدفع.")
        return redirect(f"{reverse('payment_pending')}?order={order.id}")

    messages.error(request, "تعذر فتح صفحة الدفع حاليًا. حاول مرة أخرى.")
    return redirect("checkout", plan_code=plan["code"])


@login_required
@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
@rate_limit("bank-receipt", limit_setting="RATE_LIMIT_UPLOAD", default=10)
def bank_transfer_proof(request, order_id):
    order = get_owned_payment_order_or_404(request, order_id)
    if order.method != PaymentOrder.Method.BANK_TRANSFER:
        raise Http404("Bank transfer page is only available for bank transfer orders.")

    errors = []
    if request.method == "POST":
        receipt_file = request.FILES.get("receipt_file")
        transferred_at_raw = (request.POST.get("transferred_at") or "").strip()
        amount_raw = (request.POST.get("amount_sar") or "").strip()

        try:
            transferred_at = datetime.strptime(transferred_at_raw, "%Y-%m-%d").date()
        except ValueError:
            transferred_at = None
            errors.append("تاريخ التحويل غير صحيح.")

        try:
            amount_sar = Decimal(amount_raw)
        except (InvalidOperation, TypeError):
            amount_sar = None
            errors.append("مبلغ التحويل غير صحيح.")

        if not receipt_file:
            errors.append("ارفع ملف الإيصال بصيغة JPG أو PNG أو PDF.")

        if not errors:
            proof = BankTransferProof(
                payment_order=order,
                user=request.user,
                bank_name=(request.POST.get("bank_name") or "").strip(),
                sender_name=(request.POST.get("sender_name") or "").strip(),
                sender_account_last_digits=(request.POST.get("sender_account_last_digits") or "").strip(),
                transfer_reference=(request.POST.get("transfer_reference") or "").strip(),
                transferred_at=transferred_at,
                amount_sar=amount_sar,
                receipt_file=receipt_file,
                note=(request.POST.get("note") or "").strip(),
            )
            try:
                proof.full_clean()
                proof.save()
                order.status = PaymentOrder.Status.AWAITING_BANK_REVIEW
                order.provider_status = "bank_receipt_uploaded"
                order.save(update_fields=["status", "provider_status", "updated_at"])
                messages.success(request, "تم استلام الإيصال. سيتم التحقق وتفعيل الاشتراك بعد المراجعة.")
                return redirect(f"{reverse('payment_pending')}?order={order.id}&bank=1")
            except ValidationError as exc:
                errors.extend(flatten_validation_errors(exc))

    return render(request, "bank_transfer_proof.html", {
        "order": order,
        "plan": CHECKOUT_PLANS.get(order.plan_code),
        "bank_transfer": bank_transfer_context(),
        "errors": errors,
    }, status=400 if errors else 200)


@login_required
@require_GET
def payment_success(request):
    order = None
    if (request.GET.get("order") or "").isdigit():
        order = get_owned_payment_order_or_404(request, request.GET["order"])
    return render(request, "payment_status.html", payment_status_payload(
        order,
        "success",
        "تم الدفع بنجاح",
        "تم تفعيل الاشتراك إذا كانت حالة الدفع مؤكدة من مزود الدفع.",
    ))


@login_required
@require_GET
def payment_failed(request):
    order = None
    if (request.GET.get("order") or "").isdigit():
        order = get_owned_payment_order_or_404(request, request.GET["order"])
    return render(request, "payment_status.html", payment_status_payload(
        order,
        "failed",
        "لم تكتمل عملية الدفع",
        "يمكنك المحاولة مرة أخرى أو اختيار طريقة دفع أخرى.",
    ))


@login_required
@require_GET
def payment_pending(request):
    order = None
    if (request.GET.get("order") or "").isdigit():
        order = get_owned_payment_order_or_404(request, request.GET["order"])
    message = "عملية الدفع قيد المعالجة. لا يتم تفعيل الاشتراك إلا بعد نجاح الدفع أو اعتماد التحويل البنكي."
    if request.GET.get("bank"):
        message = "تم رفع الإيصال والطلب قيد المراجعة. سيتم تفعيل الاشتراك بعد الاعتماد الإداري."
    elif order and order.status == PaymentOrder.Status.PAID_REQUIRES_REVIEW:
        message = "تم استلام الدفع ويجري التحقق من الترقية. لن تُمنح صلاحيات جديدة حتى تكتمل المراجعة."
    return render(request, "payment_status.html", payment_status_payload(
        order,
        "pending",
        "الدفع قيد المعالجة",
        message,
    ))


@login_required
@require_GET
def moyasar_callback(request):
    order_value = request.GET.get("order") or ""
    order = None
    if order_value.isdigit():
        order = PaymentOrder.objects.filter(
            pk=order_value,
            user=request.user,
            provider=PaymentOrder.Provider.MOYASAR,
        ).first()
    if not order:
        invoice_value = str(request.GET.get("invoice_id") or request.GET.get("id") or "")
        masked_invoice = (
            f"{invoice_value[:4]}...{invoice_value[-4:]}" if len(invoice_value) > 8 else "missing"
        )
        payment_logger.warning(
            "moyasar_callback_order_missing request_id=%s invoice_id=%s",
            getattr(request, "request_id", "missing"),
            masked_invoice,
        )
        return render(request, "payment_status.html", payment_status_payload(
            None,
            "pending",
            "الدفع قيد التحقق",
            "تم استلام نتيجة الدفع، وجارٍ التحقق من العملية. لم يتم منح أي صلاحية حتى يكتمل التحقق.",
        ), status=202)

    # Browser query values are deliberately ignored. Reconciliation uses only the
    # locally stored invoice ID and the server-to-server Moyasar response.
    try:
        reconcile_payment_order(order.id)
    except Exception:
        payment_logger.exception(
            "moyasar_callback_reconciliation_error payment_order_id=%s", order.id
        )
    order.refresh_from_db()
    if order.status == PaymentOrder.Status.PAID and order.activated_at:
        destination = "payment_success"
    elif order.status in {
        PaymentOrder.Status.FAILED,
        PaymentOrder.Status.EXPIRED,
        PaymentOrder.Status.CANCELED,
    }:
        destination = "payment_failed"
    else:
        destination = "payment_pending"
    return redirect(f"{reverse(destination)}?order={order.id}")


@csrf_exempt
@require_POST
def moyasar_webhook(request):
    webhook_secret = str(getattr(settings, "MOYASAR_WEBHOOK_SECRET", "") or "")
    if not webhook_secret:
        return JsonResponse({
            "status": "webhook_disabled",
            "message": "Moyasar webhook is not enabled until MOYASAR_WEBHOOK_SECRET is configured.",
        }, status=503)

    max_body_bytes = max(1024, int(getattr(settings, "MOYASAR_WEBHOOK_MAX_BODY_BYTES", 65536)))
    try:
        content_length = int(request.META.get("CONTENT_LENGTH") or 0)
    except (TypeError, ValueError):
        return JsonResponse({"status": "invalid_content_length"}, status=400)
    if content_length > max_body_bytes:
        return JsonResponse({"status": "payload_too_large"}, status=413)
    raw_body = request.body
    if len(raw_body) > max_body_bytes:
        return JsonResponse({"status": "payload_too_large"}, status=413)
    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse({"status": "invalid_json"}, status=400)
    if not isinstance(payload, dict):
        return JsonResponse({"status": "invalid_payload"}, status=400)

    supplied_secret = payload.get("secret_token")
    if not isinstance(supplied_secret, str) or not secrets.compare_digest(
        supplied_secret, webhook_secret
    ):
        return JsonResponse({"status": "forbidden"}, status=403)

    event_id = payload.get("id")
    event_type = payload.get("type")
    event_live = payload.get("live")
    allowed_event_types = {
        "payment_paid",
        "payment_failed",
        "payment_refunded",
        "payment_voided",
        "payment_authorized",
        "payment_captured",
        "payment_verified",
    }
    if (
        not isinstance(event_id, str)
        or not event_id.strip()
        or len(event_id.strip()) > 120
        or event_type not in allowed_event_types
        or not isinstance(event_live, bool)
    ):
        return JsonResponse({"status": "invalid_event"}, status=400)
    if event_live or getattr(settings, "MOYASAR_ENVIRONMENT", "test") != "test":
        return JsonResponse({"status": "environment_mismatch"}, status=403)

    data = payload.get("data")
    invoice_id = data.get("invoice_id") if isinstance(data, dict) else None
    order = None
    if isinstance(invoice_id, str) and invoice_id:
        order = PaymentOrder.objects.filter(
            provider=PaymentOrder.Provider.MOYASAR,
            payment_environment=PaymentOrder.Environment.TEST,
            moyasar_invoice_id=invoice_id,
        ).first()

    try:
        with transaction.atomic():
            webhook_event = PaymentWebhookEvent.objects.create(
                provider=PaymentOrder.Provider.MOYASAR,
                event_id=event_id.strip(),
                event_type=event_type,
                payment_environment=PaymentOrder.Environment.TEST,
                payment_order=order,
                processing_status=PaymentWebhookEvent.ProcessingStatus.RECEIVED,
                payload_hash=hashlib.sha256(raw_body).hexdigest(),
            )
    except IntegrityError:
        return JsonResponse({"status": "duplicate"}, status=200)

    if order is None:
        webhook_event.processing_status = PaymentWebhookEvent.ProcessingStatus.IGNORED
        webhook_event.failure_code = "unknown_invoice"
        webhook_event.processed_at = timezone.now()
        webhook_event.save(update_fields=[
            "processing_status", "failure_code", "processed_at",
        ])
        return JsonResponse({"status": "accepted"}, status=202)

    webhook_event.processing_status = PaymentWebhookEvent.ProcessingStatus.PROCESSING
    webhook_event.save(update_fields=["processing_status"])
    try:
        result = reconcile_payment_order(order.id)
    except Exception:
        payment_logger.exception(
            "moyasar_webhook_reconciliation_error payment_order_id=%s event_id=%s",
            order.id,
            webhook_event.event_id,
        )
        webhook_event.processing_status = PaymentWebhookEvent.ProcessingStatus.FAILED
        webhook_event.failure_code = "reconciliation_error"
        response_status = 202
    else:
        status_map = {
            "paid": PaymentWebhookEvent.ProcessingStatus.PROCESSED,
            "failed": PaymentWebhookEvent.ProcessingStatus.PROCESSED,
            "expired": PaymentWebhookEvent.ProcessingStatus.PROCESSED,
            "canceled": PaymentWebhookEvent.ProcessingStatus.PROCESSED,
            "pending": PaymentWebhookEvent.ProcessingStatus.PENDING,
            "review": PaymentWebhookEvent.ProcessingStatus.PROCESSED,
            "mismatch": PaymentWebhookEvent.ProcessingStatus.MISMATCH,
            "invalid": PaymentWebhookEvent.ProcessingStatus.IGNORED,
        }
        webhook_event.processing_status = status_map.get(
            result.status, PaymentWebhookEvent.ProcessingStatus.FAILED
        )
        webhook_event.failure_code = result.code or None
        response_status = 200 if result.status not in {"pending"} else 202
    webhook_event.processed_at = timezone.now()
    webhook_event.save(update_fields=[
        "processing_status", "failure_code", "processed_at",
    ])
    return JsonResponse({"status": "accepted"}, status=response_status)


@cache_page(PUBLIC_PAGE_CACHE_TIMEOUT)
@require_GET
def start(request):
    return render(request, "start.html")


@cache_page(PUBLIC_PAGE_CACHE_TIMEOUT)
@require_GET
def levels(request):
    level_cards = [
        {
            "id": "level-1",
            "title": "المستوى الأول",
            "subtitle": "الحروف الإنجليزية A-Z",
            "description": "مناسب لمن يبدأ من الحروف أو يحتاج مراجعة الحروف والأصوات الأساسية.",
            "price": "بداية مجانية حسب الخطة الحالية",
            "button": "ابدأ المستوى الأول",
            "url": reverse("index"),
        },
        {
            "id": "level-2",
            "title": "المستوى الثاني",
            "subtitle": "الصوتيات والنطق",
            "description": "مناسب لمن يعرف الحروف ويريد تعلم الأصوات، حروف العلة، Digraphs، Ending Sounds، وTrigraphs.",
            "price": "ضمن باقة الصوتيات الحالية",
            "button": "ابدأ المستوى الثاني",
            "url": reverse("sounds"),
        },
        {
            "id": "level-3",
            "title": "المستوى الثالث",
            "subtitle": "قراءة CVC",
            "description": "مناسب لمن يعرف الحروف والصوتيات ويريد قراءة كلمات CVC والجمل والقصص القصيرة.",
            "price": "15 ريال شهريا",
            "button": "اشترك في المستوى الثالث",
            "url": reverse("pricing") + "#level-3-plan",
        },
        {
            "id": "level-4",
            "title": "المستوى الرابع",
            "subtitle": "قراءة واستماع وتحدث وكتابة",
            "description": "مناسب لمن يريد تطوير القراءة والاستماع والتحدث والكتابة والمحادثات والجمل الشائعة.",
            "price": "15 ريال شهريا",
            "button": "اشترك في المستوى الرابع",
            "url": reverse("pricing") + "#level-4-plan",
        },
    ]
    return render(request, "levels.html", {"level_cards": level_cards})


@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def placement_test(request):
    if request.method == "POST":
        data, error = parse_json_safely(request)
        if error:
            return error

        answers = data.get("answers")
        if not isinstance(answers, dict):
            return _json_error("answers must be an object", 400)

        return JsonResponse(score_placement_test(answers))

    questions = public_placement_questions()
    return render(request, "placement_test.html", {
        "questions": questions,
        "questions_json": json.dumps(questions, ensure_ascii=False),
    })


def build_curriculum_context():
    stages = [
        {
            "order": 1,
            "status": "available",
            "title_en": "Level 1: Letters A-Z",
            "title_ar": "المستوى الأول: الحروف الإنجليزية",
            "description_ar": "يتعلم المتعلم شكل الحرف، اسمه، صوته، كلمات عليه، كتابته، ثم يراجع من خلال ألعاب داخلية وشهادة إنجاز حسب الباقة.",
            "unlock_condition": "متاح حسب الباقة: Free للتجربة، Basic وما فوق للمسار الكامل.",
            "mastery_goal": "التعرف على A-Z والتمييز بين الحروف الكبيرة والصغيرة.",
            "certificate": "شهادة المستوى الأول حسب الإنجاز.",
            "lessons": ["Letter name", "Letter sound", "Writing", "Words", "Internal games", "Certificate"],
            "examples": ["A / a - ant", "B / b - ball", "C / c - cat"],
            "link": "/",
            "button_text": "افتح الحروف",
        },
        {
            "order": 2,
            "status": "available",
            "title_en": "Level 2: Sounds and Phonics",
            "title_ar": "المستوى الثاني: الصوتيات والنطق",
            "description_ar": "مسار صوتيات منظم يشمل المقاطع، CVC للتأسيس الصوتي، حروف العلة، Digraphs، Ending Sounds، Trigraphs، ومعاينة Advanced Patterns.",
            "unlock_condition": "Silver وما فوق.",
            "mastery_goal": "ربط شكل الصوت بالنطق والكلمة مع تدريبات مايك وأوراق عمل.",
            "certificate": "",
            "lessons": ["Syllables", "CVC sounds", "Vowels", "Digraphs", "Ending sounds", "Trigraphs", "Worksheets"],
            "examples": ["sh in ship", "ch in chair", "igh in night", "silent e in cake"],
            "link": "/sounds/",
            "button_text": "افتح الصوتيات",
        },
        {
            "order": 3,
            "status": "locked",
            "title_en": "Level 3: CVC Reading",
            "title_ar": "المستوى الثالث: قراءة الكلمات والجمل القصيرة",
            "description_ar": "ينتقل المتعلم من الصوت إلى قراءة كلمات CVC ثم الجمل والقصص القصيرة والضمائر والمراجعة.",
            "unlock_condition": "الباقة الماسية.",
            "mastery_goal": "قراءة كلمات وجمل قصيرة بثقة وتسجيل تقدم القراءة.",
            "certificate": "شهادة CVC عند اكتمال المسار.",
            "lessons": ["CVC words", "Word families", "Sentences", "Short stories", "Pronouns", "Worksheets"],
            "examples": ["cat", "bed", "sun", "The cat can run."],
            "link": "/cvc-reading/",
            "button_text": "افتح قراءة CVC",
        },
        {
            "order": 4,
            "status": "locked",
            "title_en": "Level 4: English Foundation",
            "title_ar": "المستوى الرابع: التأسيس الإنجليزي الكامل",
            "description_ar": "قراءة، استماع، تحدث، كتابة، قصص، أوراق عمل، اختبار نهائي، وشهادة مستوى.",
            "unlock_condition": "الباقة الماسية.",
            "mastery_goal": "استخدام الإنجليزية في مواقف يومية بسيطة ومنظمة.",
            "certificate": "شهادة المستوى الرابع عند اكتمال الاختبار.",
            "lessons": ["Reading", "Listening", "Speaking", "Writing", "Stories", "Exam"],
            "examples": ["Introduce yourself.", "Read a short passage.", "Write about your school day."],
            "link": "/level-four/",
            "button_text": "افتح المستوى الرابع",
        },
    ]
    return {
        "stages": stages,
        "progress_steps": ["الحروف", "الصوتيات", "قراءة CVC", "التأسيس الإنجليزي"],
    }


@cache_page(PUBLIC_PAGE_CACHE_TIMEOUT)
@require_GET
def curriculum(request):
    return render(request, "curriculum.html", build_curriculum_context())


@cache_page(PUBLIC_PAGE_CACHE_TIMEOUT)
@require_GET
def about(request):
    return render(request, "about.html")


@cache_page(PUBLIC_PAGE_CACHE_TIMEOUT)
@require_GET
def guide(request):
    return render(request, "guide.html")


@cache_page(PUBLIC_PAGE_CACHE_TIMEOUT)
@require_GET
def privacy(request):
    return render(request, "privacy.html")


@cache_page(PUBLIC_PAGE_CACHE_TIMEOUT)
@require_GET
def terms(request):
    return render(request, "terms.html")


@ensure_csrf_cookie
@require_GET
def sounds(request):
    blocked = require_feature(request, "sounds_basic", UPGRADE_SILVER_OR_HIGHER_MESSAGE)
    if blocked:
        return blocked

    progress = None
    profile = None
    if request.user.is_authenticated:
        progress, _ = SoundPracticeProgress.objects.get_or_create(user=request.user)
        profile = get_or_create_student_profile(request.user)

    progress_payload = {
        "completed_items": progress.completed_items if progress else [],
        "quiz_attempts": progress.quiz_attempts if progress else 0,
        "quiz_correct": progress.quiz_correct if progress else 0,
        "mic_attempts": progress.mic_attempts if progress else 0,
        "mic_success": progress.mic_success if progress else 0,
        "worksheet_downloads": progress.worksheet_downloads if progress else 0,
        "last_item": progress.last_item if progress else "",
        "vowel_lessons_completed": progress.vowel_lessons_completed if progress else 0,
        "practiced_vowels": progress.practiced_vowels if progress else [],
        "vowel_quiz_attempts": progress.vowel_quiz_attempts if progress else 0,
        "vowel_quiz_correct": progress.vowel_quiz_correct if progress else 0,
        "vowel_microphone_attempts": progress.vowel_microphone_attempts if progress else 0,
        "vowel_microphone_success": progress.vowel_microphone_success if progress else 0,
        "last_vowel_practiced": progress.last_vowel_practiced if progress else "",
        "vowel_mastery_percentage": progress.vowel_mastery_percentage if progress else 0,
        "last_payload": progress.last_payload if progress else {},
    }

    return render(request, "sounds.html", {
        "syllable_rows_json": json.dumps(SOUND_SYLLABLE_ROWS, ensure_ascii=False),
        "cvc_words_json": json.dumps(SOUND_CVC_WORDS, ensure_ascii=False),
        "quiz_questions_json": json.dumps(SOUND_QUIZ_QUESTIONS, ensure_ascii=False),
        "vowel_lessons_json": json.dumps(VOWEL_LESSONS, ensure_ascii=False),
        "vowel_activities_json": json.dumps(VOWEL_ACTIVITIES, ensure_ascii=False),
        "sound_pattern_groups_json": json.dumps(SOUND_PATTERN_GROUPS, ensure_ascii=False),
        "sound_pattern_activities_json": json.dumps(SOUND_PATTERN_ACTIVITIES, ensure_ascii=False),
        "foundation_vocabulary_json": json.dumps(FOUNDATION_VOCABULARY_CATEGORIES, ensure_ascii=False),
        "level_two_grammar_json": json.dumps(LEVEL_TWO_GRAMMAR_LESSONS, ensure_ascii=False),
        "sound_progress_json": json.dumps(progress_payload, ensure_ascii=False),
        "student_display_name": (
            (profile.display_name or profile.student_name or request.user.username)
            if profile and request.user.is_authenticated
            else ""
        ),
    })


@require_GET
def sounds_worksheet(request):
    blocked = require_feature(request, "sounds_worksheets", "أوراق عمل الصوتيات متاحة في Silver أو باقة أعلى.")
    if blocked:
        return blocked

    return render(request, "sounds_worksheet.html", {
        "syllable_rows": SOUND_SYLLABLE_ROWS,
        "cvc_words": SOUND_CVC_WORDS,
        "quiz_questions": SOUND_QUIZ_QUESTIONS,
        "vowel_lessons": VOWEL_LESSONS,
        "vowel_activities": VOWEL_ACTIVITIES,
        "sound_pattern_groups": SOUND_PATTERN_GROUPS,
        "sound_pattern_activities": SOUND_PATTERN_ACTIVITIES,
        "foundation_vocabulary": FOUNDATION_VOCABULARY_CATEGORIES,
        "level_two_grammar_lessons": LEVEL_TWO_GRAMMAR_LESSONS,
    })


@require_http_methods(["GET", "POST"])
def sound_progress_api(request):
    blocked = require_feature(request, "sounds_basic", UPGRADE_SILVER_OR_HIGHER_MESSAGE)
    if blocked:
        return blocked

    if not request.user.is_authenticated:
        return JsonResponse({"authenticated": False, "message": "local_only"})

    progress, _ = SoundPracticeProgress.objects.get_or_create(user=request.user)

    if request.method == "GET":
        return JsonResponse({
            "authenticated": True,
            "completed_items": progress.completed_items,
            "quiz_attempts": progress.quiz_attempts,
            "quiz_correct": progress.quiz_correct,
            "mic_attempts": progress.mic_attempts,
            "mic_success": progress.mic_success,
            "worksheet_downloads": progress.worksheet_downloads,
            "last_item": progress.last_item,
            "last_payload": progress.last_payload,
            "vowel_lessons_completed": progress.vowel_lessons_completed,
            "practiced_vowels": progress.practiced_vowels,
            "vowel_quiz_attempts": progress.vowel_quiz_attempts,
            "vowel_quiz_correct": progress.vowel_quiz_correct,
            "vowel_microphone_attempts": progress.vowel_microphone_attempts,
            "vowel_microphone_success": progress.vowel_microphone_success,
            "last_vowel_practiced": progress.last_vowel_practiced,
            "vowel_mastery_percentage": progress.vowel_mastery_percentage,
        })

    data, error = parse_json_safely(request)
    if error:
        return error

    tracked_fields = [
        "completed_items",
        "quiz_attempts",
        "quiz_correct",
        "mic_attempts",
        "mic_success",
        "worksheet_downloads",
        "last_item",
        "last_payload",
        "vowel_lessons_completed",
        "practiced_vowels",
        "vowel_quiz_attempts",
        "vowel_quiz_correct",
        "vowel_microphone_attempts",
        "vowel_microphone_success",
        "last_vowel_practiced",
        "vowel_mastery_percentage",
    ]
    before_state = {field: getattr(progress, field) for field in tracked_fields}

    completed_items = data.get("completed_items")
    if isinstance(completed_items, list):
        progress.completed_items = [str(item)[:80] for item in completed_items[:300]]

    progress.quiz_attempts = max(progress.quiz_attempts, int(data.get("quiz_attempts") or 0))
    progress.quiz_correct = max(progress.quiz_correct, int(data.get("quiz_correct") or 0))
    progress.mic_attempts = max(progress.mic_attempts, int(data.get("mic_attempts") or 0))
    progress.mic_success = max(progress.mic_success, int(data.get("mic_success") or 0))
    progress.worksheet_downloads = max(progress.worksheet_downloads, int(data.get("worksheet_downloads") or 0))
    progress.last_item = str(data.get("last_item") or "")[:80]
    progress.last_payload = data.get("last_payload") if isinstance(data.get("last_payload"), dict) else {}
    practiced_vowels = data.get("practiced_vowels")
    if isinstance(practiced_vowels, list):
        progress.practiced_vowels = [
            str(item).upper()[:2]
            for item in practiced_vowels[:10]
            if str(item).upper()[:1] in {"A", "E", "I", "O", "U", "Y"}
        ]
    progress.vowel_lessons_completed = max(progress.vowel_lessons_completed, int(data.get("vowel_lessons_completed") or 0))
    progress.vowel_quiz_attempts = max(progress.vowel_quiz_attempts, int(data.get("vowel_quiz_attempts") or 0))
    progress.vowel_quiz_correct = max(progress.vowel_quiz_correct, int(data.get("vowel_quiz_correct") or 0))
    progress.vowel_microphone_attempts = max(progress.vowel_microphone_attempts, int(data.get("vowel_microphone_attempts") or 0))
    progress.vowel_microphone_success = max(progress.vowel_microphone_success, int(data.get("vowel_microphone_success") or 0))
    progress.last_vowel_practiced = str(data.get("last_vowel_practiced") or "")[:12]
    incoming_vowel_mastery = int(data.get("vowel_mastery_percentage") or 0)
    progress.vowel_mastery_percentage = max(
        progress.vowel_mastery_percentage,
        max(0, min(100, incoming_vowel_mastery)),
    )
    changed_fields = [
        field
        for field in tracked_fields
        if getattr(progress, field) != before_state[field]
    ]
    changed = bool(changed_fields)
    if changed:
        progress.last_used_at = timezone.now()
        progress.save(update_fields=changed_fields + ["last_used_at", "updated_at"])

    return JsonResponse({
        "status": "ok",
        "authenticated": True,
        "changed": changed,
        "completed_items": progress.completed_items,
        "quiz_attempts": progress.quiz_attempts,
        "quiz_correct": progress.quiz_correct,
        "mic_attempts": progress.mic_attempts,
        "mic_success": progress.mic_success,
        "worksheet_downloads": progress.worksheet_downloads,
        "vowel_lessons_completed": progress.vowel_lessons_completed,
        "practiced_vowels": progress.practiced_vowels,
        "vowel_quiz_attempts": progress.vowel_quiz_attempts,
        "vowel_quiz_correct": progress.vowel_quiz_correct,
        "vowel_microphone_attempts": progress.vowel_microphone_attempts,
        "vowel_microphone_success": progress.vowel_microphone_success,
        "last_vowel_practiced": progress.last_vowel_practiced,
        "vowel_mastery_percentage": progress.vowel_mastery_percentage,
    })




@require_GET
def leaderboard(request):
    blocked = require_feature(request, "leaderboard", UPGRADE_VIP_OR_FULL_MESSAGE)
    if blocked:
        return blocked

    try:
        rows = build_leaderboard_rows(request.GET)
        return render(request, "phonics/leaderboard.html", {
            "rows": rows,
            "period": request.GET.get("period", "all"),
            "type_filter": request.GET.get("type", "all"),
            "grade_filter": request.GET.get("grade", ""),
            "search_query": request.GET.get("search", ""),
            "grade_options": sorted({row["grade"] for row in rows if row["grade"]}),
        })
    except Exception as e:
        return render(request, "phonics/leaderboard.html", {
            "rows": [],
            "error": "Failed to load leaderboard",
            "details": str(e),
            "period": "all",
            "type_filter": "all",
            "grade_filter": "",
            "search_query": "",
            "grade_options": [],
        })


@require_GET
def leaderboard_api(request):
    blocked = require_feature(request, "leaderboard", UPGRADE_VIP_OR_FULL_MESSAGE)
    if blocked:
        return blocked

    try:
        return JsonResponse({"rows": build_leaderboard_rows(request.GET)})
    except Exception:
        logger.exception("leaderboard_load_failed request_id=%s", getattr(request, "request_id", ""))
        return _json_error("Failed to load leaderboard", 500, request_id=getattr(request, "request_id", ""))


def get_leaderboard_period_start(period):
    now = timezone.now()
    if period in {"daily", "today"}:
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    if period == "weekly":
        return now - timedelta(days=7)
    if period == "monthly":
        return now - timedelta(days=30)
    return None


def normalize_leaderboard_grade(value):
    return (value or "").strip() or "غير محدد"


def build_achievement(completed_letters, has_certificate, total_points):
    if has_certificate:
        return "شهادة الحروف", True, "شهادة إتقان الحروف"
    if completed_letters >= 26:
        return "أنهى الحروف", False, ""
    if total_points > 0:
        return "الأكثر تفاعلًا", False, ""
    return "مشارك جديد", False, ""


def score_letter_progress(progress_entries):
    points = 0
    completed_letters = set()

    for progress in progress_entries:
        base_score = progress.total_score if progress.user_id else progress.score
        points += int(base_score or 0)
        if progress.completed or progress.passed:
            completed_letters.add(progress.letter)
            points += 7

    if len(completed_letters) >= 26:
        points += 100
        points += 150

    return points, len(completed_letters)


def score_sound_progress(progress):
    if not progress:
        return 0
    completed_items = progress.completed_items or []
    practiced_vowels = progress.practiced_vowels or []
    points = len(completed_items) * 5
    points += int(progress.quiz_attempts or 0) * 10
    points += int(progress.mic_success or 0) * 5
    points += int(progress.vowel_lessons_completed or 0)
    points += len(practiced_vowels) * 5
    points += int(progress.vowel_quiz_attempts or 0) * 10
    points += int(progress.vowel_microphone_success or 0) * 5
    return points


def score_cvc_reading_progress(progress):
    if not progress:
        return 0
    points = 0
    points += len(progress.completed_lessons or []) * 5
    points += len(progress.words_mastered or []) * 5
    points += int(progress.sentences_read or 0) * 5
    points += int(progress.sentence_quiz_attempts or 0) * 10
    points += int(progress.sentence_microphone_success or 0) * 5
    points += int(progress.stories_completed or 0) * 10
    points += int(progress.story_quiz_attempts or 0) * 10
    points += int(progress.story_microphone_success or 0) * 5
    points += int(progress.pronoun_lessons_completed or 0) * 5
    points += len(progress.pronouns_mastered or []) * 5
    points += int(progress.fluency_attempts or 0) * 10
    points += int(progress.conversations_completed or 0) * 10
    points += len(progress.action_verbs_mastered or []) * 5
    points += len(progress.adjectives_mastered or []) * 5
    return points


def activity_matches_period(*timestamps, period_start=None):
    if not period_start:
        return True
    return any(ts and ts >= period_start for ts in timestamps)


def leaderboard_cache_key(period, type_filter, grade_filter, search_query):
    normalized = "|".join([
        str(period or "all").strip().lower(),
        str(type_filter or "all").strip().lower(),
        str(grade_filter or "").strip().lower(),
        str(search_query or "").strip().lower(),
        f"limit:{LEADERBOARD_LIMIT}",
    ])
    return f"leaderboard:{CVC_CONTENT_CACHE_VERSION}:{normalized}"


def _leaderboard_row(student_name, grade, total_points, completed_letters):
    has_certificate = completed_letters >= 26
    achievement_type, has_certificate, certificate_title = build_achievement(
        completed_letters,
        has_certificate,
        total_points,
    )
    return {
        "rank": 0,
        "student_name": student_name,
        "grade": normalize_leaderboard_grade(grade),
        "total_points": total_points,
        "achievement_type": achievement_type,
        "has_certificate": has_certificate,
        "certificate_title": certificate_title,
    }


def build_leaderboard_rows(params):
    period = (params.get("period") or "all").strip()
    type_filter = (params.get("type") or "all").strip()
    grade_filter = (params.get("grade") or "").strip()
    search_query = (params.get("search") or "").strip().lower()
    period_start = get_leaderboard_period_start(period)
    cache_key = leaderboard_cache_key(period, type_filter, grade_filter, search_query)
    cached = safe_cache_get(cache_key)
    if isinstance(cached, list):
        return cached

    rows = []

    student_progress_qs = (
        LetterProgress.objects
        .filter(student__isnull=False)
        .values("student_id", "student__name", "student__grade")
        .annotate(
            letter_points=Sum("score"),
            completed_letters=Count("letter", filter=Q(completed=True) | Q(passed=True), distinct=True),
            last_activity=Max("timestamp"),
        )
    )
    if period_start:
        student_progress_qs = student_progress_qs.filter(timestamp__gte=period_start)
    if grade_filter:
        student_progress_qs = student_progress_qs.filter(student__grade=grade_filter)
    if search_query:
        student_progress_qs = student_progress_qs.filter(student__name__icontains=search_query)

    cvc_by_student = {
        row["student_id"]: row
        for row in CVCProgress.objects.values("student_id", "total_score", "last_activity")
    }

    seen_students = set()
    for summary in student_progress_qs:
        student_id = summary["student_id"]
        seen_students.add(student_id)
        completed_letters = int(summary["completed_letters"] or 0)
        letter_points = int(summary["letter_points"] or 0) + (completed_letters * 7)
        if completed_letters >= 26:
            letter_points += 250
        cvc_progress = cvc_by_student.get(student_id) or {}
        if period_start and cvc_progress and not activity_matches_period(
            summary.get("last_activity"),
            cvc_progress.get("last_activity"),
            period_start=period_start,
        ):
            continue
        total_points = letter_points + int(cvc_progress.get("total_score") or 0)
        rows.append(_leaderboard_row(
            summary["student__name"],
            summary["student__grade"],
            total_points,
            completed_letters,
        ))

    cvc_student_ids = set(cvc_by_student) - seen_students
    if cvc_student_ids:
        cvc_students = Student.objects.filter(id__in=cvc_student_ids)
        if grade_filter:
            cvc_students = cvc_students.filter(grade=grade_filter)
        if search_query:
            cvc_students = cvc_students.filter(name__icontains=search_query)
        student_labels = {
            row["id"]: row
            for row in cvc_students.values("id", "name", "grade")
        }
        for student_id, cvc_progress in cvc_by_student.items():
            if student_id not in student_labels:
                continue
            if period_start and not activity_matches_period(cvc_progress.get("last_activity"), period_start=period_start):
                continue
            student = student_labels[student_id]
            rows.append(_leaderboard_row(
                student["name"],
                student["grade"],
                int(cvc_progress.get("total_score") or 0),
                0,
            ))

    user_progress_qs = (
        LetterProgress.objects
        .filter(user__isnull=False)
        .values("user_id")
        .annotate(
            letter_points=Sum("total_score"),
            completed_letters=Count("letter", filter=Q(completed=True) | Q(passed=True), distinct=True),
            last_activity=Max("last_updated_at"),
        )
    )
    if period_start:
        user_progress_qs = user_progress_qs.filter(last_updated_at__gte=period_start)
    progress_by_user = {row["user_id"]: row for row in user_progress_qs}

    english_progress_qs = EnglishFoundationProgress.objects.values("user_id").annotate(
        points=Sum("points"),
        last_activity=Max("last_activity_at"),
    )
    if period_start:
        english_progress_qs = english_progress_qs.filter(last_activity_at__gte=period_start)
    english_progress_by_user = {row["user_id"]: row for row in english_progress_qs}

    profile_qs = StudentProfile.objects.select_related(
        "user",
        "user__sound_practice_progress",
        "user__cvc_reading_progress",
        "user__bird_tutor_progress",
    )
    if grade_filter:
        profile_qs = profile_qs.filter(grade=grade_filter)
    if search_query:
        profile_qs = profile_qs.filter(
            Q(display_name__icontains=search_query)
            | Q(student_name__icontains=search_query)
            | Q(user__username__icontains=search_query)
        )

    for profile in profile_qs:
        letter_summary = progress_by_user.get(profile.user_id) or {}
        sound_progress = getattr(profile.user, "sound_practice_progress", None)
        cvc_reading_progress = getattr(profile.user, "cvc_reading_progress", None)
        bird_progress = getattr(profile.user, "bird_tutor_progress", None)
        english_summary = english_progress_by_user.get(profile.user_id) or {}

        if not any([letter_summary, sound_progress, cvc_reading_progress, bird_progress, english_summary]):
            continue
        if not activity_matches_period(
            letter_summary.get("last_activity"),
            sound_progress.updated_at if sound_progress else None,
            cvc_reading_progress.updated_at if cvc_reading_progress else None,
            bird_progress.updated_at if bird_progress else None,
            english_summary.get("last_activity"),
            period_start=period_start,
        ):
            continue

        completed_letters = int(letter_summary.get("completed_letters") or 0)
        letter_points = int(letter_summary.get("letter_points") or 0) + (completed_letters * 7)
        if completed_letters >= 26:
            letter_points += 250
        total_points = letter_points
        total_points += score_sound_progress(sound_progress)
        total_points += score_cvc_reading_progress(cvc_reading_progress)
        total_points += int(getattr(bird_progress, "xp", 0) or 0)
        total_points += int(english_summary.get("points") or 0)

        rows.append(_leaderboard_row(
            profile.display_name or profile.student_name or profile.user.username,
            profile.grade,
            total_points,
            completed_letters,
        ))

    if type_filter == "letters_completed":
        rows = [row for row in rows if row["achievement_type"] in {"أنهى الحروف", "شهادة الحروف"}]
    elif type_filter == "letters_certificate":
        rows = [row for row in rows if row["has_certificate"]]

    if grade_filter:
        rows = [row for row in rows if row["grade"] == grade_filter]
    if search_query:
        rows = [row for row in rows if search_query in row["student_name"].lower()]

    rows.sort(key=lambda row: (-row["total_points"], row["student_name"]))
    rows = rows[:LEADERBOARD_LIMIT]
    for index, row in enumerate(rows, start=1):
        row["rank"] = index

    safe_cache_set(cache_key, rows, timeout=LEADERBOARD_CACHE_TIMEOUT)
    return rows


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
    blocked = require_feature(request, "wordwall_level1", UPGRADE_VIP_OR_FULL_MESSAGE)
    if blocked:
        return blocked

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

def serialize_cvc_reading_progress(progress):
    if not progress:
        return {
            "completed_levels": [],
            "completed_lessons": [],
            "completed_families": [],
            "words_practiced": [],
            "words_mastered": [],
            "sentences_read": 0,
            "sentences_mastered": [],
            "sentence_quiz_attempts": 0,
            "sentence_quiz_correct": 0,
            "sentence_microphone_attempts": 0,
            "sentence_microphone_success": 0,
            "last_sentence": "",
            "last_sentence_level": "",
            "common_sentences_completed": 0,
            "numbers_completed": 0,
            "days_completed": 0,
            "months_completed": 0,
            "sentence_mastery_percentage": 0,
            "sentence_best_time_seconds": 0,
            "sentence_total_time_seconds": 0,
            "stories_completed": 0,
            "stories_started": [],
            "story_quiz_attempts": 0,
            "story_quiz_correct": 0,
            "story_microphone_attempts": 0,
            "story_microphone_success": 0,
            "last_story": "",
            "last_story_level": "",
            "story_mastery_percentage": 0,
            "story_best_reading_time": 0,
            "story_needs_review": [],
            "pronoun_lessons_completed": 0,
            "pronouns_practiced": [],
            "pronouns_mastered": [],
            "pronoun_quiz_attempts": 0,
            "pronoun_quiz_correct": 0,
            "pronoun_microphone_attempts": 0,
            "pronoun_microphone_success": 0,
            "last_pronoun": "",
            "last_pronoun_level": "",
            "pronoun_mastery_percentage": 0,
            "pronouns_needs_review": [],
            "sight_words_practiced": [],
            "sight_words_mastered": [],
            "sight_word_quiz_attempts": 0,
            "sight_word_quiz_correct": 0,
            "fluency_sentences_read": 0,
            "fluency_attempts": 0,
            "best_wpm": 0,
            "best_reading_time": 0,
            "fluency_accuracy": 0,
            "fluency_score": 0,
            "question_words_mastered": [],
            "conversations_completed": 0,
            "action_verbs_mastered": [],
            "adjectives_mastered": [],
            "last_fluency_sentence": "",
            "last_sight_word": "",
            "last_conversation": "",
            "fluency_mastery_percentage": 0,
            "quiz_attempts": 0,
            "quiz_correct": 0,
            "mic_attempts": 0,
            "mic_success": 0,
            "last_word": "",
            "last_family": "",
            "last_level": "",
            "cvc_mastery_percentage": 0,
            "needs_review_words": [],
        }

    return {
        "completed_levels": progress.completed_levels or [],
        "completed_lessons": progress.completed_lessons or [],
        "completed_families": progress.completed_families or [],
        "words_practiced": progress.words_practiced or [],
        "words_mastered": progress.words_mastered or [],
        "sentences_read": progress.sentences_read,
        "sentences_mastered": progress.sentences_mastered or [],
        "sentence_quiz_attempts": progress.sentence_quiz_attempts,
        "sentence_quiz_correct": progress.sentence_quiz_correct,
        "sentence_microphone_attempts": progress.sentence_microphone_attempts,
        "sentence_microphone_success": progress.sentence_microphone_success,
        "last_sentence": progress.last_sentence,
        "last_sentence_level": progress.last_sentence_level,
        "common_sentences_completed": progress.common_sentences_completed,
        "numbers_completed": progress.numbers_completed,
        "days_completed": progress.days_completed,
        "months_completed": progress.months_completed,
        "sentence_mastery_percentage": progress.sentence_mastery_percentage,
        "sentence_best_time_seconds": progress.sentence_best_time_seconds,
        "sentence_total_time_seconds": progress.sentence_total_time_seconds,
        "stories_completed": progress.stories_completed,
        "stories_started": progress.stories_started or [],
        "story_quiz_attempts": progress.story_quiz_attempts,
        "story_quiz_correct": progress.story_quiz_correct,
        "story_microphone_attempts": progress.story_microphone_attempts,
        "story_microphone_success": progress.story_microphone_success,
        "last_story": progress.last_story,
        "last_story_level": progress.last_story_level,
        "story_mastery_percentage": progress.story_mastery_percentage,
        "story_best_reading_time": progress.story_best_reading_time,
        "story_needs_review": progress.story_needs_review or [],
        "pronoun_lessons_completed": progress.pronoun_lessons_completed,
        "pronouns_practiced": progress.pronouns_practiced or [],
        "pronouns_mastered": progress.pronouns_mastered or [],
        "pronoun_quiz_attempts": progress.pronoun_quiz_attempts,
        "pronoun_quiz_correct": progress.pronoun_quiz_correct,
        "pronoun_microphone_attempts": progress.pronoun_microphone_attempts,
        "pronoun_microphone_success": progress.pronoun_microphone_success,
        "last_pronoun": progress.last_pronoun,
        "last_pronoun_level": progress.last_pronoun_level,
        "pronoun_mastery_percentage": progress.pronoun_mastery_percentage,
        "pronouns_needs_review": progress.pronouns_needs_review or [],
        "sight_words_practiced": progress.sight_words_practiced or [],
        "sight_words_mastered": progress.sight_words_mastered or [],
        "sight_word_quiz_attempts": progress.sight_word_quiz_attempts,
        "sight_word_quiz_correct": progress.sight_word_quiz_correct,
        "fluency_sentences_read": progress.fluency_sentences_read,
        "fluency_attempts": progress.fluency_attempts,
        "best_wpm": progress.best_wpm,
        "best_reading_time": progress.best_reading_time,
        "fluency_accuracy": progress.fluency_accuracy,
        "fluency_score": progress.fluency_score,
        "question_words_mastered": progress.question_words_mastered or [],
        "conversations_completed": progress.conversations_completed,
        "action_verbs_mastered": progress.action_verbs_mastered or [],
        "adjectives_mastered": progress.adjectives_mastered or [],
        "last_fluency_sentence": progress.last_fluency_sentence,
        "last_sight_word": progress.last_sight_word,
        "last_conversation": progress.last_conversation,
        "fluency_mastery_percentage": progress.fluency_mastery_percentage,
        "quiz_attempts": progress.quiz_attempts,
        "quiz_correct": progress.quiz_correct,
        "mic_attempts": progress.mic_attempts,
        "mic_success": progress.mic_success,
        "last_word": progress.last_word,
        "last_family": progress.last_family,
        "last_level": progress.last_level,
        "cvc_mastery_percentage": progress.cvc_mastery_percentage,
        "needs_review_words": progress.needs_review_words or [],
    }


@require_GET
@ensure_csrf_cookie
def cvc_reading_view(request):
    blocked = require_feature(request, "cvc_words", UPGRADE_LEVEL_THREE_MESSAGE)
    if blocked:
        return blocked

    progress = None
    if request.user.is_authenticated:
        progress, _ = CVCReadingProgress.objects.get_or_create(user=request.user)

    return render(request, "phonics/cvc_reading.html", {
        "cvc_progress_json": json.dumps(serialize_cvc_reading_progress(progress), ensure_ascii=False),
        "cvc_words_total": CVCWord.objects.count(),
        "cvc_sentences_total": CVCSentence.objects.count(),
        "cvc_stories_total": CVCStory.objects.count(),
    })


@require_GET
def cvc_reading_worksheet(request):
    blocked = require_feature(request, "cvc_worksheets", UPGRADE_LEVEL_THREE_MESSAGE)
    if blocked:
        return blocked

    ensure_seed_data()
    words = list(CVCWord.objects.all().order_by("vowel_sound", "word_family", "order", "word")[:CVC_WORKSHEET_WORD_LIMIT])
    sentences = list(CVCSentence.objects.filter(category__in=["cvc", ""]).order_by("order", "difficulty")[:CVC_WORKSHEET_SENTENCE_LIMIT])
    stories = list(CVCStory.objects.all().order_by("order", "difficulty")[:CVC_WORKSHEET_STORY_LIMIT])
    groups = {}
    for word in words:
        groups.setdefault(word.vowel_sound or "mixed", []).append(word)

    return render(request, "phonics/cvc_worksheet.html", {
        "words": words,
        "sentences": sentences,
        "stories": stories,
        "word_groups": groups,
    })


def log_public_api_exception(request, message, exc):
    logger.exception(
        message,
        extra={
            "request_id": getattr(request, "request_id", ""),
            "method": getattr(request, "method", ""),
            "path": getattr(request, "path", ""),
            "status_code": 500,
            "duration_ms": 0,
        },
    )


def parse_pagination_params(request):
    def positive_int(name, default):
        raw = request.GET.get(name, default)
        try:
            value = int(raw)
        except (TypeError, ValueError):
            value = default
        return max(1, value)

    page = positive_int("page", 1)
    page_size = min(positive_int("page_size", CVC_API_DEFAULT_PAGE_SIZE), CVC_API_MAX_PAGE_SIZE)
    return page, page_size


def get_cached_cvc_content_count(kind, model, *, extra=0):
    cache_key = f"cvc-count:{CVC_CONTENT_CACHE_VERSION}:{kind}"
    cached = safe_cache_get(cache_key)
    if isinstance(cached, int) and cached >= 0:
        return max(cached + extra, 1)
    count = model.objects.count()
    safe_cache_set(cache_key, count, timeout=CVC_COUNT_CACHE_TIMEOUT)
    return max(count + extra, 1)


def paginate_queryset(qs, request, *, resource, serializer, legacy_key, cache_extra="", timeout=300):
    page, page_size = parse_pagination_params(request)
    include_legacy = str(request.GET.get("legacy", "1")).lower() not in {"0", "false", "no"}
    cache_key = (
        f"cvc-api:{CVC_CONTENT_CACHE_VERSION}:{resource}:"
        f"page:{page}:page_size:{page_size}:legacy:{int(include_legacy)}:filters:{cache_extra}"
    )
    cached = safe_cache_get(cache_key)
    if isinstance(cached, dict):
        return JsonResponse(cached)

    count = qs.count()
    total_pages = max(1, math.ceil(count / page_size)) if count else 1
    if page > total_pages:
        page = total_pages
    offset = (page - 1) * page_size
    results = [serializer(item) for item in qs[offset:offset + page_size]]
    payload = {
        "count": count,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "results": results,
    }
    if include_legacy:
        payload[legacy_key] = results
    safe_cache_set(cache_key, payload, timeout=timeout)
    return JsonResponse(payload)


def cvc_word_payload(w):
    return {
        "id": w.id,
        "word": getattr(w, "word", ""),
        "arabic_meaning": getattr(w, "arabic_meaning", "") or getattr(w, "meaning_ar", ""),
        "image_url": getattr(w, "image_url", "") or getattr(w, "image", ""),
        "emoji": getattr(w, "emoji", ""),
        "category": getattr(w, "category", ""),
        "word_family": getattr(w, "word_family", ""),
        "vowel_sound": getattr(w, "vowel_sound", ""),
        "difficulty_level": getattr(w, "difficulty_level", None) or getattr(w, "difficulty", None),
    }


def cvc_sentence_payload(s):
    return {
        "id": s.id,
        "sentence": getattr(s, "sentence", "") or getattr(s, "text", ""),
        "arabic_translation": getattr(s, "arabic_translation", "") or getattr(s, "translation_ar", ""),
        "difficulty": getattr(s, "difficulty", None),
        "time_limit": getattr(s, "time_limit", None),
        "category": getattr(s, "category", ""),
        "quiz_data": getattr(s, "quiz_data", None),
        "emoji": getattr(s, "emoji", ""),
    }


def cvc_story_payload(s, *, summary=False):
    payload = {
        "id": s.id,
        "title": getattr(s, "title", ""),
        "difficulty": getattr(s, "difficulty", None),
        "image_url": getattr(s, "image_url", "") or getattr(s, "image", ""),
    }
    content = getattr(s, "content", "") or getattr(s, "story", "")
    explanation = getattr(s, "arabic_explanation", "") or getattr(s, "explanation_ar", "")
    if summary:
        words = content.split()
        payload.update({
            "summary": " ".join(words[:24]),
            "word_count": len(words),
        })
    else:
        payload.update({
            "content": content,
            "arabic_explanation": explanation,
            "quiz_data": getattr(s, "quiz_data", None),
        })
    return payload


@require_GET
def get_cvc_words_api(request):
    blocked = require_feature(request, "cvc_words", UPGRADE_LEVEL_THREE_MESSAGE)
    if blocked:
        return blocked

    """
    Returns JSON words.
    IMPORTANT: Avoid `.only()` to prevent 500 if fields differ from expectations.
    """
    # Auto-seed if database is empty (Render Free tier solution)
    ensure_seed_data()

    try:
        qs = CVCWord.objects.all().order_by("order", "id")
        return paginate_queryset(qs, request, resource="words", serializer=cvc_word_payload, legacy_key="words")
    except Exception as e:
        log_public_api_exception(request, "failed_fetch_cvc_words", e)
        return _json_error("Failed to fetch CVC words", 500)


@require_GET
def get_cvc_sentences_api(request):
    blocked = require_feature(request, "cvc_sentences", UPGRADE_LEVEL_THREE_MESSAGE)
    if blocked:
        return blocked

    # Auto-seed if database is empty
    ensure_seed_data()

    try:
        qs = CVCSentence.objects.all().order_by("order", "id")
        return paginate_queryset(qs, request, resource="sentences", serializer=cvc_sentence_payload, legacy_key="sentences")
    except Exception as e:
        log_public_api_exception(request, "failed_fetch_cvc_sentences", e)
        return _json_error("Failed to fetch CVC sentences", 500)


@require_GET
def get_cvc_stories_api(request):
    blocked = require_feature(request, "cvc_stories", UPGRADE_LEVEL_THREE_MESSAGE)
    if blocked:
        return blocked

    # Auto-seed if database is empty
    ensure_seed_data()

    try:
        summary = str(request.GET.get("summary", "")).strip().lower() in {"1", "true", "yes"}
        qs = CVCStory.objects.all().order_by("order", "id")
        return paginate_queryset(
            qs,
            request,
            resource="stories",
            serializer=lambda story: cvc_story_payload(story, summary=summary),
            legacy_key="stories",
            cache_extra=f"summary:{int(summary)}",
        )
    except Exception as e:
        log_public_api_exception(request, "failed_fetch_cvc_stories", e)
        return _json_error("Failed to fetch CVC stories", 500)


@require_POST
@login_required
@rate_limit("legacy-cvc-progress", limit_setting="RATE_LIMIT_WRITE", default=60)
def save_cvc_progress_api(request):
    blocked = require_feature(request, "cvc_words", UPGRADE_LEVEL_THREE_MESSAGE)
    if blocked:
        return blocked

    return JsonResponse({
        "error": "legacy_endpoint_retired",
        "message": "Use the authenticated CVC reading progress endpoint.",
        "replacement": reverse("api_cvc_reading_progress"),
    }, status=410)


@require_http_methods(["GET", "POST"])
def cvc_reading_progress_api(request):
    blocked = require_feature(request, "cvc_words", UPGRADE_LEVEL_THREE_MESSAGE)
    if blocked:
        return blocked

    if not request.user.is_authenticated:
        return JsonResponse({
            "authenticated": False,
            "message": "local_only",
            "progress": serialize_cvc_reading_progress(None),
        })

    progress, _ = CVCReadingProgress.objects.get_or_create(user=request.user)

    if request.method == "GET":
        return JsonResponse({
            "authenticated": True,
            "progress": serialize_cvc_reading_progress(progress),
        })

    data, error = parse_json_safely(request)
    if error:
        return error

    event_type = str(data.get("event_type") or data.get("type") or "").strip()[:30]
    item_text = str(data.get("item_text") or data.get("word") or "").strip()[:80]
    level = str(data.get("level") or "").strip()[:40]
    family = str(data.get("family") or "").strip()[:40]
    lesson_id = str(data.get("lesson_id") or "").strip()[:80]
    sentence_level = str(data.get("sentence_level") or "").strip()[:40]
    story_level = str(data.get("story_level") or "").strip()[:60]
    pronoun_level = str(data.get("pronoun_level") or "").strip()[:80]
    fluency_level = str(data.get("fluency_level") or "").strip()[:80]
    score = int(data.get("score") or data.get("points") or 0)
    mastered = bool(data.get("mastered", score >= 70))

    words_practiced = list(progress.words_practiced or [])
    words_mastered = list(progress.words_mastered or [])
    needs_review = list(progress.needs_review_words or [])
    completed_levels = list(progress.completed_levels or [])
    completed_lessons = list(progress.completed_lessons or [])
    completed_families = list(progress.completed_families or [])
    is_new_lesson = bool(lesson_id and lesson_id not in completed_lessons)

    if item_text and event_type in {"word", "listen", "mic", "spelling", "quiz"}:
        if item_text not in words_practiced:
            words_practiced.append(item_text)
        if mastered:
            if item_text not in words_mastered:
                words_mastered.append(item_text)
            needs_review = [word for word in needs_review if word != item_text]
        elif event_type != "listen" and item_text not in needs_review:
            needs_review.append(item_text)

    if event_type == "sentence":
        progress.sentences_read = max(progress.sentences_read, int(data.get("sentences_read") or progress.sentences_read + 1))
    if event_type == "sentence_mastered":
        progress.sentences_read = max(progress.sentences_read, int(data.get("sentences_read") or progress.sentences_read + 1))
        sentences_mastered = list(progress.sentences_mastered or [])
        if item_text and item_text not in sentences_mastered:
            sentences_mastered.append(item_text)
        progress.sentences_mastered = sentences_mastered[:300]
    if event_type == "sentence_quiz":
        progress.sentence_quiz_attempts += 1
        if mastered:
            progress.sentence_quiz_correct += 1
    if event_type == "sentence_mic":
        progress.sentence_microphone_attempts += 1
        if mastered:
            progress.sentence_microphone_success += 1
    if event_type == "sentence_timer":
        try:
            reading_time = max(0, int(float(data.get("reading_time") or 0)))
        except (TypeError, ValueError):
            reading_time = 0
        if reading_time:
            progress.sentence_total_time_seconds += reading_time
            progress.sentence_best_time_seconds = min(
                progress.sentence_best_time_seconds or reading_time,
                reading_time,
            )
    if event_type == "story":
        progress.stories_completed = max(progress.stories_completed, int(data.get("stories_completed") or progress.stories_completed + 1))
    if event_type.startswith("story"):
        stories_started = list(progress.stories_started or [])
        story_needs_review = list(progress.story_needs_review or [])
        if item_text:
            progress.last_story = item_text[:160]
        progress.last_story_level = story_level or level or progress.last_story_level
        if event_type in {"story_started", "story_listen"} and item_text and item_text not in stories_started:
            stories_started.append(item_text)
        if event_type == "story_quiz":
            progress.story_quiz_attempts += 1
            if mastered:
                progress.story_quiz_correct += 1
            elif item_text and item_text not in story_needs_review:
                story_needs_review.append(item_text)
        if event_type == "story_mic":
            progress.story_microphone_attempts += 1
            if mastered:
                progress.story_microphone_success += 1
            elif item_text and item_text not in story_needs_review:
                story_needs_review.append(item_text)
        if event_type in {"story_timer", "story_complete"}:
            try:
                reading_time = max(0, int(float(data.get("reading_time") or data.get("time_spent") or 0)))
            except (TypeError, ValueError):
                reading_time = 0
            if reading_time:
                progress.story_best_reading_time = min(progress.story_best_reading_time or reading_time, reading_time)
        if event_type == "story_complete":
            progress.stories_completed = max(progress.stories_completed, int(data.get("stories_completed") or progress.stories_completed + 1))
            if item_text and item_text not in stories_started:
                stories_started.append(item_text)
            story_needs_review = [story for story in story_needs_review if story != item_text]
        progress.stories_started = stories_started[:120]
        progress.story_needs_review = story_needs_review[:60]
    if event_type.startswith("pronoun"):
        pronouns_practiced = list(progress.pronouns_practiced or [])
        pronouns_mastered = list(progress.pronouns_mastered or [])
        pronouns_needs_review = list(progress.pronouns_needs_review or [])
        if item_text:
            progress.last_pronoun = item_text[:80]
        progress.last_pronoun_level = pronoun_level or level or progress.last_pronoun_level
        if item_text and event_type in {"pronoun_practice", "pronoun_listen", "pronoun_mic", "pronoun_quiz", "pronoun_mastered"} and item_text not in pronouns_practiced:
            pronouns_practiced.append(item_text)
        if event_type == "pronoun_quiz":
            progress.pronoun_quiz_attempts += 1
            if mastered:
                progress.pronoun_quiz_correct += 1
            elif item_text and item_text not in pronouns_needs_review:
                pronouns_needs_review.append(item_text)
        if event_type == "pronoun_mic":
            progress.pronoun_microphone_attempts += 1
            if mastered:
                progress.pronoun_microphone_success += 1
            elif item_text and item_text not in pronouns_needs_review:
                pronouns_needs_review.append(item_text)
        if mastered and item_text:
            if item_text not in pronouns_mastered:
                pronouns_mastered.append(item_text)
            pronouns_needs_review = [item for item in pronouns_needs_review if item != item_text]
        elif event_type not in {"pronoun_listen", "pronoun_practice"} and item_text and item_text not in pronouns_needs_review:
            pronouns_needs_review.append(item_text)
        if event_type == "pronoun_mastered" and is_new_lesson:
            progress.pronoun_lessons_completed += 1
        progress.pronouns_practiced = pronouns_practiced[:160]
        progress.pronouns_mastered = pronouns_mastered[:160]
        progress.pronouns_needs_review = pronouns_needs_review[:80]
    if event_type.startswith("sight_word"):
        sight_words_practiced = list(progress.sight_words_practiced or [])
        sight_words_mastered = list(progress.sight_words_mastered or [])
        if item_text:
            progress.last_sight_word = item_text[:60]
            if item_text not in sight_words_practiced:
                sight_words_practiced.append(item_text)
        if event_type == "sight_word_quiz":
            progress.sight_word_quiz_attempts += 1
            if mastered:
                progress.sight_word_quiz_correct += 1
        if mastered and item_text and item_text not in sight_words_mastered:
            sight_words_mastered.append(item_text)
        progress.sight_words_practiced = sight_words_practiced[:120]
        progress.sight_words_mastered = sight_words_mastered[:120]
    if event_type.startswith("fluency"):
        if item_text:
            progress.last_fluency_sentence = item_text[:180]
        if event_type in {"fluency_attempt", "fluency_mic"}:
            progress.fluency_attempts += 1
        if event_type == "fluency_attempt":
            progress.fluency_sentences_read += 1
            try:
                reading_time = max(0, int(float(data.get("reading_time") or data.get("time_spent") or 0)))
            except (TypeError, ValueError):
                reading_time = 0
            try:
                wpm = max(0, int(float(data.get("wpm") or 0)))
            except (TypeError, ValueError):
                wpm = 0
            if reading_time:
                progress.best_reading_time = min(progress.best_reading_time or reading_time, reading_time)
            if wpm:
                progress.best_wpm = max(progress.best_wpm, wpm)
        if event_type == "fluency_mic":
            progress.fluency_accuracy = max(progress.fluency_accuracy, min(100, score))
        if score:
            progress.fluency_score = max(progress.fluency_score, min(100, score))
    if event_type == "question_word_mastered" and item_text:
        question_words_mastered = list(progress.question_words_mastered or [])
        if item_text not in question_words_mastered:
            question_words_mastered.append(item_text)
        progress.question_words_mastered = question_words_mastered[:30]
    if event_type == "conversation_complete":
        if item_text:
            progress.last_conversation = item_text[:120]
        progress.conversations_completed = max(progress.conversations_completed, int(data.get("conversations_completed") or progress.conversations_completed + 1))
    if event_type == "action_verb_mastered" and item_text:
        action_verbs_mastered = list(progress.action_verbs_mastered or [])
        if item_text not in action_verbs_mastered:
            action_verbs_mastered.append(item_text)
        progress.action_verbs_mastered = action_verbs_mastered[:60]
    if event_type == "adjective_mastered" and item_text:
        adjectives_mastered = list(progress.adjectives_mastered or [])
        if item_text not in adjectives_mastered:
            adjectives_mastered.append(item_text)
        progress.adjectives_mastered = adjectives_mastered[:60]
    if event_type in {"quiz", "spelling"}:
        progress.quiz_attempts += 1
        if mastered:
            progress.quiz_correct += 1
    if event_type == "mic":
        progress.mic_attempts += 1
        if mastered:
            progress.mic_success += 1

    if level and level not in completed_levels and mastered:
        completed_levels.append(level)
    if lesson_id and lesson_id not in completed_lessons and mastered:
        completed_lessons.append(lesson_id)
    if family and family not in completed_families and mastered:
        completed_families.append(family)

    total_words = get_cached_cvc_content_count("words", CVCWord)
    total_sentences = get_cached_cvc_content_count("sentences", CVCSentence, extra=99)
    if event_type.startswith("sentence"):
        progress.last_sentence = item_text[:160] or progress.last_sentence
        progress.last_sentence_level = sentence_level or level or progress.last_sentence_level
        if is_new_lesson and sentence_level == "common" and mastered:
            progress.common_sentences_completed += 1
        if is_new_lesson and sentence_level == "numbers" and mastered:
            progress.numbers_completed += 1
        if is_new_lesson and sentence_level == "days" and mastered:
            progress.days_completed += 1
        if is_new_lesson and sentence_level == "months" and mastered:
            progress.months_completed += 1
        progress.sentence_mastery_percentage = min(
            100,
            round((len(progress.sentences_mastered or []) / total_sentences) * 100),
        )
    total_stories = get_cached_cvc_content_count("stories", CVCStory, extra=9)
    if event_type.startswith("story"):
        progress.story_mastery_percentage = min(
            100,
            round((progress.stories_completed / total_stories) * 100),
        )
    total_pronoun_items = 35
    if event_type.startswith("pronoun"):
        progress.pronoun_mastery_percentage = min(
            100,
            round((len(progress.pronouns_mastered or []) / total_pronoun_items) * 100),
        )
    if (
        event_type.startswith("sight_word")
        or event_type.startswith("fluency")
        or event_type in {"question_word_mastered", "conversation_complete", "action_verb_mastered", "adjective_mastered"}
    ):
        total_fluency_items = 40 + 34 + 6 + 6 + 16 + 15
        completed_fluency_items = (
            len(progress.sight_words_mastered or [])
            + min(progress.fluency_sentences_read, 24)
            + len(progress.question_words_mastered or [])
            + min(progress.conversations_completed, 6)
            + len(progress.action_verbs_mastered or [])
            + len(progress.adjectives_mastered or [])
        )
        progress.fluency_mastery_percentage = min(
            100,
            round((completed_fluency_items / total_fluency_items) * 100),
        )
    progress.words_practiced = words_practiced[:300]
    progress.words_mastered = words_mastered[:300]
    progress.needs_review_words = needs_review[:50]
    progress.completed_levels = completed_levels[:20]
    progress.completed_lessons = completed_lessons[:80]
    progress.completed_families = completed_families[:60]
    progress.last_word = item_text or progress.last_word
    progress.last_family = family or progress.last_family
    progress.last_level = level or progress.last_level
    progress.cvc_mastery_percentage = max(
        progress.cvc_mastery_percentage,
        min(100, round((len(progress.words_mastered) / total_words) * 100)),
    )
    progress.last_payload = data
    progress.save()

    return JsonResponse({
        "status": "ok",
        "authenticated": True,
        "progress": serialize_cvc_reading_progress(progress),
    })


@csrf_exempt
@require_POST
@rate_limit("pronunciation", limit_setting="RATE_LIMIT_PUBLIC_API", default=30)
def check_cvc_pronunciation(request):
    blocked = require_feature(request, "cvc_words", UPGRADE_LEVEL_THREE_MESSAGE)
    if blocked:
        return blocked

    try:
        target_word = (request.POST.get("word") or "").strip().upper()
        if not target_word:
            return _json_error("Word parameter required", 400)

        return JsonResponse({
            "word": target_word,
            "accuracy": None,
            "correct": False,
            "message": "Current pronunciation practice relies on browser Web Speech text recognition. This endpoint does not perform real audio pronunciation analysis."
        })

        # mock response
        accuracy = 85
        return JsonResponse({
            "word": target_word,
            "accuracy": accuracy,
            "correct": True,
            "message": "ط±ط§ط¦ط¹! ظ†ط·ظ‚ ظ…ظ…طھط§ط²" if accuracy >= 80 else "ط¬ظٹط¯طŒ ط­ط§ظˆظ„ ظ…ط±ط© ط£ط®ط±ظ‰"
        })

    except Exception:
        logger.exception("pronunciation_check_failed request_id=%s", getattr(request, "request_id", ""))
        return _json_error("Pronunciation check failed", 500, request_id=getattr(request, "request_id", ""))
