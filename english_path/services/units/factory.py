def vocab(word, arabic, example, example_ar, category="core", collocation="", word_family=""):
    return {"word": word, "arabic": arabic, "example": example, "example_ar": example_ar, "category": category, "collocation": collocation, "word_family": word_family, "audio": {"tts": True, "lang": "en-US"}}


def activity_question(prompt, choices, answer):
    return {"prompt": prompt, "choices": tuple(choices), "answer": answer}


def quiz_question(qid, skill, subskill, difficulty, prompt, choices, answer, reason, clue, similar):
    choices = tuple(choices)
    return {
        "id": qid, "skill": skill, "subskill": subskill, "difficulty": difficulty,
        "prompt": prompt, "choices": choices, "answer": answer,
        "explanation_ar": reason, "why_correct": reason, "clue": clue,
        "why_each_wrong": {choice: f"الخيار «{choice}» لا يطابق الدليل: {clue}" for choice in choices if choice != answer},
        "similar_question": {"prompt": similar[0], "choices": tuple(similar[1]), "answer": similar[2], "why": similar[3]},
    }


def build_unit(*, code, title, arabic_title, theme, objectives, can_do, vocabulary, grammar, listening, speaking, reading, writing, mission, quiz, games=None, review_from=(), arabic_support="clear"):
    level, order = code.split(".")
    return {
        "code": code, "level": level, "order": int(order), "title": title, "arabic_title": arabic_title,
        "theme": theme, "objectives": tuple(objectives), "can_do_statements": tuple(can_do), "review_from": tuple(review_from), "arabic_support": arabic_support,
        "vocabulary": tuple(vocabulary), "grammar": grammar, "listening": listening, "speaking": speaking,
        "reading": reading, "writing": writing,
        "games": tuple(games) if games else (
            {"id": "word-match", "type": "word_match", "title": "Word Match", "goal": "ربط مفردات الوحدة بمعانيها"},
            {"id": "sentence-builder", "type": "sentence_builder", "title": "Sentence Builder", "goal": grammar["examples"][0]},
            {"id": "missing-word", "type": "missing_word", "title": "Missing Word", "goal": grammar["examples"][1], "prompt": "Choose a correct model sentence.", "choices": (grammar["examples"][0], grammar["examples"][1], "Not a complete sentence."), "answer": grammar["examples"][1]},
        ),
        "mission": mission, "quiz": tuple(quiz),
    }
