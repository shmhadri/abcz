SKILLS = ("vocabulary", "grammar", "reading", "listening", "speaking", "writing")

A1_UNITS = (
    ("A1.1", "Hello!", "Greetings, names, age and countries", "be", "Introduce yourself to a new classmate"),
    ("A1.2", "My Family", "Family words and simple descriptions", "possessives · have/has", "Introduce your family"),
    ("A1.3", "My Things", "Everyday objects and ownership", "this/that · plurals · a/an", "Describe the things in your bag"),
    ("A1.4", "My Day", "Routines and telling the time", "Present Simple", "Plan and describe your day"),
    ("A1.5", "What Are You Doing?", "Activities happening now", "Present Continuous", "Report what people are doing"),
    ("A1.6", "Food & Drinks", "Meals, preferences and ordering", "like/don't like · some/any", "Order your meal"),
    ("A1.7", "My Home", "Rooms, furniture and location", "there is/are", "Give a tour of your home"),
    ("A1.8", "Around Town", "Places and simple directions", "prepositions", "Help a visitor find a place"),
    ("A1.9", "I Can!", "Abilities and polite requests", "can/can't", "Ask for help and offer help"),
    ("A1.10", "Yesterday", "Finished events and level review", "basic Past Simple", "Tell a short story about yesterday"),
)

A2_UNITS = (
    ("A2.1", "My Life", "Habits versus actions happening now", "Present Simple/Continuous", "Describe a busy week"),
    ("A2.2", "What Happened?", "Past events and time expressions", "Past Simple", "Explain what happened"),
    ("A2.3", "Life Experiences", "Experiences without a finished time", "Present Perfect", "Interview someone about experiences"),
    ("A2.4", "Plans & Dreams", "Intentions, predictions and decisions", "going to / will", "Present your future plan"),
    ("A2.5", "Health", "Symptoms, advice and obligations", "should · have to", "Help a patient choose what to do"),
    ("A2.6", "Shopping", "Prices, choices and quantities", "comparatives · superlatives", "Complete a shopping challenge"),
    ("A2.7", "Travel", "Transport, booking and directions", "travel language", "Book a complete journey"),
    ("A2.8", "Technology", "Devices, communication and instructions", "imperatives · sequencing", "Teach someone to use an app"),
    ("A2.9", "Stories & Events", "Connecting and sequencing ideas", "because/so/when/but", "Retell an event clearly"),
    ("A2.10", "Real English", "Integrated language in everyday situations", "A2 integration", "Complete the final real-world mission"),
)

LEVELS = {
    "a1": {"code": "A1", "title": "A1 Explorer", "icon": "🏝️", "units": A1_UNITS},
    "a2": {"code": "A2", "title": "A2 Explorer", "icon": "🚀", "units": A2_UNITS},
}

VOCABULARY = {
    "A1.1": (("hello", "مرحبًا"), ("name", "اسم"), ("country", "دولة"), ("friend", "صديق"), ("welcome", "أهلًا بك")),
    "A1.6": (("hungry", "جائع"), ("menu", "قائمة الطعام"), ("meal", "وجبة"), ("drink", "مشروب"), ("bill", "الفاتورة")),
    "A2.7": (("journey", "رحلة"), ("ticket", "تذكرة"), ("platform", "رصيف"), ("booking", "حجز"), ("luggage", "أمتعة")),
}


def _unit(raw):
    code, title, topic, grammar, mission = raw
    words = VOCABULARY.get(code, (("practice", "يتدرّب"), ("challenge", "تحدٍ"), ("improve", "يتحسن"), ("remember", "يتذكر"), ("ready", "مستعد")))
    return {
        "code": code,
        "slug": code.lower().replace(".", "-"),
        "title": title,
        "topic": topic,
        "grammar": grammar,
        "mission": mission,
        "vocabulary": words,
        "example": "She goes to school every day." if "Present Simple" in grammar else f"Let's use English in: {title}.",
    }


def units_for(level_slug):
    level = LEVELS.get(level_slug)
    return [_unit(row) for row in level["units"]] if level else []


def all_units():
    return [unit for slug in LEVELS for unit in units_for(slug)]


def get_unit(unit_slug):
    return next((unit for unit in all_units() if unit["slug"] == unit_slug.lower()), None)


ASSESSMENT_QUESTIONS = (
    {"id": "q1", "skill": "grammar", "question": "She ___ to school every day.", "choices": ("go", "goes", "going"), "answer": "goes"},
    {"id": "q2", "skill": "vocabulary", "question": "Choose the food word.", "choices": ("station", "sandwich", "window"), "answer": "sandwich"},
    {"id": "q3", "skill": "reading", "question": "Maya gets up at seven. When does Maya get up?", "choices": ("At six", "At seven", "At eight"), "answer": "At seven"},
    {"id": "q4", "skill": "listening", "question": "A speaker says: 'Turn left at the bank.' Where do you turn?", "choices": ("Left", "Right", "Back"), "answer": "Left"},
    {"id": "q5", "skill": "speaking", "question": "Choose the polite request.", "choices": ("Give water", "I'd like some water, please.", "Water now"), "answer": "I'd like some water, please."},
    {"id": "q6", "skill": "writing", "question": "Choose the complete sentence.", "choices": ("My family is small.", "Family small", "My is family"), "answer": "My family is small."},
)
