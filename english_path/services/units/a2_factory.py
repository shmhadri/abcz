from english_path.services.unit_schema import validate_unit
from english_path.services.units.factory import build_unit, quiz_question, vocab


def word(*values):
    return vocab(*values)


def question(qid, skill, subskill, difficulty, prompt, choices, answer, reason, clue, similar_prompt, similar_answer=None):
    return quiz_question(qid, skill, subskill, difficulty, prompt, tuple(choices), answer, reason, clue, (similar_prompt, tuple(choices), similar_answer or answer, reason))


def game(game_id, game_type, title, goal, prompt="", choices=(), answer=""):
    return {"id": game_id, "type": game_type, "title": title, "goal": goal, "prompt": prompt, "choices": tuple(choices), "answer": answer}


def unit(**values):
    return validate_unit(build_unit(**values))
