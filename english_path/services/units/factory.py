def vocab(word, arabic, example, example_ar, category="core", collocation="", word_family=""):
    return {"word": word, "arabic": arabic, "example": example, "example_ar": example_ar, "category": category, "collocation": collocation, "word_family": word_family, "audio": {"tts": True, "lang": "en-US"}}


def activity_question(prompt, choices, answer):
    return {"prompt": prompt, "choices": tuple(choices), "answer": answer}


A1_LISTENING_QUIZ_AUDIO = {
    "A1.3": {
        "l1": ("I have two pencils and one ruler.", "Listen, then choose the number of pencils.", "I have three books.", "Listen, then choose the number of books."),
        "l2": ("These are Adam’s keys.", "Listen, then choose who owns the keys.", "That is Lina’s bag.", "Listen, then choose who owns the bag."),
    },
    "A1.4": {
        "l1": ("School starts at seven thirty.", "Listen, then choose the school start time.", "I wake up at six fifteen.", "Listen, then choose the wake-up time."),
        "l2": ("I do homework, then I play.", "Listen, then choose what happens first.", "I eat, then I study.", "Listen, then choose what happens second."),
    },
    "A1.5": {
        "l1": ("Dad is talking on the phone.", "Listen, then choose what Dad is doing.", "Lina is reading.", "Listen, then choose what Lina is doing."),
        "l2": ("Mum is cooking and the baby is sleeping.", "Listen, then choose who is sleeping.", "Ali is running and Omar is sitting.", "Listen, then choose who is running."),
    },
    "A1.6": {
        "l1": ("I’d like chicken and salad.", "Listen, then choose the food order.", "I’d like rice and water.", "Listen, then choose the drink."),
        "l2": ("I don’t like juice.", "Listen, then choose the speaker’s preference.", "She likes apples.", "Listen, then choose her preference."),
    },
    "A1.7": {
        "l1": ("The desk is next to the window.", "Listen, then choose the desk’s location.", "The bag is under the chair.", "Listen, then choose the bag’s location."),
        "l2": ("There are two books.", "Listen, then choose the number of books.", "There is one sofa.", "Listen, then choose the number of sofas."),
    },
    "A1.8": {
        "l1": ("Turn right at the bank.", "Listen, then choose the direction.", "Turn left after the park.", "Listen, then choose the direction."),
        "l2": ("The hospital is opposite the supermarket.", "Listen, then choose what faces the supermarket.", "The café is next to the park.", "Listen, then choose what is beside the park."),
    },
    "A1.9": {
        "l1": ("I can swim, but I can’t cook.", "Listen, then choose what the speaker can do.", "She can draw but can’t sing.", "Listen, then choose what she can do."),
        "l2": ("Can you carry these bags?", "Listen, then choose the requested help.", "Can you open the window?", "Listen, then choose the requested action."),
    },
    "A1.10": {
        "l1": ("We watched a film.", "Listen, then choose what they watched.", "I played football.", "Listen, then choose what the speaker played."),
        "l2": ("I saw three cousins.", "Listen, then choose how many cousins.", "We visited two places.", "Listen, then choose how many places."),
    },
}

A1_MISSING_WORD_GAMES = {
    "A1.2": {"prompt": "She ___ a sister.", "choices": ("have", "has", "having"), "answer": "has"},
    "A1.3": {"prompt": "___ are my books.", "choices": ("This", "These", "That"), "answer": "These"},
    "A1.4": {"prompt": "Sara ___ to school every day.", "choices": ("go", "goes", "going"), "answer": "goes"},
    "A1.5": {"prompt": "They ___ playing outside.", "choices": ("is", "are", "am"), "answer": "are"},
    "A1.6": {"prompt": "We have ___ rice.", "choices": ("some", "any", "a"), "answer": "some"},
    "A1.7": {"prompt": "There ___ two windows.", "choices": ("is", "are", "am"), "answer": "are"},
    "A1.8": {"prompt": "Turn ___ at the bank.", "choices": ("left", "opposite", "between"), "answer": "left"},
    "A1.9": {"prompt": "She can ___ a bike.", "choices": ("rides", "ride", "riding"), "answer": "ride"},
    "A1.10": {"prompt": "They ___ happy yesterday.", "choices": ("was", "were", "are"), "answer": "were"},
}


def quiz_question(
    qid, skill, subskill, difficulty, prompt, choices, answer, reason, clue, similar,
    *, spoken="", similar_spoken="",
):
    choices = tuple(choices)
    question = {
        "id": qid, "skill": skill, "subskill": subskill, "difficulty": difficulty,
        "prompt": prompt, "choices": choices, "answer": answer,
        "explanation_ar": reason, "why_correct": reason, "clue": clue,
        "why_each_wrong": {choice: f"الخيار «{choice}» لا يطابق الدليل: {clue}" for choice in choices if choice != answer},
        "similar_question": {
            "prompt": similar[0], "choices": tuple(similar[1]),
            "answer": similar[2], "why": similar[3],
        },
    }
    if spoken:
        question["spoken"] = spoken
    if similar_spoken:
        question["similar_question"]["spoken"] = similar_spoken
    return question


def build_unit(*, code, title, arabic_title, theme, objectives, can_do, vocabulary, grammar, listening, speaking, reading, writing, mission, quiz, games=None, missing_word=None, review_from=(), arabic_support="clear"):
    level, order = code.split(".")
    missing_word_game = missing_word or A1_MISSING_WORD_GAMES.get(code) or {
        "prompt": "Choose a correct model sentence.",
        "choices": (grammar["examples"][0], grammar["examples"][1], "Not a complete sentence."),
        "answer": grammar["examples"][1],
    }
    quiz = tuple(quiz)
    for question in quiz:
        audio = A1_LISTENING_QUIZ_AUDIO.get(code, {}).get(question["id"])
        if audio:
            question["spoken"], question["prompt"] = audio[0], audio[1]
            question["similar_question"]["spoken"] = audio[2]
            question["similar_question"]["prompt"] = audio[3]
    return {
        "code": code, "level": level, "order": int(order), "title": title, "arabic_title": arabic_title,
        "theme": theme, "objectives": tuple(objectives), "can_do_statements": tuple(can_do), "review_from": tuple(review_from), "arabic_support": arabic_support,
        "vocabulary": tuple(vocabulary), "grammar": grammar, "listening": listening, "speaking": speaking,
        "reading": reading, "writing": writing,
        "games": tuple(games) if games else (
            {"id": "word-match", "type": "word_match", "title": "Word Match", "goal": "ربط مفردات الوحدة بمعانيها"},
            {"id": "sentence-builder", "type": "sentence_builder", "title": "Sentence Builder", "goal": grammar["examples"][0]},
            {"id": "missing-word", "type": "missing_word", "title": "Missing Word", "goal": grammar["examples"][1], **missing_word_game},
        ),
        "mission": mission, "quiz": quiz,
    }
