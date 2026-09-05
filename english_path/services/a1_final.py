QUESTIONS = (
    {"id":"v1","skill":"vocabulary","prompt":"Choose the family word.","choices":("mother","hospital","breakfast"),"answer":"mother"},
    {"id":"v2","skill":"vocabulary","prompt":"You buy food at a ___.","choices":("supermarket","bedroom","school bag"),"answer":"supermarket"},
    {"id":"v3","skill":"vocabulary","prompt":"Which action happens with a book?","choices":("reading","cooking","swimming"),"answer":"reading"},
    {"id":"g1","skill":"grammar","prompt":"She ___ two brothers.","choices":("have","has","having"),"answer":"has"},
    {"id":"g2","skill":"grammar","prompt":"Omar ___ to school every day.","choices":("go","goes","going"),"answer":"goes"},
    {"id":"g3","skill":"grammar","prompt":"They ___ playing now.","choices":("is","are","was"),"answer":"are"},
    {"id":"r1","skill":"reading","prompt":"Maha wakes at six, then eats. What happens first?","choices":("wakes","eats","school"),"answer":"wakes"},
    {"id":"r2","skill":"reading","prompt":"The bank is opposite the park. What faces the park?","choices":("bank","hospital","school"),"answer":"bank"},
    {"id":"r3","skill":"reading","prompt":"Ali was tired, so he stayed home. Why did he stay?","choices":("He was tired.","It was school.","He can swim."),"answer":"He was tired."},
    {"id":"l1","skill":"listening","prompt":"Listen: I’d like rice and water. Choose the drink.","spoken":"I would like rice and water.","choices":("rice","water","bread"),"answer":"water"},
    {"id":"l2","skill":"listening","prompt":"Listen: Turn left at the bank. Where do you turn?","spoken":"Turn left at the bank.","choices":("bank","park","school"),"answer":"bank"},
    {"id":"l3","skill":"listening","prompt":"Listen: We went to the park yesterday. When?","spoken":"We went to the park yesterday.","choices":("yesterday","now","tomorrow"),"answer":"yesterday"},
)

RUBRICS = {
    "speaking": (
        "I introduced myself without reading every word.",
        "I answered two personal questions.",
        "I used understandable words and short sentences.",
        "I completed one role-play from start to finish.",
    ),
    "writing": (
        "I wrote at least five complete sentences.",
        "I used capital letters and full stops.",
        "I checked one grammar point from A1.",
        "Another person can understand my message.",
    ),
}


def public_questions():
    return tuple({key: value for key, value in item.items() if key != "answer"} for item in QUESTIONS)


def grade(answers, rubric_checks):
    totals = {skill: [0, 0] for skill in ("vocabulary", "grammar", "reading", "listening")}
    mistakes = []
    for item in QUESTIONS:
        selected = answers.get(item["id"], "")
        if selected and selected not in item["choices"]:
            raise ValueError("invalid answer")
        correct = selected == item["answer"]
        totals[item["skill"]][0] += int(correct)
        totals[item["skill"]][1] += 1
        if not correct:
            mistakes.append({"key": f"A1-FINAL-{item['id']}", "skill": item["skill"], "subskill": "a1-final", "difficulty": 3, "prompt": item["prompt"], "answer": item["answer"]})
    skills = {skill: round(got / count * 100) for skill, (got, count) in totals.items()}
    for skill in ("speaking", "writing"):
        checked = sum(str(index) in rubric_checks.get(skill, set()) for index in range(len(RUBRICS[skill])))
        skills[skill] = round(checked / len(RUBRICS[skill]) * 100)
    objective_score = round(sum(got for got, _ in totals.values()) / len(QUESTIONS) * 100)
    passed = objective_score >= 80 and all(skills[skill] >= 60 for skill in totals)
    weakest = min(skills, key=skills.get)
    return {"score": objective_score, "skills": skills, "passed": passed, "weakest": weakest, "mistakes": mistakes, "note": "Speaking and Writing are structured self-checks, not automatic proficiency measurements."}
