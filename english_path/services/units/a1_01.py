from copy import deepcopy

from english_path.services.a1_unit_1 import LESSON as LEGACY_LESSON, QUIZ as LEGACY_QUIZ
from english_path.services.unit_schema import validate_unit


def _question(item, number):
    similar = item["similar"]
    return {
        "id": item["id"], "skill": item["skill"], "subskill": "greetings" if item["skill"] == "vocabulary" else "be" if item["skill"] == "grammar" else "personal-information",
        "difficulty": min(4, 1 + number // 3), "prompt": item["prompt"], "choices": item["choices"], "answer": item["answer"],
        "explanation_ar": item["why"], "why_correct": item["why"], "clue": item["why"],
        "why_each_wrong": {choice: item["wrong"].get(choice, f"{choice} لا يحقق معنى الجملة.") for choice in item["choices"] if choice != item["answer"]},
        "similar_question": {"prompt": similar["prompt"], "choices": similar["choices"], "answer": similar["answer"], "why": similar["why"]},
        **({"spoken": item["spoken"]} if item.get("spoken") else {}),
    }


_lesson = deepcopy(LEGACY_LESSON)
UNIT = validate_unit({
    "code": "A1.1", "level": "A1", "order": 1, "title": "Hello!", "arabic_title": "مرحبًا!", "theme": "first-meeting",
    "objectives": _lesson["objectives"], "can_do_statements": _lesson["objectives"],
    "discover": _lesson["discover"],
    "vocabulary": tuple({**item, "example_ar": f"استخدم {item['word']} في لقاء أول.", "category": "greeting" if item["word"] in {"hello", "good morning", "welcome", "goodbye"} else "personal-information", "audio": {"tts": True, "lang": "en-US"}} for item in _lesson["vocabulary"]),
    "grammar": {
        **_lesson["grammar"], "explanation_en": "Use am with I, are with you/we/they, and is with he/she/it.", "explanation_ar": _lesson["grammar"]["rule_ar"],
        "examples": tuple(row[2] for row in _lesson["grammar"]["forms"]),
        "common_mistakes": ("I is Sara. → I am Sara.", "She are a student. → She is a student.", "You is welcome. → You are welcome."),
        "tips": ("Find the subject first.", "Use the short forms I’m, you’re, he’s and she’s in speaking."),
    },
    "listening": {**_lesson["listening"], "audio_text": " ".join(line for _, line in _lesson["listening"]["dialogue"]), "transcript": _lesson["listening"]["dialogue"], "hide_transcript_until_attempt": True},
    "speaking": {**_lesson["speaking"], "pronunciation_practice": ("I’m /aɪm/", "name /neɪm/", "meet /miːt/"), "prompts": ("Say your real name.", "Say your city or country.")},
    "reading": {**_lesson["reading"], "passage": _lesson["reading"]["text"], "arabic_support": "اضغط المساعدة فقط عند الحاجة: طالبة جديدة تعرّف بنفسها."},
    "writing": {**_lesson["writing"], "task": _lesson["writing"]["prompt"], "scaffold": _lesson["writing"]["frames"]},
    "games": (
        {**_lesson["games"][0], "type": "word_match"},
        {**_lesson["games"][1], "type": "sentence_builder"},
        {**_lesson["games"][2], "type": "missing_word", "prompt": "Choose the correct sentence.", "choices": ("I am Sara.", "I is Sara.", "I are Sara."), "answer": "I am Sara."},
    ), "mission": {**_lesson["mission"], "real_world_task": _lesson["mission"]["brief"], "success_criteria": (_lesson["mission"]["success"],)},
    "quiz": tuple(_question(item, index) for index, item in enumerate(LEGACY_QUIZ, 1)),
})
