from __future__ import annotations

import json
import random
from dataclasses import dataclass
from typing import Any


SCENARIO_WEIGHTS = {
    "visitor": 30,
    "silver": 30,
    "level3": 15,
    "level4": 15,
    "diamond": 10,
}


@dataclass(frozen=True)
class ScenarioStep:
    method: str
    path: str
    name: str


VISITOR_PAGES = [
    ScenarioStep("GET", "/", "visitor:index"),
    ScenarioStep("GET", "/pricing/", "visitor:pricing"),
    ScenarioStep("GET", "/levels/", "visitor:levels"),
    ScenarioStep("GET", "/about/", "visitor:about"),
    ScenarioStep("GET", "/privacy/", "visitor:privacy"),
]

SILVER_PAGES = [
    ScenarioStep("GET", "/", "silver:index"),
    ScenarioStep("GET", "/sounds/", "silver:sounds"),
    ScenarioStep("GET", "/sounds/worksheet/", "silver:sounds_worksheet"),
    ScenarioStep("GET", "/letters/worksheet/", "silver:letters_worksheet"),
    ScenarioStep("GET", "/api/sounds/progress/", "silver:sounds_progress_get"),
]

LEVEL3_PAGES = [
    ScenarioStep("GET", "/", "level3:index"),
    ScenarioStep("GET", "/cvc-reading/", "level3:cvc_reading"),
    ScenarioStep("GET", "/api/cvc-progress/", "level3:cvc_progress_get"),
]

LEVEL4_PAGES = [
    ScenarioStep("GET", "/", "level4:index"),
    ScenarioStep("GET", "/level-four/", "level4:level_four"),
    ScenarioStep("GET", "/english-foundation/", "level4:english_foundation"),
    ScenarioStep("GET", "/vocabulary-foundation/", "level4:vocabulary"),
    ScenarioStep("GET", "/grammar-foundation/", "level4:grammar"),
]

DIAMOND_PAGES = [
    ScenarioStep("GET", "/", "diamond:index"),
    ScenarioStep("GET", "/profile/", "diamond:profile"),
    ScenarioStep("GET", "/sounds/", "diamond:sounds"),
    ScenarioStep("GET", "/cvc-reading/", "diamond:cvc_reading"),
    ScenarioStep("GET", "/level-four/", "diamond:level_four"),
]


def csrf_token_from_client(client: Any) -> str:
    token = client.cookies.get("csrftoken")
    return getattr(token, "value", token) or ""


def json_headers(client: Any) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    csrf_token = csrf_token_from_client(client)
    if csrf_token:
        headers["X-CSRFToken"] = csrf_token
    return headers


def login(client: Any, username: str, password: str) -> None:
    client.get("/accounts/login/", name="auth:login_form")
    client.post(
        "/accounts/login/",
        data={
            "username": username,
            "password": password,
            "csrfmiddlewaretoken": csrf_token_from_client(client),
        },
        name="auth:login_submit",
        allow_redirects=False,
    )


def run_steps(client: Any, steps: list[ScenarioStep]) -> None:
    for step in steps:
        if step.method == "GET":
            client.get(step.path, name=step.name)
        else:
            raise ValueError(f"Unsupported load-test method: {step.method}")


def post_sounds_progress(client: Any) -> None:
    payload = {
        "completed_items": ["digraph:sh", "ending:ck"],
        "quiz_attempts": random.randint(1, 6),
        "quiz_correct": random.randint(1, 5),
        "mic_attempts": random.randint(1, 3),
        "mic_success": random.randint(0, 3),
        "worksheet_downloads": random.randint(0, 2),
        "last_item": random.choice(["sh", "ch", "ck", "air"]),
        "practiced_vowels": ["A", "E"],
        "vowel_lessons_completed": random.randint(1, 4),
        "vowel_quiz_attempts": random.randint(1, 4),
        "vowel_quiz_correct": random.randint(1, 4),
        "vowel_microphone_attempts": random.randint(1, 3),
        "vowel_microphone_success": random.randint(0, 3),
        "last_vowel_practiced": random.choice(["A", "E", "I"]),
        "vowel_mastery_percentage": random.randint(10, 80),
    }
    client.post(
        "/api/sounds/progress/",
        data=json.dumps(payload),
        headers=json_headers(client),
        name="silver:sounds_progress_post",
    )


def post_cvc_progress(client: Any) -> None:
    payload = {
        "event_type": random.choice(["word", "quiz", "mic", "sentence_quiz"]),
        "item_text": random.choice(["cat", "map", "sun", "The cat sat."]),
        "level": "load-test",
        "family": random.choice(["at", "ap", "un"]),
        "lesson_id": "load-test-cvc",
        "score": random.randint(60, 100),
        "mastered": True,
    }
    client.post(
        "/api/cvc-progress/",
        data=json.dumps(payload),
        headers=json_headers(client),
        name="level3:cvc_progress_post",
    )


def post_english_foundation_progress(client: Any) -> None:
    payload = {
        "section": random.choice(["vocabulary", "grammar", "conversations", "common_sentences"]),
        "activity_type": random.choice(["open", "exercise", "game"]),
        "points": random.randint(1, 10),
    }
    client.post(
        "/api/english-foundation/progress/",
        data=json.dumps(payload),
        headers=json_headers(client),
        name="level4:english_progress_post",
    )
