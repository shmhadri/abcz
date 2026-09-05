"""Canonical, fully-authored lesson used as the quality bar for later units."""

LESSON = {
    "code": "A1.1",
    "title": "Hello!",
    "subtitle": "Meet Sara and learn how to introduce yourself",
    "duration": 35,
    "objectives": (
        "Greet someone at different times of day",
        "Say your name, age and country",
        "Use I am, you are, he is and she is",
        "Ask and answer simple personal questions",
        "Write a four-sentence introduction",
    ),
    "discover": {
        "scene": "Sara arrives at a new English club. Adam welcomes her for the first time.",
        "question": "What will Sara say first?",
        "choices": ("Goodbye!", "Hello!", "Good night!"),
        "answer": "Hello!",
        "explanation": "Hello is a greeting. Sara is meeting Adam, so she greets him first.",
    },
    "vocabulary": (
        {"word": "hello", "arabic": "مرحبًا", "example": "Hello, I’m Sara."},
        {"word": "good morning", "arabic": "صباح الخير", "example": "Good morning, Mr Ali."},
        {"word": "name", "arabic": "اسم", "example": "My name is Omar."},
        {"word": "meet", "arabic": "يقابل", "example": "Nice to meet you."},
        {"word": "from", "arabic": "من", "example": "I’m from Saudi Arabia."},
        {"word": "country", "arabic": "دولة", "example": "What is your country?"},
        {"word": "student", "arabic": "طالب", "example": "I’m a student."},
        {"word": "friend", "arabic": "صديق", "example": "Adam is my friend."},
        {"word": "welcome", "arabic": "أهلًا بك", "example": "Welcome to our class!"},
        {"word": "goodbye", "arabic": "مع السلامة", "example": "Goodbye! See you tomorrow."},
    ),
    "grammar": {
        "title": "Subject pronouns + be",
        "rule_ar": "نستخدم am مع I، وare مع you/we/they، وis مع he/she/it.",
        "forms": (
            ("I", "am", "I am Sara."),
            ("You / We / They", "are", "You are welcome."),
            ("He / She / It", "is", "She is a student."),
        ),
        "question_forms": (
            ("What’s your name?", "My name is Sara."),
            ("Where are you from?", "I’m from Saudi Arabia."),
            ("How old are you?", "I’m twelve years old."),
        ),
        "micro_check": {
            "prompt": "She ___ a new student.",
            "choices": ("am", "is", "are"),
            "answer": "is",
            "explanation": "She takes is: She is a new student.",
        },
    },
    "listening": {
        "dialogue": (
            ("Adam", "Hello! My name is Adam. What’s your name?"),
            ("Sara", "Hi, Adam. I’m Sara. Nice to meet you."),
            ("Adam", "Nice to meet you too. Where are you from?"),
            ("Sara", "I’m from Saudi Arabia. I’m twelve years old."),
            ("Adam", "Welcome to the English club, Sara!"),
        ),
        "questions": (
            {"prompt": "What is the girl’s name?", "choices": ("Lina", "Sara", "Maya"), "answer": "Sara"},
            {"prompt": "Where is Sara from?", "choices": ("Saudi Arabia", "Egypt", "Jordan"), "answer": "Saudi Arabia"},
            {"prompt": "How old is Sara?", "choices": ("Ten", "Eleven", "Twelve"), "answer": "Twelve"},
        ),
    },
    "speaking": {
        "shadowing": (
            "Hello! My name is Sara.",
            "Nice to meet you.",
            "I’m from Saudi Arabia.",
            "I’m twelve years old.",
        ),
        "role_play": (
            ("Coach", "Hello! What’s your name?"),
            ("You", "My name is …"),
            ("Coach", "Where are you from?"),
            ("You", "I’m from …"),
            ("Coach", "Nice to meet you!"),
            ("You", "Nice to meet you too!"),
        ),
    },
    "reading": {
        "title": "A new student",
        "text": "Hello! My name is Lina. I am eleven years old. I am from Jeddah, Saudi Arabia. I am a new student at Bright School. Omar is my new friend. He is twelve. We are in the English club.",
        "questions": (
            {"prompt": "How old is Lina?", "choices": ("10", "11", "12"), "answer": "11"},
            {"prompt": "Who is Lina’s new friend?", "choices": ("Adam", "Omar", "Ali"), "answer": "Omar"},
            {"prompt": "Where are Lina and Omar?", "choices": ("English club", "Restaurant", "Library"), "answer": "English club"},
        ),
    },
    "writing": {
        "prompt": "Write your mini profile in four sentences.",
        "frames": ("Hello! My name is ____.", "I am ____ years old.", "I am from ____.", "I am a ____.") ,
        "checklist": ("I used a capital letter.", "I used am after I.", "I ended each sentence with a full stop."),
        "model": "Hello! My name is Faisal. I am twelve years old. I am from Riyadh. I am a student.",
    },
    "games": (
        {"id": "word-match", "title": "Word Match", "icon": "🧠", "goal": "Match greetings and personal information with Arabic meanings."},
        {"id": "sentence-builder", "title": "Sentence Builder", "icon": "🧩", "goal": "Build: My name is Sara."},
        {"id": "missing-word", "title": "Missing Word", "icon": "⚡", "goal": "Choose am, is or are before time runs out."},
    ),
    "mission": {
        "title": "Meet a New Classmate",
        "brief": "Introduce yourself, answer two questions, and welcome your new classmate.",
        "steps": ("Say hello", "Say your name", "Say your age and country", "Ask: What’s your name?", "Finish with: Nice to meet you"),
        "success": "I can introduce myself clearly without reading every sentence.",
    },
}


QUIZ = (
    {
        "id": "vocab-greeting", "skill": "vocabulary", "prompt": "You meet a friend at 8:00 a.m. What do you say?",
        "choices": ("Good morning", "Goodbye", "Good night"), "answer": "Good morning",
        "why": "Good morning is the greeting used in the morning.",
        "wrong": {"Goodbye": "Goodbye ends a meeting; it does not begin one.", "Good night": "Good night is normally used when leaving at night or going to sleep."},
        "similar": {"prompt": "You are leaving your class. What do you say?", "choices": ("Welcome", "Goodbye", "Hello"), "answer": "Goodbye", "why": "Goodbye is used when you leave."},
    },
    {
        "id": "vocab-from", "skill": "vocabulary", "prompt": "Complete: I’m ___ Jeddah.",
        "choices": ("name", "from", "meet"), "answer": "from", "why": "From introduces a place of origin: I’m from Jeddah.",
        "wrong": {"name": "Name is a noun and cannot introduce a place here.", "meet": "Meet is a verb about seeing someone for the first time."},
        "similar": {"prompt": "Complete: She is ___ Riyadh.", "choices": ("from", "friend", "country"), "answer": "from", "why": "We use from before the city or country of origin."},
    },
    {
        "id": "grammar-i", "skill": "grammar", "prompt": "I ___ a student.",
        "choices": ("am", "is", "are"), "answer": "am", "why": "The subject I always takes am in the present tense.",
        "wrong": {"is": "Is is used with he, she or it—not I.", "are": "Are is used with you, we or they—not I."},
        "similar": {"prompt": "I ___ from Saudi Arabia.", "choices": ("is", "am", "are"), "answer": "am", "why": "I takes am: I am from Saudi Arabia."},
    },
    {
        "id": "grammar-she", "skill": "grammar", "prompt": "She ___ my new friend.",
        "choices": ("am", "is", "are"), "answer": "is", "why": "She takes is: She is my new friend.",
        "wrong": {"am": "Am is only used with I.", "are": "Are is used with you, we or they."},
        "similar": {"prompt": "He ___ twelve years old.", "choices": ("are", "am", "is"), "answer": "is", "why": "He, she and it take is."},
    },
    {
        "id": "grammar-you", "skill": "grammar", "prompt": "You ___ welcome here.",
        "choices": ("is", "are", "am"), "answer": "are", "why": "You takes are: You are welcome.",
        "wrong": {"is": "Is is used with he, she or it.", "am": "Am is only used with I."},
        "similar": {"prompt": "We ___ in the English club.", "choices": ("are", "is", "am"), "answer": "are", "why": "We and they take are."},
    },
    {
        "id": "listening-name", "skill": "listening", "prompt": "Listen, then choose the speaker’s name.", "spoken": "Hello. My name is Adam. I am a new student.",
        "choices": ("Omar", "Adam", "Ali"), "answer": "Adam", "why": "The speaker says: My name is Adam.",
        "wrong": {"Omar": "The recording does not mention Omar.", "Ali": "The recording does not mention Ali."},
        "similar": {"prompt": "Listen: Hi, I’m Lina. Choose the name.", "choices": ("Sara", "Lina", "Maya"), "answer": "Lina", "why": "I’m Lina means the speaker’s name is Lina."},
    },
    {
        "id": "listening-country", "skill": "listening", "prompt": "Listen, then choose the country.", "spoken": "Nice to meet you. I am from Saudi Arabia.",
        "choices": ("Saudi Arabia", "Jordan", "Egypt"), "answer": "Saudi Arabia", "why": "The speaker says: I am from Saudi Arabia.",
        "wrong": {"Jordan": "Jordan was not said in the recording.", "Egypt": "Egypt was not said in the recording."},
        "similar": {"prompt": "Listen: I’m from Oman. Choose the country.", "choices": ("Oman", "Qatar", "Kuwait"), "answer": "Oman", "why": "The place immediately after from is Oman."},
    },
    {
        "id": "reading-detail", "skill": "reading", "prompt": "Lina is eleven. Omar is twelve. Who is twelve?",
        "choices": ("Lina", "Omar", "Sara"), "answer": "Omar", "why": "The text directly says: Omar is twelve.",
        "wrong": {"Lina": "The text says Lina is eleven, not twelve.", "Sara": "Sara is not mentioned in this short text."},
        "similar": {"prompt": "Adam is ten. Faisal is eleven. Who is ten?", "choices": ("Faisal", "Adam", "Lina"), "answer": "Adam", "why": "The first sentence says Adam is ten."},
    },
    {
        "id": "writing-order", "skill": "writing", "prompt": "Choose the correctly written sentence.",
        "choices": ("my name is sara", "My name is Sara.", "My Name Is sara"), "answer": "My name is Sara.", "why": "A sentence and a person’s name begin with capital letters, and the sentence ends with a full stop.",
        "wrong": {"my name is sara": "The sentence and the name Sara need capital letters, and a full stop is missing.", "My Name Is sara": "Name and is do not need capital letters here, while Sara does."},
        "similar": {"prompt": "Choose the correctly written sentence.", "choices": ("I am from Riyadh.", "i am from riyadh", "I Am From riyadh."), "answer": "I am from Riyadh.", "why": "I and Riyadh are capitalized, and the sentence ends with a full stop."},
    },
    {
        "id": "speaking-response", "skill": "speaking", "prompt": "Someone says: Nice to meet you. Choose the natural reply.",
        "choices": ("Nice to meet you too.", "I am country.", "Good morning name."), "answer": "Nice to meet you too.", "why": "Adding too returns the same friendly greeting.",
        "wrong": {"I am country.": "This is not a meaningful reply and country needs more information.", "Good morning name.": "These words do not form a natural English response."},
        "similar": {"prompt": "Someone says: Welcome to our class! Choose the natural reply.", "choices": ("Thank you!", "I from class.", "Goodbye name."), "answer": "Thank you!", "why": "Thank you is a natural response to a welcome."},
    },
)


def public_quiz():
    return tuple({key: value for key, value in question.items() if key not in {"answer", "why", "wrong", "similar"}} for question in QUIZ)


def quiz_question(question_id):
    return next((question for question in QUIZ if question["id"] == question_id), None)
