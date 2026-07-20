from __future__ import annotations

from decimal import Decimal


PLAN_FREE = "free"
PLAN_BASIC = "basic"
PLAN_SILVER = "silver"
PLAN_VIP = "vip"
PLAN_DIAMOND = "diamond"
PLAN_FULL_ACCESS = "full_access"
PLAN_LEVEL_THREE = "level_3"
PLAN_LEVEL_FOUR = "level_4"

MAIN_PLAN_CODES = (PLAN_FREE, PLAN_BASIC, PLAN_SILVER, PLAN_VIP, PLAN_DIAMOND)
PAID_MAIN_PLAN_CODES = (PLAN_BASIC, PLAN_SILVER, PLAN_VIP, PLAN_DIAMOND)
ADDON_PLAN_CODES = (PLAN_LEVEL_THREE, PLAN_LEVEL_FOUR)

BASIC_FEATURE_KEYS = frozenset({
    "letters_full",
    "letter_sounds_basic",
    "internal_games",
    "student_progress",
    "basic_parent_report",
    "letter_certificate_basic",
})

SILVER_FEATURE_KEYS = BASIC_FEATURE_KEYS | {
    "sounds_basic",
    "sounds_full",
    "vowels",
    "digraphs",
    "ending_sounds",
    "trigraphs",
    "advanced_patterns_preview",
    "sounds_mic",
    "worksheets_level1",
    "worksheets_print_level1",
    "worksheets_download_level1",
    "sounds_worksheets",
}

VIP_FEATURE_KEYS = SILVER_FEATURE_KEYS | {
    "book_download_level1",
    "full_book_download",
    "wordwall_level1",
    "bird_tutor",
    "bird_tutor_trial",
    "bird_tutor_full",
    "bird_xp",
    "bird_error_review",
    "bird_parent_report",
    "parent_report_detailed",
    "smart_review_plan",
    "gold_certificate",
    "honor_board_consent",
    "leaderboard",
    "mistake_review",
    "improvement_report",
    "audio_question_reading",
    "step_by_step_error_review",
}

LEVEL_THREE_FEATURE_KEYS = frozenset({
    "cvc_words",
    "word_families",
    "cvc_sentences",
    "cvc_stories",
    "pronouns",
    "cvc_worksheets",
    "cvc_certificate",
})

LEVEL_FOUR_FEATURE_KEYS = frozenset({
    "level_four",
    "level_four_full",
    "level4_foundation",
})

FULL_ACCESS_ONLY_FEATURE_KEYS = LEVEL_THREE_FEATURE_KEYS | LEVEL_FOUR_FEATURE_KEYS | {
    "full_access",
}
FULL_ACCESS_FEATURE_KEYS = VIP_FEATURE_KEYS | FULL_ACCESS_ONLY_FEATURE_KEYS


PLAN_CATALOG = {
    PLAN_FREE: {
        "code": PLAN_FREE,
        "name": "Free",
        "category": "main",
        "rank": 0,
        "price": Decimal("0.00"),
        "duration_days": 0,
        "included_addons": (),
        "features": frozenset(),
    },
    PLAN_BASIC: {
        "code": PLAN_BASIC,
        "name": "Basic",
        "category": "main",
        "rank": 1,
        "price": Decimal("19.00"),
        "duration_days": 30,
        "included_addons": (),
        "features": BASIC_FEATURE_KEYS,
    },
    PLAN_SILVER: {
        "code": PLAN_SILVER,
        "name": "Silver",
        "category": "main",
        "rank": 2,
        "price": Decimal("27.00"),
        "duration_days": 30,
        "included_addons": (),
        "features": SILVER_FEATURE_KEYS,
    },
    PLAN_VIP: {
        "code": PLAN_VIP,
        "name": "VIP",
        "category": "main",
        "rank": 3,
        "price": Decimal("39.00"),
        "duration_days": 30,
        "included_addons": (),
        "features": VIP_FEATURE_KEYS,
    },
    PLAN_DIAMOND: {
        "code": PLAN_DIAMOND,
        "name": "Diamond",
        "category": "main",
        "rank": 4,
        "price": Decimal("50.00"),
        "duration_days": 30,
        "included_addons": (PLAN_LEVEL_THREE, PLAN_LEVEL_FOUR),
        "features": FULL_ACCESS_FEATURE_KEYS,
    },
    PLAN_LEVEL_THREE: {
        "code": PLAN_LEVEL_THREE,
        "name": "Level 3",
        "category": "addon",
        "rank": None,
        "price": Decimal("15.00"),
        "duration_days": 30,
        "included_addons": (),
        "features": LEVEL_THREE_FEATURE_KEYS,
    },
    PLAN_LEVEL_FOUR: {
        "code": PLAN_LEVEL_FOUR,
        "name": "Level 4",
        "category": "addon",
        "rank": None,
        "price": Decimal("15.00"),
        "duration_days": 30,
        "included_addons": (),
        "features": LEVEL_FOUR_FEATURE_KEYS,
    },
}

FEATURE_KEYS_BY_PLAN = {
    code: set(definition["features"])
    for code, definition in PLAN_CATALOG.items()
}
FEATURE_KEYS_BY_PLAN[PLAN_FULL_ACCESS] = set(FULL_ACCESS_FEATURE_KEYS)


def normalize_plan_code(value: str) -> str:
    return str(value or "").strip().lower().replace("-", "_")


def get_plan_definition(plan_code: str) -> dict:
    return PLAN_CATALOG.get(normalize_plan_code(plan_code))


def main_plan_rank(plan_code: str) -> int:
    plan = get_plan_definition(plan_code)
    if not plan or plan["category"] != "main":
        return -1
    return int(plan["rank"])
