QUESTIONS = (
    {"id":"v1","skill":"vocabulary","source_units":("A1.2",),"prompt":"Choose the family word.","choices":("mother","hospital","breakfast"),"answer":"mother"},
    {"id":"v2","skill":"vocabulary","source_units":("A1.13",),"prompt":"Which word describes weather with a lot of wind?","choices":("windy","cheap","friendly"),"answer":"windy"},
    {"id":"v3","skill":"vocabulary","source_units":("A1.17",),"prompt":"Which person prepares food in a restaurant?","choices":("chef","driver","teacher"),"answer":"chef"},
    {"id":"g1","skill":"grammar","source_units":("A1.4",),"prompt":"Omar ___ to school every day.","choices":("go","goes","going"),"answer":"goes"},
    {"id":"g2","skill":"grammar","source_units":("A1.11",),"prompt":"The English class is ___ Monday.","choices":("on","in","at"),"answer":"on"},
    {"id":"g3","skill":"grammar","source_units":("A1.16",),"prompt":"She ___ got a science project.","choices":("has","have","is"),"answer":"has"},
    {"id":"r1","skill":"reading","source_units":("A1.8",),"prompt":"The bank is opposite the park. What faces the park?","choices":("bank","hospital","school"),"answer":"bank"},
    {"id":"r2","skill":"reading","source_units":("A1.12","A1.15"),"prompt":"Shop notice: Green jackets are 60 riyals. Blue shirts are 25 riyals. Which item costs 60 riyals?","choices":("green jacket","blue shirt","both items"),"answer":"green jacket"},
    {"id":"r3","skill":"reading","source_units":("A1.11","A1.20"),"prompt":"Community Day is on Saturday. Registration opens at 9:30 and art starts at 10:00. What happens first?","choices":("registration","art","lunch"),"answer":"registration"},
    {"id":"l1","skill":"listening","source_units":("A1.6",),"prompt":"Listen and choose the drink.","spoken":"I would like rice and water, please.","choices":("rice","water","bread"),"answer":"water"},
    {"id":"l2","skill":"listening","source_units":("A1.12","A1.13"),"prompt":"Listen and choose what Maya should take.","spoken":"It is cold and windy. Maya should take her green jacket.","choices":("green jacket","red hat","blue shoes"),"answer":"green jacket"},
    {"id":"l3","skill":"listening","source_units":("A1.19",),"prompt":"Listen and choose the appointment time.","spoken":"Your appointment is on Tuesday at two o’clock.","choices":("Tuesday at 2:00","Thursday at 2:00","Tuesday at 3:00"),"answer":"Tuesday at 2:00"},
)

RUBRICS = {
    "speaking": (
        "I completed the task: introduce myself, choose an activity and ask one practical question.",
        "I answered two personal or everyday questions without reading every word.",
        "I used understandable A1 words and short sentences.",
        "I completed the role-play from greeting to a polite close.",
    ),
    "writing": (
        "I completed the task: write a five-sentence plan with a day, time, activity and practical detail.",
        "I used capital letters and full stops.",
        "I checked at least two grammar points from A1.",
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
