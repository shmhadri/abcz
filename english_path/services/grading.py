from english_path.services.unit_schema import SKILLS


def grade_quiz(unit, answers):
    if not isinstance(answers, dict):
        raise ValueError("answers must be an object")
    feedback = []
    totals = {skill: [0, 0] for skill in SKILLS}
    mistakes = []
    for question in unit["quiz"]:
        selected = answers.get(question["id"], "")
        if selected and selected not in question["choices"]:
            raise ValueError("invalid answer choice")
        correct = selected == question["answer"]
        if question.get("productive_score", True):
            totals[question["skill"]][0] += int(correct)
            totals[question["skill"]][1] += 1
        item = {"id": question["id"], "correct": correct, "selected": selected, "correct_answer": question["answer"], "why": question["why_correct"], "clue": question["clue"]}
        if not correct:
            item["why_wrong"] = question["why_each_wrong"].get(selected, "لم تختر إجابة. اقرأ الدليل ثم حاول مرة أخرى.")
            similar = question["similar_question"]
            item["similar"] = {"id": question["id"], "prompt": similar["prompt"], "choices": similar["choices"]}
            if similar.get("spoken"):
                item["similar"]["spoken"] = similar["spoken"]
            mistakes.append({"key": f"{unit['code']}-{question['id']}", "skill": question["skill"], "subskill": question["subskill"], "difficulty": question["difficulty"], "prompt": question["prompt"], "answer": question["answer"]})
        feedback.append(item)
    correct_count = sum(item["correct"] for item in feedback)
    score = round(correct_count / len(feedback) * 100)
    skills = {skill: round(got / count * 100) if count else 0 for skill, (got, count) in totals.items()}
    productive_practice = [skill for skill in ("speaking", "writing") if any(question["skill"] == skill and not question.get("productive_score", True) for question in unit["quiz"])]
    return {"score": score, "mastered": score >= 80, "skills": skills, "productive_practice": productive_practice, "feedback": feedback, "mistakes": mistakes}


def grade_similar(unit, question_id, selected):
    question = next((item for item in unit["quiz"] if item["id"] == question_id), None)
    if not question or selected not in question["similar_question"]["choices"]:
        raise ValueError("invalid similar question")
    similar = question["similar_question"]
    return {"correct": selected == similar["answer"], "correct_answer": similar["answer"], "explanation": similar["why"]}
