from copy import deepcopy


CAN_DO = {
    "A1.1": ("I can greet someone politely.", "I can introduce myself.", "I can ask and answer simple personal questions.", "I can write a short introduction."),
    "A1.2": ("I can name close family members.", "I can talk about my family.", "I can use have and has.", "I can ask who someone is."),
    "A1.3": ("I can name everyday objects.", "I can use a and an.", "I can describe near and far objects.", "I can ask who owns an object."),
    "A1.4": ("I can say times in my day.", "I can describe my daily routine.", "I can ask and answer about routines.", "I can use usually and never."),
    "A1.5": ("I can describe actions happening now.", "I can ask what someone is doing.", "I can use am, is and are with -ing.", "I can give a short live report."),
    "A1.6": ("I can name common food and drinks.", "I can say what I like and dislike.", "I can ask for food and drink politely.", "I can respond to an offer."),
    "A1.7": ("I can name rooms and furniture.", "I can say what a room contains.", "I can locate objects in a room.", "I can ask and answer about a home."),
    "A1.8": ("I can ask where a place is.", "I can understand a short route.", "I can give simple directions.", "I can use a landmark and a polite opener."),
    "A1.9": ("I can say what I can and cannot do.", "I can ask and answer about abilities.", "I can make a polite request.", "I can respond naturally to a request."),
    "A1.10": ("I can locate an event in the past.", "I can use was and were.", "I can report finished actions in order.", "I can ask and answer basic weekend questions."),
}

EXPRESSIONS = {
    "A1.1": (("Hello!", "مرحبًا!", "Hello! I’m Sara."), ("Nice to meet you.", "سعيد بلقائك.", "Nice to meet you too."), ("Can you repeat that?", "هل يمكنك تكرار ذلك؟", "Sorry. Can you repeat that?")),
    "A1.2": (("This is my …", "هذا/هذه ... الخاص بي.", "This is my sister."), ("Who is this?", "من هذا/هذه؟", "Who is this in the photo?"), ("Her name is …", "اسمها ...", "Her name is Huda.")),
    "A1.3": (("What’s this?", "ما هذا؟", "What’s this? It’s a ruler."), ("These are my …", "هذه ... الخاصة بي.", "These are my keys."), ("Is this yours?", "هل هذا لك؟", "Excuse me. Is this yours?"), ("I don’t understand.", "أنا لا أفهم.", "Sorry, I don’t understand.")),
    "A1.4": (("What time do you …?", "في أي وقت ...؟", "What time do you wake up?"), ("every day", "كل يوم", "I study every day."), ("after school", "بعد المدرسة", "I play after school."), ("then", "ثم", "I eat, then I study.")),
    "A1.5": (("What are you doing?", "ماذا تفعل الآن؟", "What are you doing right now?"), ("right now", "الآن", "I’m studying right now."), ("Look!", "انظر!", "Look! They’re running.")),
    "A1.6": (("I’d like …, please.", "أود ... من فضلك.", "I’d like some water, please."), ("Can I have …?", "هل يمكنني الحصول على ...؟", "Can I have an apple?"), ("No, thank you.", "لا، شكرًا.", "No, thank you. I’m fine."), ("Of course.", "بالطبع.", "Of course. Here you are.")),
    "A1.7": (("Welcome to my home.", "مرحبًا بك في منزلي.", "Welcome to my home."), ("Is there …?", "هل يوجد ...؟", "Is there a desk?"), ("Where is …?", "أين ...؟", "Where is the school bag?"), ("next to", "بجانب", "The lamp is next to the bed.")),
    "A1.8": (("Excuse me.", "عذرًا.", "Excuse me. Where is the bank?"), ("Where is …?", "أين ...؟", "Where is the hospital?"), ("Thank you.", "شكرًا لك.", "Thank you for your help."), ("You’re welcome.", "على الرحب والسعة.", "You’re welcome.")),
    "A1.9": (("Can you …, please?", "هل يمكنك ... من فضلك؟", "Can you help me, please?"), ("Yes, of course.", "نعم، بالطبع.", "Yes, of course. I can help."), ("Sorry, I can’t.", "آسف، لا أستطيع.", "Sorry, I can’t carry it.")),
    "A1.10": (("How was your weekend?", "كيف كانت عطلة نهاية الأسبوع؟", "How was your weekend?"), ("Where did you go?", "إلى أين ذهبت؟", "Where did you go yesterday?"), ("What did you do?", "ماذا فعلت؟", "What did you do there?"), ("It was …", "لقد كان ...", "It was great.")),
}

REVIEW = {
    "A1.2": (("A1.1",), (("Complete the greeting: Nice to ___ you.", ("meet", "name", "from"), "meet"), ("Choose: I ___ Sara.", ("am", "is", "are"), "am"))),
    "A1.3": (("A1.1", "A1.2"), (("Choose the polite greeting.", ("Hello!", "Bag!", "Brother!"), "Hello!"), ("Mona ___ one brother.", ("have", "has", "are"), "has"))),
    "A1.4": (("A1.2", "A1.3"), (("We ___ two school bags.", ("have", "has", "is"), "have"), ("Choose the school object.", ("notebook", "mother", "kitchen"), "notebook"))),
    "A1.5": (("A1.1", "A1.4"), (("She ___ a student.", ("is", "are", "am"), "is"), ("Which phrase describes a routine?", ("every day", "right now", "Look!"), "every day"))),
    "A1.6": (("A1.3", "A1.4"), (("Choose: ___ apple.", ("an", "a", "some"), "an"), ("I have breakfast ___ day.", ("every", "now", "under"), "every"))),
    "A1.7": (("A1.3", "A1.6"), (("___ are my books.", ("These", "This", "That"), "These"), ("There is some milk in the ___.", ("kitchen", "park", "bank"), "kitchen"))),
    "A1.8": (("A1.1", "A1.7"), (("Choose a polite opener.", ("Excuse me.", "Bank now.", "Go you."), "Excuse me."), ("There ___ two parks.", ("are", "is", "am"), "are"))),
    "A1.9": (("A1.5", "A1.8"), (("They are ___ now.", ("running", "run", "runs"), "running"), ("Complete politely: ___ me. Where is the bank?", ("Excuse", "Turn", "Carry"), "Excuse"))),
    "A1.10": (("A1.2", "A1.4", "A1.6"), (("My family ___ lunch at home every Friday.", ("has", "have", "having"), "has"), ("Choose the past-time phrase.", ("yesterday", "right now", "every day"), "yesterday"))),
}

GIST = {
    "A1.1": ("What is the conversation mainly about?", ("a first meeting", "a meal", "a town map"), "a first meeting"),
    "A1.2": ("What are they looking at?", ("a family photo", "a menu", "a timetable"), "a family photo"),
    "A1.3": ("What is the main situation?", ("finding someone’s things", "ordering lunch", "asking the time"), "finding someone’s things"),
    "A1.4": ("What is Omar talking about?", ("his school day", "his family photo", "his home"), "his school day"),
    "A1.5": ("Is the home quiet or busy?", ("busy", "quiet", "empty"), "busy"),
    "A1.6": ("What is Sara doing?", ("ordering a meal", "giving directions", "describing a room"), "ordering a meal"),
    "A1.7": ("What is Lina showing?", ("a room", "a school bag", "a restaurant"), "a room"),
    "A1.8": ("What does the visitor need?", ("directions", "food", "a family photo"), "directions"),
    "A1.9": ("What is the conversation mainly about?", ("abilities and help", "yesterday", "furniture"), "abilities and help"),
    "A1.10": ("How was Sara’s weekend?", ("good", "bad", "not stated"), "good"),
}

SPEAKING = {
    "A1.1": ("What’s your name and where are you from?", "Introduce yourself in four clear sentences.", "Contractions and rhythm", "Use I’m naturally; stress your name and country."),
    "A1.2": ("Who is in your family?", "Introduce three family members from a photo or drawing.", "Word stress", "Stress the first syllable in mother, father and family."),
    "A1.3": ("What is in your bag?", "Show three objects and say who owns them.", "Plural endings", "Hear the final /s/ or /z/ in books, pens and keys."),
    "A1.4": ("What time do you start your day?", "Give a 30-second routine with four actions and two times.", "Third-person endings", "Notice /s/, /z/ and /ɪz/ in wakes, goes and watches."),
    "A1.5": ("What are you doing right now?", "Give a short live report about three people.", "Final -ing", "Keep the /ɪŋ/ ending clear and use natural question rhythm."),
    "A1.6": ("What food do you like?", "Order one food and one drink, then decline one offer politely.", "Polite request rhythm", "Use I’d /aɪd/ and don’t /dəʊnt/ clearly."),
    "A1.7": ("Is there a desk in your room?", "Give a short room tour and locate three objects.", "There and there’s", "Practise /ð/ in there and the short form there’s."),
    "A1.8": ("Where is a place near your home?", "Give a visitor two directions using one landmark.", "Direction rhythm", "Stress turn, straight, left and right."),
    "A1.9": ("What can you do well?", "Ask two ability questions and make one polite request.", "Can and can’t", "Compare weak can /kən/, strong can /kæn/ and can’t /kɑːnt/."),
    "A1.10": ("How was your weekend?", "Tell a five-part story and finish with how you felt.", "Past endings", "Notice /ɪd/, /d/ and /t/ in visited, played and watched."),
}

READING_TYPES = {
    "A1.1": ("Find information", "Who?", "Where?"), "A1.2": ("Choose", "Who?", "When?"),
    "A1.3": ("Find information", "How many?", "Whose?"), "A1.4": ("How?", "Sequence", "True / False"),
    "A1.5": ("What?", "Where?", "How many?"), "A1.6": ("Find information", "Choose", "Why?"),
    "A1.7": ("How many?", "Find information", "Where?"), "A1.8": ("Sequence", "Where?", "What?"),
    "A1.9": ("What?", "Who?", "Why?"), "A1.10": ("Why?", "Who?", "Sequence"),
}

WRITING_PROMPTS = {
    "A1.1": ("name", "age", "country", "one greeting"), "A1.2": ("family size", "three people", "one name", "have/has"),
    "A1.3": ("three objects", "one colour", "this/these", "one owner"), "A1.4": ("four actions", "two times", "usually/never", "then"),
    "A1.5": ("three people", "three actions", "now", "am/is/are + -ing"), "A1.6": ("two preferences", "one food order", "one drink", "please"),
    "A1.7": ("one room", "three objects", "there is/are", "two locations"), "A1.8": ("a start place", "two directions", "one landmark", "a destination"),
    "A1.9": ("three abilities", "one inability", "one request", "a natural response"), "A1.10": ("a past-time phrase", "where you were", "three actions", "a final feeling"),
}

EXTRA_GAMES = {
    "A1.1": ("fast-choice", "fast_choice", "Fast Choice", "Choose a natural greeting quickly.", "You meet a new classmate. What do you say?", ("Hello!", "Goodbye!", "I am country."), "Hello!", ""),
    "A1.2": ("grammar-detective", "grammar_detective", "Grammar Detective", "Choose have or has with the correct subject.", "Find the correct sentence.", ("She has one sister.", "She have one sister.", "She having sister."), "She has one sister.", ""),
    "A1.3": ("order-words", "order_words", "Order the Words", "Build a clear object sentence.", "Choose the correctly ordered sentence.", ("These are my books.", "My these books are.", "These my are books."), "These are my books.", ""),
    "A1.4": ("fast-choice", "fast_choice", "Fast Choice", "Choose the correct routine form.", "Sara ___ to school every day.", ("goes", "go", "going"), "goes", ""),
    "A1.5": ("grammar-detective", "grammar_detective", "Grammar Detective", "Find the complete action-now sentence.", "Which sentence is correct?", ("They are playing.", "They playing.", "They is playing."), "They are playing.", ""),
    "A1.6": ("listen-choose", "listen_choose", "Listen & Choose", "Recognise a polite food order.", "Listen, then choose the drink.", ("water", "juice", "milk"), "water", "I’d like some water, please."),
    "A1.7": ("memory", "memory", "Memory Pair", "Connect a room with a suitable object.", "Which pair belongs together?", ("bed — bedroom", "bed — bank", "sofa — bathroom"), "bed — bedroom", ""),
    "A1.8": ("order-words", "order_words", "Order the Words", "Put a direction in a clear order.", "Choose the correctly ordered direction.", ("Go straight, then turn left.", "Straight go left then.", "Then straight left go."), "Go straight, then turn left.", ""),
    "A1.9": ("fast-choice", "fast_choice", "Fast Choice", "Use can with a base verb.", "She can ___ a bike.", ("ride", "rides", "riding"), "ride", ""),
    "A1.10": ("grammar-detective", "grammar_detective", "Grammar Detective", "Choose a correct finished action.", "Which sentence is correct?", ("We went to the park.", "We goed to the park.", "We go yesterday."), "We went to the park.", ""),
}

COLLOCATIONS = {
    "A1.1": {"good morning": "say good morning", "meet": "meet a friend"},
    "A1.2": {"family": "a big family", "parents": "my parents"},
    "A1.3": {"school": "school bag", "keys": "house keys", "notebook": "English notebook"},
    "A1.4": {"wake up": "wake up early", "have breakfast": "have breakfast", "do homework": "do homework", "go to school": "go to school"},
    "A1.5": {"reading": "reading a book", "talking": "talking on the phone"},
    "A1.6": {"orange juice": "orange juice", "menu": "look at the menu", "water": "some water"},
    "A1.7": {"living room": "in the living room", "table": "on the table", "bed": "under the bed"},
    "A1.8": {"turn left": "turn left at the bank", "turn right": "turn right", "go straight": "go straight"},
    "A1.9": {"ride a bike": "ride a bike", "help": "help a friend"},
    "A1.10": {"last weekend": "last weekend", "played": "played football", "watched": "watched a film"},
}


def _replace_strings(value, replacements):
    if isinstance(value, str):
        for old, new in replacements.items():
            value = value.replace(old, new)
        return value
    if isinstance(value, tuple):
        return tuple(_replace_strings(item, replacements) for item in value)
    if isinstance(value, list):
        return [_replace_strings(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: _replace_strings(item, replacements) for key, item in value.items()}
    return value


def _grammar_practice(unit):
    questions = [item for item in unit["quiz"] if item["skill"] == "grammar"]
    mistake = unit["grammar"]["common_mistakes"][0]
    wrong, separator, correct = mistake.partition("→")
    correct = correct.strip() if separator else unit["grammar"]["examples"][0]
    wrong = wrong.strip()
    return (
        {"stage": "Choose", **{key: questions[0][key] for key in ("prompt", "choices", "answer")}},
        {"stage": "Complete", **{key: questions[1][key] for key in ("prompt", "choices", "answer")}},
        {"stage": "Build sentence", "prompt": "Build the model sentence.", "target": unit["grammar"]["examples"][0], "tokens": tuple(reversed(unit["grammar"]["examples"][0].split()))},
        {"stage": "Correct mistake", "prompt": f"Correct: {wrong}", "choices": (wrong, correct), "answer": correct},
        {"stage": "Use it in context", **{key: questions[2][key] for key in ("prompt", "choices", "answer")}},
    )


def enrich_a1_unit(source):
    unit = deepcopy(source)
    code = unit["code"]
    if code not in CAN_DO:
        return unit
    replacements = {
        "color": "colour", "Color": "Colour",
        "The subject I always takes am in the present tense.": "Use am with the subject I in the present tense.",
        "I takes am:": "Use am with I:",
        "You takes are:": "Use are with You:",
        "She takes is:": "Use is with She:",
        "She takes is before the -ing verb.": "Use is with She before the -ing verb.",
        "He takes is.": "Use is with He.",
        "One nearby thing takes this.": "Use this for one nearby thing.",
        "One far thing takes that.": "Use that for one far thing.",
        "Several nearby things take these and are.": "Use these and are for several nearby things.",
        "Several far things take those.": "Use those for several far things.",
        "These is plural and takes are; books is plural.": "These and books are plural, so use are.",
        "Those takes are with a plural noun.": "Use are after Those with a plural noun.",
        "This is describes one nearby object.": "Use This is for one nearby object.",
        "These are describes several nearby objects.": "Use These are for several nearby objects.",
        "She takes doesn’t before the base verb like.": "Use doesn’t with She before the base verb like.",
        "He takes doesn’t.": "Use doesn’t with He.",
        "She takes doesn’t.": "Use doesn’t with She.",
        "He takes Does in a present simple question.": "Use Does with He in a present simple question.",
        "Three chairs is plural.": "Three chairs are plural.",
        "Plural two beds takes there are.": "Use there are with the plural phrase two beds.",
        "One table takes there is and a.": "Use there is and a with one table.",
        "A singular Is there question takes there is.": "Answer a singular Is there question with there is.",
        "A plural Are there question takes there are.": "Answer a plural Are there question with there are.",
        "Can stays unchanged and takes base verb draw.": "Can stays unchanged and is followed by the base verb draw.",
        "I takes was in the past.": "Use was with I in the past.",
        "She takes was.": "Use was with She.",
        "Plural they takes were in the past.": "Use were with plural they in the past.",
        "We takes were.": "Use were with We.",
        "امشِ بعد الحديقة.": "تجاوز الحديقة سيرًا.",
    }
    if code == "A1.5":
        replacements.update({
            "They takes are followed by running.": "Use are with They, followed by running.",
            "They takes are.": "Use are with They.",
            "We takes are.": "Use are with We.",
        })
    if code == "A1.6":
        replacements.update({
            "Would you like any juice?": "Would you like some juice?",
            "Would you like any …?": "Would you like some …?",
            "Do you have some water? → Do you have any water?": "Use any to ask about availability; use some in polite requests and offers.",
        })
    if code == "A1.7":
        replacements.update({"Two windows is plural.": "Two windows are plural.", "sofa lamp": "sofa"})
    if code == "A1.9":
        replacements["swim and bike"] = "swim and ride a bike"
    unit = _replace_strings(unit, replacements)
    if code == "A1.1":
        translations = {
            "hello": "مرحبًا، أنا سارة.", "good morning": "صباح الخير يا أستاذ علي.",
            "name": "اسمي عمر.", "meet": "سعيد بلقائك.", "from": "أنا من المملكة العربية السعودية.",
            "country": "المملكة العربية السعودية دولة.", "student": "هي طالبة جديدة.",
            "friend": "علي صديقي.", "welcome": "مرحبًا بك في صفنا.", "goodbye": "إلى اللقاء يا نورة.",
        }
        for item in unit["vocabulary"]:
            item["example_ar"] = translations[item["word"]]
    if code == "A1.2":
        question = next(item for item in unit["quiz"] if item["id"] == "v1")
        question["similar_question"] = {"prompt": "Huda and Ali have a daughter. She is their ___.", "choices": ("daughter", "mother", "sister"), "answer": "daughter", "why": "Daughter is a female child."}
        unit["grammar"]["common_mistakes"] = ("She have one brother. → She has one brother.", "He name is Ali. → His name is Ali.", unit["grammar"]["common_mistakes"][2])
        unit["speaking"]["pronunciation_practice"] = ("mother /ˈmʌðə/", "father /ˈfɑːðə/", "family /ˈfæməli/")
    if code == "A1.3":
        unit["grammar"]["functional_chunks"] = ("Whose bag is this?", "It’s Maya’s.", "Are these yours?", "Yes, they are. / No, they aren’t.")
        unit["british_english_note"] = "In British classroom English, rubber is also used for eraser."
    if code == "A1.6":
        similar = next(item for item in unit["quiz"] if item["id"] == "v1")["similar_question"]
        similar["prompt"] = "Which item do you eat rather than drink?"
    if code == "A1.7":
        similar = next(item for item in unit["quiz"] if item["id"] == "v2")["similar_question"]
        similar["choices"] = ("bed", "table", "window")
        reading_question = unit["reading"]["questions"][2]
        reading_question["choices"] = ("under the window", "between the desk and the bed", "on the chair")
        reading_question["answer"] = "between the desk and the bed"
        reading_similar = next(item for item in unit["quiz"] if item["id"] == "r1")["similar_question"]
        reading_similar["prompt"] = "The bag is between the desk and the bed. What is beside the bag?"
        reading_similar["choices"] = ("the desk and the bed", "two windows", "the kitchen")
        reading_similar["answer"] = "the desk and the bed"
    if code == "A1.10":
        next(item for item in unit["quiz"] if item["id"] == "v1")["similar_question"]["prompt"] = "Which phrase refers to the weekend before this one?"
    unit["phase3_version"] = 1
    unit["can_do_statements"] = CAN_DO[code]
    for item in unit["vocabulary"]:
        item["group"] = "core"
        item["collocation"] = COLLOCATIONS.get(code, {}).get(item["word"], item.get("collocation", ""))
        if item.get("audio"):
            item["audio"]["lang"] = "en-GB"
        if code == "A1.5":
            item["word_family"] = {
                "reading": "read → reading",
                "writing": "write → writing",
                "running": "run → running",
                "sitting": "sit → sitting",
                "talking": "talk → talking",
                "playing": "play → playing",
            }.get(item["word"], item.get("word_family", ""))
    unit["useful_expressions"] = tuple({"expression": text, "arabic": arabic, "example": example} for text, arabic, example in EXPRESSIONS[code])
    if code in REVIEW:
        references, items = REVIEW[code]
        unit["review_from"] = references
        unit["spiral_review"] = {"ratio": "80/20", "items": tuple({"prompt": prompt, "choices": choices, "answer": answer} for prompt, choices, answer in items)}
    else:
        unit["review_from"] = ()
        unit["spiral_review"] = {"ratio": "foundation", "items": ()}
    unit["grammar"]["practice"] = _grammar_practice(unit)
    if code == "A1.10":
        unit["grammar"]["functional_chunks"] = ("How was your weekend?", "Where did you go?", "What did you do?", "Use did + base verb in the question; answer with a past verb.")
    gist_prompt, gist_choices, gist_answer = GIST[code]
    unit["listening"]["gist_question"] = {"prompt": gist_prompt, "choices": gist_choices, "answer": gist_answer}
    unit["listening"]["stages"] = ("Listen for the main idea.", "Listen for names, times, places or actions.", "Listen again, answer, then check the transcript.")
    question, challenge, focus, tip = SPEAKING[code]
    unit["speaking"].update({
        "answer_question": question,
        "mini_challenge": challenge,
        "pronunciation_focus": {"title": focus, "tip": tip},
        "rubric": ("Meaning", "Target language", "Clarity", "Completion"),
    })
    for question_item, question_type in zip(unit["reading"]["questions"], READING_TYPES[code]):
        question_item["question_type"] = question_type
    unit["reading"]["strategy"] = "Read once for the main idea. Read again and find the exact clue."
    prompts = WRITING_PROMPTS[code]
    scaffold = tuple(unit["writing"].get("scaffold", ()))
    unit["writing"].update({
        "guided": scaffold[:2],
        "semi_guided": tuple(f"Include: {prompt}." for prompt in prompts[:3]),
        "independent": unit["writing"]["task"],
        "productive_practice": True,
    })
    game_id, game_type, title, goal, prompt, choices, answer, spoken = EXTRA_GAMES[code]
    unit["games"] = (*unit["games"], {"id": game_id, "type": game_type, "title": title, "goal": goal, "prompt": prompt, "choices": choices, "answer": answer, **({"spoken": spoken} if spoken else {})})
    unit["mission"]["integrated_skills"] = ("speaking", "listening", "vocabulary", "grammar")
    for question_item in unit["quiz"]:
        productive = question_item["skill"] not in {"speaking", "writing"}
        question_item["productive_score"] = productive
        if not productive:
            question_item["assessment_label"] = "Auto-scored language choice — not a productive skill score"
    return unit


A1_READINESS_REVIEW = (
    {"skill": "Vocabulary", "icon": "🧠", "task": "Recall words from personal life, home, town, dates, weather, shopping, school, jobs and communication; use five in context.", "mode": "Self-check · A1.1–A1.20"},
    {"skill": "Grammar", "icon": "🧩", "task": "Review be, present forms, can, there is/are, basic past, dates, like + -ing, prices, have got, nationality and polite requests.", "mode": "Practice · A1.1–A1.20"},
    {"skill": "Listening", "icon": "🎧", "task": "Practise the main idea and details in introductions, directions, dates, weather, shops, timetables and everyday messages.", "mode": "Practice · A1.1–A1.20"},
    {"skill": "Reading", "icon": "📖", "task": "Read short profiles, notices, timetables, offers and programmes; find who, where, when, price and event order.", "mode": "Self-check · A1.1–A1.20"},
    {"skill": "Speaking", "icon": "🎤", "task": "Introduce yourself, handle one familiar transaction, ask for clarification and explain a short plan.", "mode": "Productive practice — not auto-scored"},
    {"skill": "Writing", "icon": "✍️", "task": "Write five connected sentences with personal information, a day/time, an activity and one practical detail.", "mode": "Productive practice — not auto-scored"},
)
