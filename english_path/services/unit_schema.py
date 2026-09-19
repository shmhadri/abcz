from copy import deepcopy

SKILLS = ("vocabulary", "grammar", "reading", "listening", "speaking", "writing")
REQUIRED_SECTIONS = ("vocabulary", "grammar", "listening", "speaking", "reading", "writing", "games", "mission", "quiz")
REQUIRED_UNIT_FIELDS = ("code", "level", "order", "title", "arabic_title", "theme", "objectives", "can_do_statements")


class UnitSchemaError(ValueError):
    pass


def validate_unit(source):
    """Validate authored curriculum at import time and return a defensive copy."""
    unit = deepcopy(source)
    missing = [name for name in (*REQUIRED_UNIT_FIELDS, *REQUIRED_SECTIONS) if not unit.get(name)]
    if missing:
        raise UnitSchemaError(f"{unit.get('code', 'unknown')}: missing {', '.join(missing)}")
    expected = f"{unit['level']}.{unit['order']}"
    if unit["code"] != expected or unit["level"] not in {"A1", "A2"}:
        raise UnitSchemaError(f"{unit['code']}: invalid code/level/order")
    vocabulary_range = range(8, 13) if unit["level"] == "A1" else range(10, 16)
    if len(unit["vocabulary"]) not in vocabulary_range:
        raise UnitSchemaError(f"{unit['code']}: invalid vocabulary size for {unit['level']}")
    for item in unit["vocabulary"]:
        required = {"word", "arabic", "example", "example_ar", "category"}
        if not required.issubset(item):
            raise UnitSchemaError(f"{unit['code']}: incomplete vocabulary item")
    grammar = unit["grammar"]
    for field in ("title", "explanation_en", "explanation_ar", "examples", "common_mistakes", "tips"):
        if not grammar.get(field):
            raise UnitSchemaError(f"{unit['code']}: grammar.{field} is required")
    if len(grammar["examples"]) < 3 or len(grammar["common_mistakes"]) < 3:
        raise UnitSchemaError(f"{unit['code']}: grammar needs 3 examples and 3 common mistakes")
    if len(unit["listening"].get("questions", ())) < 3 or not unit["listening"].get("transcript"):
        raise UnitSchemaError(f"{unit['code']}: incomplete listening activity")
    if len(unit["speaking"].get("shadowing", ())) < 3 or not unit["speaking"].get("role_play"):
        raise UnitSchemaError(f"{unit['code']}: incomplete speaking activity")
    if len(unit["reading"].get("questions", ())) < 3 or not unit["reading"].get("passage"):
        raise UnitSchemaError(f"{unit['code']}: incomplete reading activity")
    if len(unit["games"]) < 3 or len(unit["quiz"]) != 10:
        raise UnitSchemaError(f"{unit['code']}: exactly 10 quiz questions and at least 3 games are required")
    for game in unit["games"]:
        if game.get("type") != "missing_word":
            continue
        choices = tuple(game.get("choices", ()))
        if "___" not in game.get("prompt", "") or len(choices) != len(set(choices)) or choices.count(game.get("answer")) != 1:
            raise UnitSchemaError(f"{unit['code']}: missing word needs one unambiguous answer")
    question_ids = set()
    quiz_skills = set()
    for question in unit["quiz"]:
        required = {"id", "prompt", "choices", "answer", "skill", "subskill", "difficulty", "explanation_ar", "why_correct", "why_each_wrong", "clue", "similar_question"}
        if not required.issubset(question):
            raise UnitSchemaError(f"{unit['code']}: incomplete quiz question")
        if question["id"] in question_ids or question["answer"] not in question["choices"]:
            raise UnitSchemaError(f"{unit['code']}: invalid quiz id or answer")
        if question["skill"] not in SKILLS or question["difficulty"] not in range(1, 6):
            raise UnitSchemaError(f"{unit['code']}: invalid skill or difficulty")
        wrong_choices = set(question["choices"]) - {question["answer"]}
        if set(question["why_each_wrong"]) != wrong_choices:
            raise UnitSchemaError(f"{unit['code']}: every distractor needs an explanation")
        similar = question["similar_question"]
        if similar.get("answer") not in similar.get("choices", ()):
            raise UnitSchemaError(f"{unit['code']}: invalid similar question")
        if unit["level"] == "A1" and question["skill"] == "listening":
            if not question.get("spoken") or not similar.get("spoken"):
                raise UnitSchemaError(f"{unit['code']}: listening quiz audio is required")
        question_ids.add(question["id"])
        quiz_skills.add(question["skill"])
    if len(quiz_skills) < 4:
        raise UnitSchemaError(f"{unit['code']}: quiz must assess at least four skills")
    if unit.get("phase3_version"):
        if unit["level"] != "A1":
            raise UnitSchemaError(f"{unit['code']}: phase 3 enrichment is A1-only")
        if not 3 <= len(unit["can_do_statements"]) <= 4 or any(not goal.startswith("I can ") for goal in unit["can_do_statements"]):
            raise UnitSchemaError(f"{unit['code']}: phase 3 needs 3-4 consistent Can-Do goals")
        if len(unit.get("useful_expressions", ())) < 3 or any(not {"expression", "arabic", "example"}.issubset(item) for item in unit.get("useful_expressions", ())):
            raise UnitSchemaError(f"{unit['code']}: useful expressions are incomplete")
        if any(item.get("group") != "core" for item in unit["vocabulary"]):
            raise UnitSchemaError(f"{unit['code']}: core vocabulary grouping is required")
        if any(item.get("audio", {}).get("lang") != "en-GB" for item in unit["vocabulary"]):
            raise UnitSchemaError(f"{unit['code']}: British English vocabulary audio metadata is required")
        vocabulary_words = [item["word"].strip().casefold() for item in unit["vocabulary"]]
        if len(vocabulary_words) != len(set(vocabulary_words)):
            raise UnitSchemaError(f"{unit['code']}: duplicate core vocabulary")
        expected_earlier = {f"A1.{number}" for number in range(1, unit["order"])}
        if not set(unit.get("review_from", ())).issubset(expected_earlier):
            raise UnitSchemaError(f"{unit['code']}: spiral review must only reference earlier A1 units")
        review_items = unit.get("spiral_review", {}).get("items", ())
        if unit["order"] > 1 and (not unit.get("review_from") or len(review_items) != 2):
            raise UnitSchemaError(f"{unit['code']}: phase 3 needs a focused 80/20 spiral review")
        for item in review_items:
            choices = tuple(item.get("choices", ()))
            if len(choices) != len(set(choices)) or choices.count(item.get("answer")) != 1:
                raise UnitSchemaError(f"{unit['code']}: invalid spiral review answer")
        practice = unit["grammar"].get("practice", ())
        required_stages = {"Choose", "Complete", "Build sentence", "Correct mistake", "Use it in context"}
        if {item.get("stage") for item in practice} != required_stages:
            raise UnitSchemaError(f"{unit['code']}: incomplete grammar practice sequence")
        if len(unit["listening"].get("stages", ())) != 3 or not unit["listening"].get("gist_question"):
            raise UnitSchemaError(f"{unit['code']}: three-stage listening is required")
        gist = unit["listening"]["gist_question"]
        if tuple(gist.get("choices", ())).count(gist.get("answer")) != 1:
            raise UnitSchemaError(f"{unit['code']}: invalid listening gist answer")
        for activity in (*unit["listening"]["questions"], *unit["reading"]["questions"]):
            choices = tuple(activity.get("choices", ()))
            if len(choices) != len(set(choices)) or choices.count(activity.get("answer")) != 1:
                raise UnitSchemaError(f"{unit['code']}: lesson activity must have one unique answer")
        speaking = unit["speaking"]
        if not speaking.get("answer_question") or not speaking.get("mini_challenge") or len(speaking.get("rubric", ())) != 4 or not speaking.get("pronunciation_focus"):
            raise UnitSchemaError(f"{unit['code']}: productive speaking sequence is incomplete")
        allowed_reading_types = {"True / False", "Choose", "Match", "Who?", "Which?", "Where?", "What?", "When?", "Why?", "How?", "How many?", "Whose?", "Sequence", "Find information"}
        if any(item.get("question_type") not in allowed_reading_types for item in unit["reading"]["questions"]):
            raise UnitSchemaError(f"{unit['code']}: reading question type is missing")
        writing = unit["writing"]
        if not writing.get("guided") or not writing.get("semi_guided") or not writing.get("independent") or not writing.get("productive_practice"):
            raise UnitSchemaError(f"{unit['code']}: three-stage writing is incomplete")
        for game in unit["games"]:
            if game.get("choices"):
                choices = tuple(game["choices"])
                if len(choices) != len(set(choices)) or choices.count(game.get("answer")) != 1:
                    raise UnitSchemaError(f"{unit['code']}: game must have one unique answer")
        if any(question.get("productive_score") is not (question["skill"] not in {"speaking", "writing"}) for question in unit["quiz"]):
            raise UnitSchemaError(f"{unit['code']}: productive practice cannot receive an automatic skill score")
        if unit["code"] == "A1.10" and not unit["grammar"].get("functional_chunks"):
            raise UnitSchemaError("A1.10: did-question chunks must be taught before use")
    if unit["level"] == "A2":
        for field in ("review_from", "arabic_support"):
            if not unit.get(field):
                raise UnitSchemaError(f"{unit['code']}: {field} is required for A2")
        if not unit["speaking"].get("guided") or not unit["speaking"].get("independent"):
            raise UnitSchemaError(f"{unit['code']}: guided and independent speaking are required")
        if not unit["listening"].get("pre_listening"):
            raise UnitSchemaError(f"{unit['code']}: pre-listening is required")
        if not unit["writing"].get("useful_phrases") or not unit["writing"].get("optional_challenge"):
            raise UnitSchemaError(f"{unit['code']}: expanded writing support is required")
        difficulties = [question["difficulty"] for question in unit["quiz"]]
        if unit["order"] <= 3 and sum(value in (2, 3) for value in difficulties) < 7:
            raise UnitSchemaError(f"{unit['code']}: early A2 should mostly use difficulty 2-3")
        if unit["order"] >= 8 and sum(value in (3, 4) for value in difficulties) < 7:
            raise UnitSchemaError(f"{unit['code']}: late A2 should mostly use difficulty 3-4")
    return unit


def public_unit(unit):
    """Remove all answer keys before curriculum data reaches a template."""
    result = deepcopy(unit)
    for question in result["quiz"]:
        for secret in ("answer", "explanation_ar", "why_correct", "why_each_wrong", "clue", "similar_question"):
            question.pop(secret, None)
    for section in ("discover",):
        if isinstance(result.get(section), dict):
            result[section].pop("answer", None)
    return result
