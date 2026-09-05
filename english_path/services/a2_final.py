"""Server-owned A2 final challenge assembled from the authored A2 bank."""

from english_path.services.units import all_a2_units

OBJECTIVE_SKILLS = ("vocabulary", "grammar", "reading", "listening")
RUBRICS = {
    "speaking": (
        "I completed a real-life role-play without reading a full script.",
        "I connected at least four ideas and answered a follow-up question.",
        "My word stress and pace made the message understandable.",
        "I repaired the conversation when information changed.",
    ),
    "writing": (
        "I wrote 80–120 words that fully address the task.",
        "I connected ideas with clear sequence, reason, or contrast words.",
        "I used past, present, or future forms to match my meaning.",
        "I checked spelling, punctuation, and paragraph organisation.",
    ),
}
TASKS = {
    "speaking": "Resolve a booking problem, explain one past event, and agree on a future solution.",
    "writing": "Write an 80–120 word message explaining a changed plan and proposing a practical solution.",
}


def _bank():
    selected = {skill: [] for skill in OBJECTIVE_SKILLS}
    for unit in all_a2_units():
        for item in unit["quiz"]:
            skill = item["skill"]
            if skill in selected and len(selected[skill]) < 6:
                copy = dict(item)
                copy["id"] = f"{unit['code'].replace('.', '-')}-{item['id']}"
                copy["unit_code"] = unit["code"]
                selected[skill].append(copy)
    return tuple(item for skill in OBJECTIVE_SKILLS for item in selected[skill])


QUESTIONS = _bank()
if len(QUESTIONS) != 24:
    raise RuntimeError("A2 Final must contain exactly 24 balanced objective questions")


def public_questions():
    hidden = {"answer", "explanation_ar", "why_correct", "why_each_wrong", "clue", "similar_question"}
    return tuple({key: value for key, value in item.items() if key not in hidden} for item in QUESTIONS)


def grade(answers, rubric_checks):
    totals = {skill: [0, 0] for skill in OBJECTIVE_SKILLS}
    mistakes = []
    for item in QUESTIONS:
        selected = answers.get(item["id"], "")
        if selected and selected not in item["choices"]:
            raise ValueError("invalid answer")
        correct = selected == item["answer"]
        totals[item["skill"]][0] += int(correct)
        totals[item["skill"]][1] += 1
        if not correct:
            mistakes.append({"key": f"A2-FINAL-{item['id']}", "skill": item["skill"], "subskill": item["subskill"], "difficulty": item["difficulty"], "prompt": item["prompt"], "answer": item["answer"]})
    skills = {skill: round(got / count * 100) for skill, (got, count) in totals.items()}
    for skill, rubric in RUBRICS.items():
        checked = sum(str(index) in rubric_checks.get(skill, set()) for index in range(len(rubric)))
        skills[skill] = round(checked / len(rubric) * 100)
    score = round(sum(got for got, _ in totals.values()) / len(QUESTIONS) * 100)
    passed = score >= 80 and all(skills[skill] >= 60 for skill in OBJECTIVE_SKILLS)
    ordered = sorted(skills, key=skills.get, reverse=True)
    return {
        "score": score, "skills": skills, "passed": passed,
        "strong": [skill for skill in ordered if skills[skill] >= 80],
        "developing": [skill for skill in ordered if 60 <= skills[skill] < 80],
        "needs_review": [skill for skill in ordered if skills[skill] < 60],
        "mistakes": mistakes,
        "note": "Speaking and Writing use transparent self-check rubrics; they are not automatic proficiency measurements.",
    }
