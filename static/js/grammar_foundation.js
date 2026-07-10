(function () {
    "use strict";

    const progressKey = "abcz-grammar-foundation-progress-v1";
    const themeKey = "abcz-grammar-foundation-theme";
    const categories = ["Pronouns", "Basics", "Nouns", "Tenses", "Questions", "Modals", "Prepositions", "Comparatives", "Challenge"];

    function lesson(data) {
        const examples = fillFive(data.examples || [data.example]);
        const examplesAr = fillFive(data.examples_ar || [data.example_ar || ""]);
        return {
            id: data.id,
            title: data.title,
            title_ar: data.title_ar,
            category: data.category,
            level: data.level,
            icon: data.icon || "✓",
            short_rule_en: data.short_rule_en,
            explanation_ar: data.explanation_ar,
            structure: data.structure,
            examples,
            examples_ar: examplesAr,
            common_mistake: data.common_mistake,
            correction: data.correction,
            quick_question: data.quick_question,
            choices: data.choices,
            correct_answer: data.correct_answer,
            fill_blank: data.fill_blank,
            fill_blank_answer: data.fill_blank_answer,
            true_false: data.true_false,
            true_false_answer: data.true_false_answer,
            sentence_order_words: data.sentence_order_words,
            sentence_order_answer: data.sentence_order_answer,
            translate_ar: data.translate_ar || data.examples_ar?.[0] || "",
            translate_answer: data.translate_answer || data.examples?.[0] || "",
            make_question_answer: data.make_question_answer || data.quick_question?.replace("____", data.correct_answer || ""),
            tense: data.tense || data.category
        };
    }

    function fillFive(items) {
        const safe = [...items].filter(Boolean);
        while (safe.length < 5) safe.push(safe[safe.length - 1] || "I study English.");
        return safe.slice(0, 5);
    }

    const grammarData = [
        lesson({ id: "subject-pronouns", title: "Subject Pronouns", title_ar: "ضمائر الفاعل", category: "Pronouns", level: "Easy", icon: "👤", short_rule_en: "I / you / he / she / it / we / they replace the subject.", explanation_ar: "ضمائر الفاعل تحل محل اسم الشخص أو الشيء الذي يقوم بالفعل.", structure: "Subject pronoun + verb", examples: ["I am a student.", "You are kind.", "He plays football.", "She reads books.", "They study English."], examples_ar: ["أنا طالب.", "أنت لطيف.", "هو يلعب كرة القدم.", "هي تقرأ الكتب.", "هم يدرسون الإنجليزية."], common_mistake: "Me am a student.", correction: "I am a student.", quick_question: "____ am a student.", choices: ["I", "Me", "My", "Mine"], correct_answer: "I", fill_blank: "____ is happy.", fill_blank_answer: "She", true_false: "They is a subject pronoun.", true_false_answer: true, sentence_order_words: ["She", "reads", "books"], sentence_order_answer: "She reads books.", translate_ar: "هي تقرأ الكتب.", translate_answer: "She reads books.", make_question_answer: "Is she happy?" }),
        lesson({ id: "object-pronouns", title: "Object Pronouns", title_ar: "ضمائر المفعول", category: "Pronouns", level: "Easy", icon: "🎯", short_rule_en: "me / you / him / her / it / us / them receive the action.", explanation_ar: "ضمائر المفعول تأتي بعد الفعل أو حرف الجر وتستقبل الفعل.", structure: "verb + object pronoun", examples: ["The teacher helped me.", "I called him.", "She saw us.", "They invited her.", "We like them."], examples_ar: ["ساعدني المعلم.", "اتصلت به.", "هي رأتنا.", "دعواها.", "نحن نحبهم."], common_mistake: "The teacher helped I.", correction: "The teacher helped me.", quick_question: "The teacher helped ____.", choices: ["me", "I", "my", "mine"], correct_answer: "me", fill_blank: "I called ____ yesterday.", fill_blank_answer: "him", true_false: "Me can come after a verb.", true_false_answer: true, sentence_order_words: ["The", "teacher", "helped", "me"], sentence_order_answer: "The teacher helped me.", translate_ar: "ساعدني المعلم.", translate_answer: "The teacher helped me.", make_question_answer: "Did the teacher help me?" }),
        lesson({ id: "possessive-adjectives", title: "Possessive Adjectives", title_ar: "صفات الملكية", category: "Pronouns", level: "Easy", icon: "🧩", short_rule_en: "my / your / his / her / its / our / their come before a noun.", explanation_ar: "صفات الملكية تأتي قبل الاسم لتوضح من يملك الشيء.", structure: "possessive adjective + noun", examples: ["This is my bag.", "Her pencil is red.", "Our class is clean.", "Their house is big.", "His book is new."], examples_ar: ["هذه حقيبتي.", "قلمها أحمر.", "فصلنا نظيف.", "بيتهم كبير.", "كتابه جديد."], common_mistake: "This is mine bag.", correction: "This is my bag.", quick_question: "This is ____ bag.", choices: ["my", "mine", "me", "I"], correct_answer: "my", fill_blank: "____ pencil is red.", fill_blank_answer: "Her", true_false: "My comes before a noun.", true_false_answer: true, sentence_order_words: ["This", "is", "my", "bag"], sentence_order_answer: "This is my bag.", translate_ar: "هذه حقيبتي.", translate_answer: "This is my bag.", make_question_answer: "Is this my bag?" }),
        lesson({ id: "possessive-pronouns", title: "Possessive Pronouns", title_ar: "ضمائر الملكية", category: "Pronouns", level: "Medium", icon: "🔐", short_rule_en: "mine / yours / his / hers / ours / theirs replace possessive adjective + noun.", explanation_ar: "ضمائر الملكية تأتي وحدها ولا تحتاج اسمًا بعدها.", structure: "noun + be + possessive pronoun", examples: ["This book is mine.", "The red bag is hers.", "The classroom is ours.", "This phone is yours.", "The bikes are theirs."], examples_ar: ["هذا الكتاب لي.", "الحقيبة الحمراء لها.", "الفصل لنا.", "هذا الهاتف لك.", "الدراجات لهم."], common_mistake: "This book is my.", correction: "This book is mine.", quick_question: "This book is ____.", choices: ["mine", "my", "me", "I"], correct_answer: "mine", fill_blank: "The red bag is ____.", fill_blank_answer: "hers", true_false: "Mine can stand alone.", true_false_answer: true, sentence_order_words: ["This", "book", "is", "mine"], sentence_order_answer: "This book is mine.", translate_ar: "هذا الكتاب لي.", translate_answer: "This book is mine.", make_question_answer: "Is this book mine?" }),
        lesson({ id: "verb-to-be", title: "Verb to be", title_ar: "فعل الكون", category: "Basics", level: "Easy", icon: "⚙️", short_rule_en: "Use am with I, is with he/she/it, are with you/we/they.", explanation_ar: "نستخدم am و is و are لوصف الشخص أو الشيء أو حالته.", structure: "subject + am/is/are + complement", examples: ["I am a student.", "She is happy.", "They are ready.", "He is tired.", "We are friends."], examples_ar: ["أنا طالب.", "هي سعيدة.", "هم جاهزون.", "هو متعب.", "نحن أصدقاء."], common_mistake: "She are happy.", correction: "She is happy.", quick_question: "She ____ happy.", choices: ["am", "is", "are", "be"], correct_answer: "is", fill_blank: "I ____ a student.", fill_blank_answer: "am", true_false: "They are ready.", true_false_answer: true, sentence_order_words: ["She", "is", "happy"], sentence_order_answer: "She is happy.", translate_ar: "أنا طالب.", translate_answer: "I am a student.", make_question_answer: "Is she happy?" }),
        lesson({ id: "verb-to-be-negative", title: "Verb to be Negative", title_ar: "النفي مع فعل الكون", category: "Basics", level: "Easy", icon: "🚫", short_rule_en: "Add not after am / is / are.", explanation_ar: "للنفي نضيف not بعد am أو is أو are.", structure: "subject + am/is/are + not", examples: ["He is not tired.", "I am not late.", "They are not ready.", "She is not angry.", "We are not at home."], examples_ar: ["هو ليس متعبًا.", "أنا لست متأخرًا.", "هم ليسوا جاهزين.", "هي ليست غاضبة.", "نحن لسنا في البيت."], common_mistake: "He not is tired.", correction: "He is not tired.", quick_question: "He ____ tired.", choices: ["is not", "not is", "are not", "am not"], correct_answer: "is not", fill_blank: "They ____ ready.", fill_blank_answer: "are not", true_false: "Not comes after is.", true_false_answer: true, sentence_order_words: ["He", "is", "not", "tired"], sentence_order_answer: "He is not tired.", translate_ar: "هو ليس متعبًا.", translate_answer: "He is not tired.", make_question_answer: "Is he tired?" }),
        lesson({ id: "verb-to-be-questions", title: "Verb to be Questions", title_ar: "أسئلة فعل الكون", category: "Questions", level: "Easy", icon: "❓", short_rule_en: "Move am / is / are before the subject.", explanation_ar: "لتكوين سؤال نضع am أو is أو are قبل الفاعل.", structure: "Am/Is/Are + subject + complement?", examples: ["Are you ready?", "Is she happy?", "Am I late?", "Are they friends?", "Is it cold?"], examples_ar: ["هل أنت جاهز؟", "هل هي سعيدة؟", "هل أنا متأخر؟", "هل هم أصدقاء؟", "هل الجو بارد؟"], common_mistake: "You are ready?", correction: "Are you ready?", quick_question: "____ you ready?", choices: ["Are", "Is", "Am", "Do"], correct_answer: "Are", fill_blank: "____ she happy?", fill_blank_answer: "Is", true_false: "Are you ready? is a question.", true_false_answer: true, sentence_order_words: ["Are", "you", "ready"], sentence_order_answer: "Are you ready?", translate_ar: "هل أنت جاهز؟", translate_answer: "Are you ready?", make_question_answer: "Are you ready?" }),
        lesson({ id: "there-is-there-are", title: "There is / There are", title_ar: "يوجد للمفرد والجمع", category: "Basics", level: "Easy", icon: "📍", short_rule_en: "Use there is for one thing and there are for more than one.", explanation_ar: "نستخدم there is للمفرد و there are للجمع.", structure: "There is/are + noun + place", examples: ["There is a book on the table.", "There are three students.", "There is a cat in the room.", "There are many pencils.", "There is water in the bottle."], examples_ar: ["يوجد كتاب على الطاولة.", "يوجد ثلاثة طلاب.", "توجد قطة في الغرفة.", "توجد أقلام كثيرة.", "يوجد ماء في الزجاجة."], common_mistake: "There are a book.", correction: "There is a book.", quick_question: "There ____ a book on the table.", choices: ["is", "are", "am", "be"], correct_answer: "is", fill_blank: "There ____ three students.", fill_blank_answer: "are", true_false: "There are is used with plural nouns.", true_false_answer: true, sentence_order_words: ["There", "is", "a", "book"], sentence_order_answer: "There is a book.", translate_ar: "يوجد كتاب على الطاولة.", translate_answer: "There is a book on the table.", make_question_answer: "Is there a book?" }),
        lesson({ id: "articles", title: "Articles", title_ar: "أدوات التعريف والتنكير", category: "Basics", level: "Easy", icon: "🔤", short_rule_en: "Use a before consonant sounds, an before vowel sounds, the for specific things.", explanation_ar: "نستخدم a و an لشيء غير محدد، و the لشيء محدد أو معروف.", structure: "a/an/the + noun", examples: ["I have a book.", "She eats an apple.", "The sun is bright.", "This is a pencil.", "The teacher is kind."], examples_ar: ["لدي كتاب.", "هي تأكل تفاحة.", "الشمس ساطعة.", "هذا قلم رصاص.", "المعلم لطيف."], common_mistake: "I have an book.", correction: "I have a book.", quick_question: "She eats ____ apple.", choices: ["an", "a", "the", "no article"], correct_answer: "an", fill_blank: "I have ____ book.", fill_blank_answer: "a", true_false: "An is used before vowel sounds.", true_false_answer: true, sentence_order_words: ["She", "eats", "an", "apple"], sentence_order_answer: "She eats an apple.", translate_ar: "هي تأكل تفاحة.", translate_answer: "She eats an apple.", make_question_answer: "Does she eat an apple?" }),
        lesson({ id: "singular-plural-nouns", title: "Singular and Plural Nouns", title_ar: "المفرد والجمع", category: "Nouns", level: "Easy", icon: "📚", short_rule_en: "Add s or es to many nouns; change y to ies after a consonant.", explanation_ar: "المفرد يعني شيئًا واحدًا، والجمع يعني أكثر من واحد.", structure: "book/books, box/boxes, city/cities", examples: ["I have two books.", "There are three boxes.", "The cities are big.", "One student is here.", "Many teachers are kind."], examples_ar: ["لدي كتابان.", "توجد ثلاثة صناديق.", "المدن كبيرة.", "طالب واحد هنا.", "معلمون كثيرون لطفاء."], common_mistake: "two book", correction: "two books", quick_question: "I have two ____.", choices: ["books", "book", "bookes", "bookies"], correct_answer: "books", fill_blank: "There are three ____.", fill_blank_answer: "boxes", true_false: "Cities is the plural of city.", true_false_answer: true, sentence_order_words: ["I", "have", "two", "books"], sentence_order_answer: "I have two books.", translate_ar: "لدي كتابان.", translate_answer: "I have two books.", make_question_answer: "Do you have two books?" }),
        lesson({ id: "countable-uncountable", title: "Countable and Uncountable Nouns", title_ar: "الأسماء المعدودة وغير المعدودة", category: "Nouns", level: "Medium", icon: "🥛", short_rule_en: "Countable nouns can be counted; uncountable nouns use some or much.", explanation_ar: "الأسماء المعدودة يمكن عدها، وغير المعدودة لا نعدها مباشرة مثل الماء.", structure: "a/an + countable, some + uncountable", examples: ["I have a book.", "I drink some water.", "There are many chairs.", "There is some milk.", "She needs advice."], examples_ar: ["لدي كتاب.", "أشرب بعض الماء.", "توجد كراس كثيرة.", "يوجد بعض الحليب.", "هي تحتاج نصيحة."], common_mistake: "I drink a water.", correction: "I drink some water.", quick_question: "I drink ____ water.", choices: ["some", "a", "an", "many"], correct_answer: "some", fill_blank: "I have ____ book.", fill_blank_answer: "a", true_false: "Water is usually uncountable.", true_false_answer: true, sentence_order_words: ["I", "drink", "some", "water"], sentence_order_answer: "I drink some water.", translate_ar: "أشرب بعض الماء.", translate_answer: "I drink some water.", make_question_answer: "Do you drink water?" }),
        lesson({ id: "this-that-these-those", title: "This / That / These / Those", title_ar: "أسماء الإشارة", category: "Basics", level: "Easy", icon: "👉", short_rule_en: "This/these are near; that/those are far. This/that are singular; these/those are plural.", explanation_ar: "نستخدم هذه الكلمات للإشارة إلى أشياء قريبة أو بعيدة ومفردة أو جمع.", structure: "this/that + singular, these/those + plural", examples: ["This is my pen.", "That is your bag.", "These are my books.", "Those are my shoes.", "This is a classroom."], examples_ar: ["هذا قلمي.", "تلك حقيبتك.", "هذه كتبي.", "تلك أحذيتي.", "هذا فصل دراسي."], common_mistake: "These is my book.", correction: "This is my book.", quick_question: "____ are my shoes.", choices: ["Those", "That", "This", "It"], correct_answer: "Those", fill_blank: "____ is my pen.", fill_blank_answer: "This", true_false: "These is used with plural nouns.", true_false_answer: true, sentence_order_words: ["This", "is", "my", "pen"], sentence_order_answer: "This is my pen.", translate_ar: "هذا قلمي.", translate_answer: "This is my pen.", make_question_answer: "Is this my pen?" }),
        lesson({ id: "present-simple-positive", title: "Present Simple Positive", title_ar: "المضارع البسيط المثبت", category: "Tenses", level: "Easy", icon: "⏱️", short_rule_en: "Use the base verb; add s/es with he, she, it.", explanation_ar: "نستخدم المضارع البسيط للعادات والحقائق والأشياء المتكررة.", structure: "subject + verb / verb+s", examples: ["I play football.", "She reads books.", "He watches TV.", "They study English.", "We go to school."], examples_ar: ["ألعب كرة القدم.", "هي تقرأ الكتب.", "هو يشاهد التلفاز.", "هم يدرسون الإنجليزية.", "نذهب إلى المدرسة."], common_mistake: "She read books every day.", correction: "She reads books every day.", quick_question: "She ____ books every day.", choices: ["reads", "read", "reading", "is read"], correct_answer: "reads", fill_blank: "I ____ football.", fill_blank_answer: "play", true_false: "We add s with she in present simple.", true_false_answer: true, sentence_order_words: ["She", "reads", "books"], sentence_order_answer: "She reads books.", translate_ar: "هي تقرأ الكتب كل يوم.", translate_answer: "She reads books every day.", make_question_answer: "Does she read books?", tense: "Present Simple" }),
        lesson({ id: "present-simple-negative", title: "Present Simple Negative", title_ar: "نفي المضارع البسيط", category: "Tenses", level: "Medium", icon: "➖", short_rule_en: "Use do not or does not + base verb.", explanation_ar: "في النفي نستخدم do not أو does not وبعدها الفعل الأساسي بدون s.", structure: "subject + do/does not + base verb", examples: ["I do not like coffee.", "She does not play tennis.", "They do not watch TV.", "He does not eat fish.", "We do not go late."], examples_ar: ["لا أحب القهوة.", "هي لا تلعب التنس.", "هم لا يشاهدون التلفاز.", "هو لا يأكل السمك.", "نحن لا نذهب متأخرين."], common_mistake: "She does not plays tennis.", correction: "She does not play tennis.", quick_question: "She ____ play tennis.", choices: ["does not", "do not", "is not", "not"], correct_answer: "does not", fill_blank: "I ____ like coffee.", fill_blank_answer: "do not", true_false: "After does not, use the base verb.", true_false_answer: true, sentence_order_words: ["She", "does", "not", "play", "tennis"], sentence_order_answer: "She does not play tennis.", translate_ar: "هي لا تلعب التنس.", translate_answer: "She does not play tennis.", make_question_answer: "Does she play tennis?", tense: "Present Simple" }),
        lesson({ id: "present-simple-questions", title: "Present Simple Questions", title_ar: "أسئلة المضارع البسيط", category: "Questions", level: "Medium", icon: "❔", short_rule_en: "Use Do or Does before the subject.", explanation_ar: "لتكوين سؤال في المضارع البسيط نبدأ بـ Do أو Does.", structure: "Do/Does + subject + base verb?", examples: ["Do you like English?", "Does he play football?", "Do they study math?", "Does she read books?", "Do we need help?"], examples_ar: ["هل تحب الإنجليزية؟", "هل يلعب كرة القدم؟", "هل يدرسون الرياضيات؟", "هل تقرأ الكتب؟", "هل نحتاج مساعدة؟"], common_mistake: "Does he plays football?", correction: "Does he play football?", quick_question: "____ he play football?", choices: ["Does", "Do", "Is", "Are"], correct_answer: "Does", fill_blank: "____ you like English?", fill_blank_answer: "Do", true_false: "Does he play football? is correct.", true_false_answer: true, sentence_order_words: ["Do", "you", "like", "English"], sentence_order_answer: "Do you like English?", translate_ar: "هل تحب الإنجليزية؟", translate_answer: "Do you like English?", make_question_answer: "Do you like English?", tense: "Present Simple" }),
        lesson({ id: "adverbs-frequency", title: "Adverbs of Frequency", title_ar: "ظروف التكرار", category: "Tenses", level: "Medium", icon: "🔁", short_rule_en: "always / usually / often / sometimes / never show how often something happens.", explanation_ar: "توضح ظروف التكرار كم مرة يحدث الفعل.", structure: "subject + frequency adverb + verb", examples: ["I usually wake up early.", "She always studies hard.", "He never drinks coffee.", "They often play football.", "We sometimes eat out."], examples_ar: ["عادة أستيقظ مبكرًا.", "هي دائمًا تدرس بجد.", "هو لا يشرب القهوة أبدًا.", "هم غالبًا يلعبون كرة القدم.", "نحن أحيانًا نأكل خارج البيت."], common_mistake: "I wake up usually early.", correction: "I usually wake up early.", quick_question: "I ____ wake up early.", choices: ["usually", "yesterday", "now", "tomorrow"], correct_answer: "usually", fill_blank: "She ____ studies hard.", fill_blank_answer: "always", true_false: "Never is an adverb of frequency.", true_false_answer: true, sentence_order_words: ["I", "usually", "wake", "up", "early"], sentence_order_answer: "I usually wake up early.", translate_ar: "عادة أستيقظ مبكرًا.", translate_answer: "I usually wake up early.", make_question_answer: "Do you usually wake up early?", tense: "Present Simple" }),
        lesson({ id: "present-continuous", title: "Present Continuous", title_ar: "المضارع المستمر", category: "Tenses", level: "Easy", icon: "▶️", short_rule_en: "Use am/is/are + verb-ing for actions happening now.", explanation_ar: "نستخدمه للتحدث عن شيء يحدث الآن.", structure: "subject + am/is/are + verb-ing", examples: ["They are watching TV.", "I am studying now.", "She is reading a book.", "He is playing football.", "We are learning English."], examples_ar: ["هم يشاهدون التلفاز.", "أنا أدرس الآن.", "هي تقرأ كتابًا.", "هو يلعب كرة القدم.", "نحن نتعلم الإنجليزية."], common_mistake: "They watching TV.", correction: "They are watching TV.", quick_question: "They ____ watching TV.", choices: ["are", "is", "am", "do"], correct_answer: "are", fill_blank: "I ____ studying now.", fill_blank_answer: "am", true_false: "Present continuous uses verb-ing.", true_false_answer: true, sentence_order_words: ["They", "are", "watching", "TV"], sentence_order_answer: "They are watching TV.", translate_ar: "هم يشاهدون التلفاز الآن.", translate_answer: "They are watching TV now.", make_question_answer: "Are they watching TV?", tense: "Present Continuous" }),
        lesson({ id: "present-simple-vs-continuous", title: "Present Simple vs Present Continuous", title_ar: "المضارع البسيط والمستمر", category: "Challenge", level: "Challenge", icon: "⚖️", short_rule_en: "Use present simple for habits and present continuous for now.", explanation_ar: "المضارع البسيط للعادات، والمستمر للأفعال التي تحدث الآن.", structure: "habit: verb / now: am-is-are + ing", examples: ["I study every day.", "I am studying now.", "She plays tennis on Fridays.", "She is playing tennis now.", "They usually walk to school."], examples_ar: ["أدرس كل يوم.", "أنا أدرس الآن.", "هي تلعب التنس أيام الجمعة.", "هي تلعب التنس الآن.", "هم عادة يمشون إلى المدرسة."], common_mistake: "I am study every day.", correction: "I study every day.", quick_question: "I ____ every day.", choices: ["study", "am studying", "studying", "studies"], correct_answer: "study", fill_blank: "I ____ studying now.", fill_blank_answer: "am", true_false: "Now often uses present continuous.", true_false_answer: true, sentence_order_words: ["I", "am", "studying", "now"], sentence_order_answer: "I am studying now.", translate_ar: "أنا أدرس الآن.", translate_answer: "I am studying now.", make_question_answer: "Are you studying now?", tense: "Present Continuous" }),
        lesson({ id: "past-simple-regular", title: "Past Simple Regular Verbs", title_ar: "الماضي البسيط للأفعال المنتظمة", category: "Tenses", level: "Medium", icon: "⏪", short_rule_en: "Add ed to many regular verbs in the past.", explanation_ar: "نضيف ed لكثير من الأفعال المنتظمة في الماضي.", structure: "subject + verb-ed + past time", examples: ["I visited my uncle yesterday.", "She watched a movie.", "They played football.", "We cleaned the room.", "He opened the door."], examples_ar: ["زرت عمي أمس.", "هي شاهدت فيلمًا.", "هم لعبوا كرة القدم.", "نظفنا الغرفة.", "هو فتح الباب."], common_mistake: "I visit my uncle yesterday.", correction: "I visited my uncle yesterday.", quick_question: "I ____ my uncle yesterday.", choices: ["visited", "visit", "visits", "visiting"], correct_answer: "visited", fill_blank: "They ____ football.", fill_blank_answer: "played", true_false: "Visited is a past simple regular verb.", true_false_answer: true, sentence_order_words: ["I", "visited", "my", "uncle", "yesterday"], sentence_order_answer: "I visited my uncle yesterday.", translate_ar: "زرت عمي أمس.", translate_answer: "I visited my uncle yesterday.", make_question_answer: "Did you visit your uncle?", tense: "Past Simple" }),
        lesson({ id: "past-simple-irregular", title: "Past Simple Irregular Verbs", title_ar: "الماضي البسيط للأفعال الشاذة", category: "Tenses", level: "Challenge", icon: "🔄", short_rule_en: "Some verbs change form: go/went, eat/ate, see/saw.", explanation_ar: "بعض الأفعال لا نضيف لها ed بل يتغير شكلها في الماضي.", structure: "subject + irregular past verb", examples: ["I went to school.", "She ate breakfast.", "We saw a bird.", "He wrote a story.", "They came early."], examples_ar: ["ذهبت إلى المدرسة.", "هي أكلت الفطور.", "رأينا طائرًا.", "هو كتب قصة.", "هم حضروا مبكرًا."], common_mistake: "I goed to school.", correction: "I went to school.", quick_question: "I ____ to school.", choices: ["went", "goed", "go", "going"], correct_answer: "went", fill_blank: "She ____ breakfast.", fill_blank_answer: "ate", true_false: "Went is the past of go.", true_false_answer: true, sentence_order_words: ["I", "went", "to", "school"], sentence_order_answer: "I went to school.", translate_ar: "ذهبت إلى المدرسة.", translate_answer: "I went to school.", make_question_answer: "Did you go to school?", tense: "Past Simple" }),
        lesson({ id: "past-simple-negative", title: "Past Simple Negative", title_ar: "نفي الماضي البسيط", category: "Tenses", level: "Medium", icon: "⛔", short_rule_en: "Use did not + base verb.", explanation_ar: "في نفي الماضي نستخدم did not وبعدها الفعل الأساسي.", structure: "subject + did not + base verb", examples: ["I did not watch TV.", "She did not play tennis.", "They did not go home.", "He did not eat lunch.", "We did not finish early."], examples_ar: ["لم أشاهد التلفاز.", "هي لم تلعب التنس.", "هم لم يذهبوا للبيت.", "هو لم يأكل الغداء.", "لم ننته مبكرًا."], common_mistake: "I did not watched TV.", correction: "I did not watch TV.", quick_question: "I did not ____ TV.", choices: ["watch", "watched", "watching", "watches"], correct_answer: "watch", fill_blank: "She did not ____ tennis.", fill_blank_answer: "play", true_false: "After did not, use the base verb.", true_false_answer: true, sentence_order_words: ["I", "did", "not", "watch", "TV"], sentence_order_answer: "I did not watch TV.", translate_ar: "لم أشاهد التلفاز.", translate_answer: "I did not watch TV.", make_question_answer: "Did you watch TV?", tense: "Past Simple" }),
        lesson({ id: "past-simple-questions", title: "Past Simple Questions", title_ar: "أسئلة الماضي البسيط", category: "Questions", level: "Medium", icon: "🕵️", short_rule_en: "Use Did + subject + base verb?", explanation_ar: "نبدأ سؤال الماضي بـ Did وبعدها الفاعل ثم الفعل الأساسي.", structure: "Did + subject + base verb?", examples: ["Did you finish your homework?", "Did she play tennis?", "Did they go to school?", "Did he eat lunch?", "Did we win?"], examples_ar: ["هل أنهيت واجبك؟", "هل لعبت التنس؟", "هل ذهبوا إلى المدرسة؟", "هل أكل الغداء؟", "هل فزنا؟"], common_mistake: "Did you finished your homework?", correction: "Did you finish your homework?", quick_question: "Did you ____ your homework?", choices: ["finish", "finished", "finishing", "finishes"], correct_answer: "finish", fill_blank: "____ she play tennis?", fill_blank_answer: "Did", true_false: "Did you finish? is correct.", true_false_answer: true, sentence_order_words: ["Did", "you", "finish", "homework"], sentence_order_answer: "Did you finish homework?", translate_ar: "هل أنهيت واجبك؟", translate_answer: "Did you finish your homework?", make_question_answer: "Did you finish your homework?", tense: "Past Simple" }),
        lesson({ id: "future-will", title: "Future with Will", title_ar: "المستقبل باستخدام will", category: "Tenses", level: "Medium", icon: "🔮", short_rule_en: "Use will + base verb for future decisions or predictions.", explanation_ar: "نستخدم will للتحدث عن المستقبل والقرارات والتوقعات.", structure: "subject + will + base verb", examples: ["I will study tomorrow.", "She will call you.", "They will arrive soon.", "We will help him.", "He will be happy."], examples_ar: ["سأدرس غدًا.", "هي ستتصل بك.", "سيصلون قريبًا.", "سنساعده.", "سيكون سعيدًا."], common_mistake: "I will studying tomorrow.", correction: "I will study tomorrow.", quick_question: "I will ____ tomorrow.", choices: ["study", "studying", "studies", "studied"], correct_answer: "study", fill_blank: "She will ____ you.", fill_blank_answer: "call", true_false: "After will, use the base verb.", true_false_answer: true, sentence_order_words: ["I", "will", "study", "tomorrow"], sentence_order_answer: "I will study tomorrow.", translate_ar: "سأدرس غدًا.", translate_answer: "I will study tomorrow.", make_question_answer: "Will you study tomorrow?", tense: "Future" }),
        lesson({ id: "future-going-to", title: "Future with Going to", title_ar: "المستقبل باستخدام going to", category: "Tenses", level: "Medium", icon: "🗓️", short_rule_en: "Use am/is/are going to + base verb for plans.", explanation_ar: "نستخدم going to للخطط والنوايا المستقبلية.", structure: "subject + am/is/are going to + verb", examples: ["I am going to visit my friend.", "She is going to study.", "They are going to travel.", "We are going to play.", "He is going to call me."], examples_ar: ["سأزور صديقي.", "هي ستدرس.", "هم سيسافرون.", "سنلعب.", "هو سيتصل بي."], common_mistake: "I going to visit my friend.", correction: "I am going to visit my friend.", quick_question: "I ____ going to visit my friend.", choices: ["am", "is", "are", "do"], correct_answer: "am", fill_blank: "They ____ going to travel.", fill_blank_answer: "are", true_false: "Going to is used for plans.", true_false_answer: true, sentence_order_words: ["I", "am", "going", "to", "visit", "my", "friend"], sentence_order_answer: "I am going to visit my friend.", translate_ar: "سأزور صديقي.", translate_answer: "I am going to visit my friend.", make_question_answer: "Are you going to visit your friend?", tense: "Future" }),
        lesson({ id: "can-cant", title: "Can / Can't", title_ar: "يستطيع / لا يستطيع", category: "Modals", level: "Easy", icon: "💪", short_rule_en: "Use can or can't + base verb for ability.", explanation_ar: "نستخدم can للقدرة و can't لعدم القدرة.", structure: "subject + can/can't + base verb", examples: ["I can swim.", "I can't fly.", "She can speak English.", "He can't drive.", "They can play football."], examples_ar: ["أستطيع السباحة.", "لا أستطيع الطيران.", "هي تستطيع التحدث بالإنجليزية.", "هو لا يستطيع القيادة.", "هم يستطيعون لعب كرة القدم."], common_mistake: "I can to swim.", correction: "I can swim.", quick_question: "I ____ swim.", choices: ["can", "can to", "am can", "cans"], correct_answer: "can", fill_blank: "I ____ fly.", fill_blank_answer: "can't", true_false: "After can, use the base verb.", true_false_answer: true, sentence_order_words: ["I", "can", "swim"], sentence_order_answer: "I can swim.", translate_ar: "أستطيع السباحة.", translate_answer: "I can swim.", make_question_answer: "Can you swim?" }),
        lesson({ id: "must-mustnt", title: "Must / Mustn't", title_ar: "يجب / ممنوع", category: "Modals", level: "Medium", icon: "⚠️", short_rule_en: "Use must for obligation and mustn't for prohibition.", explanation_ar: "نستخدم must لما يجب فعله، و mustn't لما هو ممنوع.", structure: "subject + must/mustn't + base verb", examples: ["You must study.", "You mustn't run in the classroom.", "We must listen.", "Students must be polite.", "You mustn't touch that."], examples_ar: ["يجب أن تدرس.", "يجب ألا تركض في الفصل.", "يجب أن نستمع.", "يجب أن يكون الطلاب مهذبين.", "يجب ألا تلمس ذلك."], common_mistake: "You must to study.", correction: "You must study.", quick_question: "You ____ study.", choices: ["must", "must to", "are must", "musts"], correct_answer: "must", fill_blank: "You ____ run in the classroom.", fill_blank_answer: "mustn't", true_false: "Mustn't means prohibited.", true_false_answer: true, sentence_order_words: ["You", "must", "study"], sentence_order_answer: "You must study.", translate_ar: "يجب أن تدرس.", translate_answer: "You must study.", make_question_answer: "Must I study?" }),
        lesson({ id: "should-shouldnt", title: "Should / Shouldn't", title_ar: "ينبغي / لا ينبغي", category: "Modals", level: "Medium", icon: "💡", short_rule_en: "Use should or shouldn't for advice.", explanation_ar: "نستخدم should للنصيحة و shouldn't للنصيحة بعدم فعل شيء.", structure: "subject + should/shouldn't + base verb", examples: ["You should drink water.", "You shouldn't eat too much candy.", "He should sleep early.", "She should practice.", "We shouldn't be late."], examples_ar: ["ينبغي أن تشرب الماء.", "لا ينبغي أن تأكل حلوى كثيرة.", "ينبغي أن ينام مبكرًا.", "ينبغي أن تتدرب.", "لا ينبغي أن نتأخر."], common_mistake: "You should to drink water.", correction: "You should drink water.", quick_question: "You ____ drink water.", choices: ["should", "should to", "are should", "shoulds"], correct_answer: "should", fill_blank: "You ____ eat too much candy.", fill_blank_answer: "shouldn't", true_false: "Should gives advice.", true_false_answer: true, sentence_order_words: ["You", "should", "drink", "water"], sentence_order_answer: "You should drink water.", translate_ar: "ينبغي أن تشرب الماء.", translate_answer: "You should drink water.", make_question_answer: "Should I drink water?" }),
        lesson({ id: "prepositions-place", title: "Prepositions of Place", title_ar: "حروف جر المكان", category: "Prepositions", level: "Easy", icon: "🧭", short_rule_en: "Use in, on, under, next to, between, behind to show place.", explanation_ar: "نستخدم حروف جر المكان لتحديد موقع الشيء.", structure: "noun + be + preposition + place", examples: ["The cat is under the table.", "The book is on the desk.", "The bag is behind the chair.", "She is next to me.", "The school is between two houses."], examples_ar: ["القطة تحت الطاولة.", "الكتاب على المكتب.", "الحقيبة خلف الكرسي.", "هي بجانبي.", "المدرسة بين بيتين."], common_mistake: "The cat is in the table.", correction: "The cat is under the table.", quick_question: "The cat is ____ the table.", choices: ["under", "happy", "went", "bigger"], correct_answer: "under", fill_blank: "The book is ____ the desk.", fill_blank_answer: "on", true_false: "Under shows place.", true_false_answer: true, sentence_order_words: ["The", "cat", "is", "under", "the", "table"], sentence_order_answer: "The cat is under the table.", translate_ar: "القطة تحت الطاولة.", translate_answer: "The cat is under the table.", make_question_answer: "Where is the cat?" }),
        lesson({ id: "question-words", title: "Question Words", title_ar: "كلمات السؤال", category: "Questions", level: "Easy", icon: "🔎", short_rule_en: "Use what, where, when, who, why, how to ask for information.", explanation_ar: "نستخدم كلمات السؤال للحصول على معلومات محددة.", structure: "question word + auxiliary + subject + verb?", examples: ["Where do you live?", "What is your name?", "When do you study?", "Who is your teacher?", "How are you?"], examples_ar: ["أين تعيش؟", "ما اسمك؟", "متى تدرس؟", "من معلمك؟", "كيف حالك؟"], common_mistake: "Where you live?", correction: "Where do you live?", quick_question: "____ do you live?", choices: ["Where", "Who", "Why", "When"], correct_answer: "Where", fill_blank: "____ is your name?", fill_blank_answer: "What", true_false: "Where asks about place.", true_false_answer: true, sentence_order_words: ["Where", "do", "you", "live"], sentence_order_answer: "Where do you live?", translate_ar: "أين تعيش؟", translate_answer: "Where do you live?", make_question_answer: "Where do you live?" }),
        lesson({ id: "comparative-superlative", title: "Comparative and Superlative", title_ar: "المقارنة والتفضيل", category: "Comparatives", level: "Challenge", icon: "🏆", short_rule_en: "Use -er/more for comparing two; use -est/most for the top one.", explanation_ar: "نستخدم المقارنة بين شيئين، والتفضيل للشيء الأفضل أو الأكبر بين مجموعة.", structure: "adjective-er than / the adjective-est", examples: ["Ali is taller than Omar.", "This is the best book.", "My bag is bigger than yours.", "English is more interesting now.", "She is the most careful student."], examples_ar: ["علي أطول من عمر.", "هذا أفضل كتاب.", "حقيبتي أكبر من حقيبتك.", "الإنجليزية أكثر تشويقًا الآن.", "هي أكثر طالبة حذرًا."], common_mistake: "Ali is more tall than Omar.", correction: "Ali is taller than Omar.", quick_question: "Ali is ____ than Omar.", choices: ["taller", "tallest", "more tall", "the taller"], correct_answer: "taller", fill_blank: "This is the ____ book.", fill_blank_answer: "best", true_false: "The biggest is superlative.", true_false_answer: true, sentence_order_words: ["Ali", "is", "taller", "than", "Omar"], sentence_order_answer: "Ali is taller than Omar.", translate_ar: "علي أطول من عمر.", translate_answer: "Ali is taller than Omar.", make_question_answer: "Who is taller than Omar?" })
    ];

    const els = {};
    let progress = loadGrammarProgress();
    let activeCategory = "";

    function escapeHtml(value) {
        return String(value ?? "").replace(/[&<>"']/g, char => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        }[char]));
    }

    function normalizeText(value) {
        return String(value || "").toLowerCase().replace(/[^a-z0-9\s]/g, "").replace(/\s+/g, " ").trim();
    }

    function shuffle(items) {
        const copy = [...items];
        for (let i = copy.length - 1; i > 0; i -= 1) {
            const j = Math.floor(Math.random() * (i + 1));
            [copy[i], copy[j]] = [copy[j], copy[i]];
        }
        return copy;
    }

    function loadGrammarProgress() {
        const initial = window.GRAMMAR_INITIAL_PROGRESS || {};
        const fallback = {
            points: Number(initial.points || 0),
            actions: Number(initial.actions || 0),
            mastered: [],
            completed: Boolean(initial.completed)
        };
        try {
            return { ...fallback, ...JSON.parse(localStorage.getItem(progressKey) || "{}") };
        } catch {
            return fallback;
        }
    }

    function preferredTheme() {
        try {
            const saved = localStorage.getItem(themeKey);
            if (saved === "dark" || saved === "light") return saved;
        } catch {
            return "light";
        }
        return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }

    function applyTheme(theme) {
        const nextTheme = theme === "dark" ? "dark" : "light";
        document.body.dataset.theme = nextTheme;
        const button = document.getElementById("gfThemeToggle");
        if (button) {
            button.setAttribute("aria-pressed", String(nextTheme === "dark"));
            button.textContent = nextTheme === "dark" ? "الوضع الفاتح" : "الوضع الداكن";
        }
        try {
            localStorage.setItem(themeKey, nextTheme);
        } catch {
            // Theme still works for the current page even if storage is blocked.
        }
    }

    function toggleTheme() {
        applyTheme(document.body.dataset.theme === "dark" ? "light" : "dark");
    }

    function saveGrammarProgress() {
        localStorage.setItem(progressKey, JSON.stringify(progress));
    }

    function csrfToken() {
        return document.cookie.split(";").map(v => v.trim()).find(v => v.startsWith("csrftoken="))?.split("=")[1] || "";
    }

    async function addPoints(activityType, points, options = {}) {
        progress.points = Math.max(0, Number(progress.points || 0) + points);
        progress.actions = Math.max(0, Number(progress.actions || 0) + 1);
        if (options.masteredLesson && !progress.mastered.includes(options.masteredLesson)) {
            progress.mastered.push(options.masteredLesson);
        }
        if (progress.mastered.length >= 5 && !progress.fiveBonus) {
            progress.fiveBonus = true;
            progress.points += 20;
        }
        if (options.completed) progress.completed = true;
        saveGrammarProgress();
        updateGrammarStats();
        // TODO: integrate grammar progress with StudentActivity leaderboard if that model becomes available.
        try {
            const response = await fetch(window.GRAMMAR_PROGRESS_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
                body: JSON.stringify({
                    section: "grammar",
                    activity_type: activityType,
                    points,
                    completed: Boolean(options.completed)
                })
            });
            const data = await response.json();
            if (data.status === "ok") {
                progress.points = data.points;
                progress.actions = data.actions_count;
                progress.completed = data.completed || progress.completed;
                saveGrammarProgress();
                updateGrammarStats();
            }
        } catch {
            updateGrammarStats();
        }
    }

    function statusFor(points) {
        if (progress.completed || points >= 150) return "متقن";
        if (points >= 80) return "ممتاز";
        if (points >= 30) return "جيد";
        return "قيد التدريب";
    }

    function updateGrammarStats() {
        const points = Number(progress.points || 0);
        els.points.textContent = points;
        els.actions.textContent = Number(progress.actions || 0);
        els.status.textContent = statusFor(points);
        els.mastered.textContent = `${progress.mastered.length} / ${grammarData.length}`;
        els.progressFill.style.width = `${Math.min(100, Math.round((points / 150) * 100))}%`;
    }

    function renderCategoryOptions() {
        els.category.innerHTML = `<option value="">كل التصنيفات</option>` + categories.map(category => `<option value="${category}">${category}</option>`).join("");
    }

    function filteredLessons() {
        const query = normalizeText(els.search.value);
        const category = activeCategory || els.category.value;
        const level = els.level.value;
        return grammarData.filter(item => {
            const haystack = normalizeText(`${item.title} ${item.title_ar} ${item.category} ${item.short_rule_en} ${item.explanation_ar}`);
            return (!query || haystack.includes(query)) && (!category || item.category === category) && (!level || item.level === level);
        });
    }

    function renderGrammarCards() {
        const lessons = filteredLessons();
        els.grid.innerHTML = lessons.map(item => {
            const mastered = progress.mastered.includes(item.id);
            return `
                <article class="gf-card" data-lesson="${escapeHtml(item.id)}">
                    <div class="gf-card-top">
                        <div class="gf-icon">${escapeHtml(item.icon)}</div>
                        <div>
                            <div class="gf-badges">
                                <span class="gf-badge">${escapeHtml(item.category)}</span>
                                <span class="gf-badge level">${escapeHtml(item.level)}</span>
                                ${mastered ? `<span class="gf-badge">متقن</span>` : ""}
                            </div>
                            <h2 class="gf-word">${escapeHtml(item.title)}</h2>
                            <div class="gf-arabic">${escapeHtml(item.title_ar)}</div>
                        </div>
                    </div>
                    <div class="gf-rule">${escapeHtml(item.structure)}</div>
                    <div class="gf-explain">${escapeHtml(item.explanation_ar)}</div>
                    <div class="gf-example">${escapeHtml(item.examples[0])}</div>
                    <div class="gf-example-ar">${escapeHtml(item.examples_ar[0])}</div>
                    <div class="gf-mistake">
                        <span>${escapeHtml(item.common_mistake)} ✗</span>
                        <span>${escapeHtml(item.correction)} ✓</span>
                    </div>
                    <div class="gf-actions">
                        <button class="gf-action train" type="button" data-action="open" data-lesson="${escapeHtml(item.id)}">ابدأ</button>
                        <button class="gf-action listen" type="button" data-action="listen" data-lesson="${escapeHtml(item.id)}">استماع</button>
                        <button class="gf-action train" type="button" data-action="training" data-lesson="${escapeHtml(item.id)}">حل تدريب</button>
                        <button class="gf-action mic" type="button" data-action="mic" data-lesson="${escapeHtml(item.id)}">مايك</button>
                        <button class="gf-action gold" type="button" data-action="examples" data-lesson="${escapeHtml(item.id)}">عرض الأمثلة</button>
                        <a class="gf-action review" href="/grammar-foundation/worksheet/" target="_blank">ورقة عمل</a>
                    </div>
                </article>
            `;
        }).join("");
        els.empty.hidden = lessons.length > 0;
    }

    function findLesson(id) {
        return grammarData.find(item => item.id === id);
    }

    function speakText(text, rate = 0.85) {
        try {
            if (!("speechSynthesis" in window)) {
                openModal("<h2 id='gfModalTitle'>النطق غير مدعوم</h2><p>جرّب Google Chrome لتفعيل النطق.</p>");
                return;
            }
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = "en-US";
            utterance.rate = rate;
            window.speechSynthesis.speak(utterance);
        } catch {
            openModal("<h2 id='gfModalTitle'>تعذر النطق</h2><p>لم يتمكن المتصفح من تشغيل الصوت الآن.</p>");
        }
    }

    function speakSlow(text) {
        speakText(text, 0.68);
    }

    function openModal(html) {
        els.modalContent.innerHTML = html;
        els.modal.hidden = false;
    }

    function closeModal() {
        els.modal.hidden = true;
        els.modalContent.innerHTML = "";
    }

    function openGrammarModal(item) {
        openModal(`
            <h2 id="gfModalTitle" class="gf-word">${escapeHtml(item.title)}</h2>
            <p class="gf-arabic">${escapeHtml(item.title_ar)}</p>
            <p class="gf-explain">${escapeHtml(item.explanation_ar)}</p>
            <p class="gf-rule">${escapeHtml(item.short_rule_en)}</p>
            <p class="gf-example">${escapeHtml(item.examples[0])}</p>
            <p class="gf-example-ar">${escapeHtml(item.examples_ar[0])}</p>
            <div class="gf-mistake"><span>${escapeHtml(item.common_mistake)} ✗</span><span>${escapeHtml(item.correction)} ✓</span></div>
            <div class="gf-actions">
                <button class="gf-action listen" type="button" data-modal-speak="${escapeHtml(item.title)}">نطق العنوان</button>
                <button class="gf-action listen" type="button" data-modal-speak="${escapeHtml(item.examples[0])}">نطق المثال</button>
                <button class="gf-action listen" type="button" data-modal-slow="${escapeHtml(item.examples[0])}">قراءة بطيئة</button>
                <button class="gf-action train" type="button" data-modal-training="${escapeHtml(item.id)}">ابدأ التدريب</button>
            </div>
        `);
        addPoints("open", 1);
    }

    function showExamples(item) {
        openModal(`
            <h2 id="gfModalTitle">أمثلة: ${escapeHtml(item.title)}</h2>
            ${item.examples.map((example, index) => `
                <div class="gf-example">${escapeHtml(example)}</div>
                <p class="gf-example-ar">${escapeHtml(item.examples_ar[index])}</p>
                <button class="gf-action listen" type="button" data-modal-speak="${escapeHtml(example)}">استماع</button>
            `).join("")}
        `);
    }

    function startGrammarTraining(item) {
        openModal(`
            <h2 id="gfModalTitle">تدريب: ${escapeHtml(item.title)}</h2>
            <p class="gf-explain">${escapeHtml(item.explanation_ar)}</p>
            <h3>1. Choose the correct answer</h3>
            <p class="gf-example">${escapeHtml(item.quick_question)}</p>
            <div class="gf-options">
                ${item.choices.map(choice => `<button class="gf-option" type="button" data-answer="${escapeHtml(choice)}" data-correct="${escapeHtml(item.correct_answer)}" data-lesson="${escapeHtml(item.id)}">${escapeHtml(choice)}</button>`).join("")}
            </div>
            <h3>2. Fill in the blank</h3>
            <p class="gf-example">${escapeHtml(item.fill_blank)}</p>
            <input id="gfBlankAnswer" type="text" placeholder="اكتب الإجابة">
            <button class="gf-btn primary" type="button" data-check-blank="${escapeHtml(item.id)}">تحقق</button>
            <h3>3. True or False</h3>
            <p class="gf-example">${escapeHtml(item.true_false)}</p>
            <button class="gf-btn" type="button" data-tf="true" data-lesson="${escapeHtml(item.id)}">صح</button>
            <button class="gf-btn" type="button" data-tf="false" data-lesson="${escapeHtml(item.id)}">خطأ</button>
            <h3>4. Sentence Order</h3>
            <p class="gf-example">${escapeHtml(item.sentence_order_words.join(" / "))}</p>
            <input id="gfOrderAnswer" type="text" placeholder="رتب الجملة">
            <button class="gf-btn primary" type="button" data-check-order="${escapeHtml(item.id)}">تحقق</button>
            <h3>5. Correct the mistake</h3>
            <p class="gf-example">${escapeHtml(item.common_mistake)}</p>
            <input id="gfMistakeAnswer" type="text" placeholder="اكتب التصحيح">
            <button class="gf-btn primary" type="button" data-check-mistake="${escapeHtml(item.id)}">تحقق</button>
            <h3>6. Translate to English</h3>
            <p>${escapeHtml(item.translate_ar)}</p>
            <input id="gfTranslateAnswer" type="text" placeholder="Translate">
            <button class="gf-btn primary" type="button" data-check-translate="${escapeHtml(item.id)}">تحقق</button>
            <h3>7. Make a question</h3>
            <p class="gf-example">${escapeHtml(item.examples[0])}</p>
            <input id="gfQuestionAnswer" type="text" placeholder="Make a question">
            <button class="gf-btn primary" type="button" data-check-question="${escapeHtml(item.id)}">تحقق</button>
            <div id="gfTrainingFeedback" class="gf-explain" style="margin-top:12px;"></div>
        `);
    }

    function similarityScore(original, spoken) {
        const a = normalizeText(original);
        const b = normalizeText(spoken);
        if (!a || !b) return 0;
        const aw = a.split(" ");
        const bw = new Set(b.split(" "));
        const hits = aw.filter(word => bw.has(word)).length;
        return Math.round((hits / Math.max(aw.length, 1)) * 100);
    }

    function startMicPractice(item) {
        const target = item.examples[0];
        openModal(`<h2 id="gfModalTitle">تدريب المايك</h2><p class="gf-example">${escapeHtml(target)}</p><div id="gfSpeechResult"></div>`);
        SpeechService.startRecognition({
            targetText: target,
            type: "short_sentence",
            section: "grammar",
            level: item.level || "",
            onStart: () => SpeechService.renderResult("#gfSpeechResult", { expected: target, spoken: SpeechService.messages.listening, score: 0, status: "retry" }),
            onResult: result => {
                SpeechService.renderResult("#gfSpeechResult", result);
                addPoints("mic", 3, { masteredLesson: result.status === "excellent" ? item.id : "" });
                renderGrammarCards();
            },
            onError: result => SpeechService.renderResult("#gfSpeechResult", result)
        });
        return;
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            openModal(`<h2 id="gfModalTitle">تدريب المايك</h2><p>الميكروفون غير مدعوم في هذا المتصفح، جرّب Google Chrome.</p><p class="gf-example">${escapeHtml(item.examples[0])}</p>`);
            return;
        }
        const recognition = new SpeechRecognition();
        recognition.lang = "en-US";
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.onresult = event => {
            const spoken = event.results[0][0].transcript;
            const score = similarityScore(item.examples[0], spoken);
            const label = score >= 85 ? "ممتاز" : score >= 60 ? "جيد" : "حاول مرة أخرى";
            openModal(`<h2 id="gfModalTitle">نتيجة المايك: ${escapeHtml(label)}</h2><p>المثال: <strong>${escapeHtml(item.examples[0])}</strong></p><p>قلت: <strong>${escapeHtml(spoken)}</strong></p><p>نسبة التطابق: <strong>${score}%</strong></p>`);
            addPoints("mic", 3, { masteredLesson: score >= 85 ? item.id : "" });
            renderGrammarCards();
        };
        recognition.onerror = () => openModal(`<h2 id="gfModalTitle">تعذر تشغيل المايك</h2><p>اسمح للمتصفح باستخدام الميكروفون ثم جرّب مرة أخرى.</p><p class="gf-example">${escapeHtml(item.examples[0])}</p>`);
        openModal(`<h2 id="gfModalTitle">استعد للنطق</h2><p>اقرأ المثال بصوت واضح بعد السماح للميكروفون.</p><p class="gf-example">${escapeHtml(item.examples[0])}</p>`);
        recognition.start();
    }

    function exactOrClose(input, expected) {
        return normalizeText(input) === normalizeText(expected);
    }

    function markFeedback(message, success) {
        const feedback = document.getElementById("gfTrainingFeedback");
        if (feedback) feedback.textContent = message;
        if (success) renderGrammarCards();
    }

    function handleTrainingClick(event) {
        const answer = event.target.closest("[data-answer]");
        if (answer) {
            const success = answer.dataset.answer === answer.dataset.correct;
            answer.classList.add(success ? "correct" : "wrong");
            if (success) addPoints("exercise", 5, { masteredLesson: answer.dataset.lesson });
            markFeedback(success ? "إجابة صحيحة +5" : "حاول مرة أخرى.", success);
            return;
        }
        const tf = event.target.closest("[data-tf]");
        if (tf) {
            const item = findLesson(tf.dataset.lesson);
            const success = String(item.true_false_answer) === tf.dataset.tf;
            if (success) addPoints("exercise", 5, { masteredLesson: item.id });
            markFeedback(success ? "صح +5" : "راجع القاعدة مرة أخرى.", success);
            return;
        }
        const blank = event.target.closest("[data-check-blank]");
        if (blank) {
            const item = findLesson(blank.dataset.checkBlank);
            const success = exactOrClose(document.getElementById("gfBlankAnswer").value, item.fill_blank_answer);
            if (success) addPoints("exercise", 5, { masteredLesson: item.id });
            markFeedback(success ? "ممتاز +5" : `الإجابة: ${item.fill_blank_answer}`, success);
            return;
        }
        const order = event.target.closest("[data-check-order]");
        if (order) {
            const item = findLesson(order.dataset.checkOrder);
            const success = exactOrClose(document.getElementById("gfOrderAnswer").value, item.sentence_order_answer);
            if (success) addPoints("exercise", 5, { masteredLesson: item.id });
            markFeedback(success ? "ترتيب صحيح +5" : `الصحيح: ${item.sentence_order_answer}`, success);
            return;
        }
        const mistake = event.target.closest("[data-check-mistake]");
        if (mistake) {
            const item = findLesson(mistake.dataset.checkMistake);
            const success = exactOrClose(document.getElementById("gfMistakeAnswer").value, item.correction);
            if (success) addPoints("exercise", 5, { masteredLesson: item.id });
            markFeedback(success ? "تصحيح ممتاز +5" : `الصحيح: ${item.correction}`, success);
            return;
        }
        const translate = event.target.closest("[data-check-translate]");
        if (translate) {
            const item = findLesson(translate.dataset.checkTranslate);
            const success = exactOrClose(document.getElementById("gfTranslateAnswer").value, item.translate_answer);
            if (success) addPoints("exercise", 5, { masteredLesson: item.id });
            markFeedback(success ? "ترجمة صحيحة +5" : `الإجابة: ${item.translate_answer}`, success);
            return;
        }
        const question = event.target.closest("[data-check-question]");
        if (question) {
            const item = findLesson(question.dataset.checkQuestion);
            const success = exactOrClose(document.getElementById("gfQuestionAnswer").value, item.make_question_answer);
            if (success) addPoints("exercise", 5, { masteredLesson: item.id });
            markFeedback(success ? "سؤال صحيح +5" : `اقتراح: ${item.make_question_answer}`, success);
        }
    }

    function grammarFixGame() {
        const item = grammarData[Math.floor(Math.random() * grammarData.length)];
        els.gamePanel.innerHTML = `<h2>Grammar Fix</h2><p class="gf-example">${escapeHtml(item.common_mistake)}</p><input id="gfGameInput" placeholder="اكتب التصحيح"><button class="gf-btn primary" data-game-check="${item.id}" data-game-kind="fix">تحقق</button><div id="gfGameFeedback"></div>`;
        els.gamePanel.hidden = false;
    }

    function sentenceBuilderGame() {
        const item = grammarData[Math.floor(Math.random() * grammarData.length)];
        els.gamePanel.innerHTML = `<h2>Sentence Builder</h2><p class="gf-example">${shuffle(item.sentence_order_words).map(escapeHtml).join(" / ")}</p><input id="gfGameInput" placeholder="اكتب الجملة مرتبة"><button class="gf-btn primary" data-game-check="${item.id}" data-game-kind="builder">تحقق</button><div id="gfGameFeedback"></div>`;
        els.gamePanel.hidden = false;
    }

    function tenseRaceGame() {
        const item = shuffle(grammarData.filter(row => row.category === "Tenses"))[0];
        const choices = ["Present Simple", "Present Continuous", "Past Simple", "Future"];
        els.gamePanel.innerHTML = `<h2>Tense Race</h2><p class="gf-example">${escapeHtml(item.examples[0])}</p><div class="gf-options">${choices.map(choice => `<button class="gf-option" data-game-answer="${choice}" data-game-correct="${item.tense}">${choice}</button>`).join("")}</div>`;
        els.gamePanel.hidden = false;
    }

    function pronounMatchGame() {
        const item = shuffle(grammarData.filter(row => row.category === "Pronouns"))[0];
        els.gamePanel.innerHTML = `<h2>Pronoun Match</h2><p>${escapeHtml(item.title_ar)}</p><div class="gf-options">${shuffle(grammarData.filter(row => row.category === "Pronouns")).slice(0, 4).map(row => `<button class="gf-option" data-game-answer="${row.title}" data-game-correct="${item.title}">${row.title}</button>`).join("")}</div>`;
        els.gamePanel.hidden = false;
    }

    function verbToBeChallenge() {
        const question = { text: "She ____ happy.", correct: "is", choices: ["am", "is", "are", "be"] };
        els.gamePanel.innerHTML = `<h2>Verb to be Challenge</h2><p class="gf-example">${question.text}</p><div class="gf-options">${question.choices.map(choice => `<button class="gf-option" data-game-answer="${choice}" data-game-correct="${question.correct}">${choice}</button>`).join("")}</div>`;
        els.gamePanel.hidden = false;
    }

    function questionBuilderGame() {
        const item = shuffle(grammarData.filter(row => row.category === "Questions"))[0];
        els.gamePanel.innerHTML = `<h2>Question Builder</h2><p class="gf-example">${shuffle(item.sentence_order_words).join(" / ")}</p><input id="gfGameInput" placeholder="اكتب السؤال"><button class="gf-btn primary" data-game-check="${item.id}" data-game-kind="question">تحقق</button><div id="gfGameFeedback"></div>`;
        els.gamePanel.hidden = false;
    }

    function errorHunterGame() {
        const item = grammarData[Math.floor(Math.random() * grammarData.length)];
        els.gamePanel.innerHTML = `<h2>Error Hunter</h2><p>اكتب الكلمة أو الجزء الخطأ ثم صحح الجملة.</p><p class="gf-example">${escapeHtml(item.common_mistake)}</p><input id="gfGameInput" placeholder="اكتب التصحيح الكامل"><button class="gf-btn primary" data-game-check="${item.id}" data-game-kind="fix">تحقق</button><div id="gfGameFeedback"></div>`;
        els.gamePanel.hidden = false;
    }

    function grammarSpeedChallenge() {
        const item = grammarData[Math.floor(Math.random() * grammarData.length)];
        els.gamePanel.innerHTML = `<h2>Grammar Speed Challenge</h2><p>تحدي 60 ثانية: اختر الإجابة بسرعة.</p><p class="gf-example">${escapeHtml(item.quick_question)}</p><div class="gf-options">${item.choices.map(choice => `<button class="gf-option" data-game-answer="${choice}" data-game-correct="${item.correct_answer}">${choice}</button>`).join("")}</div>`;
        els.gamePanel.hidden = false;
    }

    function renderGame(game) {
        if (game === "fix") grammarFixGame();
        if (game === "builder") sentenceBuilderGame();
        if (game === "tense") tenseRaceGame();
        if (game === "pronoun") pronounMatchGame();
        if (game === "be") verbToBeChallenge();
        if (game === "question") questionBuilderGame();
        if (game === "hunter") errorHunterGame();
        if (game === "speed") grammarSpeedChallenge();
    }

    function handleGameClick(event) {
        const answer = event.target.closest("[data-game-answer]");
        if (answer) {
            const success = answer.dataset.gameAnswer === answer.dataset.gameCorrect;
            answer.classList.add(success ? "correct" : "wrong");
            if (success) addPoints("game", 7);
            return;
        }
        const check = event.target.closest("[data-game-check]");
        if (!check) return;
        const item = findLesson(check.dataset.gameCheck);
        const value = document.getElementById("gfGameInput").value;
        const expected = check.dataset.gameKind === "builder" || check.dataset.gameKind === "question" ? item.sentence_order_answer : item.correction;
        const success = exactOrClose(value, expected);
        document.getElementById("gfGameFeedback").textContent = success ? "إجابة صحيحة +7" : `الصحيح: ${expected}`;
        if (success) addPoints("game", 7);
    }

    function handleCardAction(action, item) {
        if (!item) return;
        if (action === "open") openGrammarModal(item);
        if (action === "listen") {
            speakText(item.title);
            setTimeout(() => speakText(item.examples[0]), 700);
            addPoints("listen", 1);
        }
        if (action === "training") startGrammarTraining(item);
        if (action === "mic") startMicPractice(item);
        if (action === "examples") showExamples(item);
    }

    function handleModalClick(event) {
        const speak = event.target.closest("[data-modal-speak]");
        if (speak) {
            speakText(speak.dataset.modalSpeak);
            addPoints("listen", 1);
            return;
        }
        const slow = event.target.closest("[data-modal-slow]");
        if (slow) {
            speakSlow(slow.dataset.modalSlow);
            addPoints("listen", 1);
            return;
        }
        const training = event.target.closest("[data-modal-training]");
        if (training) {
            startGrammarTraining(findLesson(training.dataset.modalTraining));
            return;
        }
        handleTrainingClick(event);
    }

    function bindEvents() {
        els.search.addEventListener("input", renderGrammarCards);
        els.category.addEventListener("change", () => {
            activeCategory = "";
            renderGrammarCards();
        });
        els.level.addEventListener("change", renderGrammarCards);
        document.querySelectorAll("[data-filter-category]").forEach(button => {
            button.addEventListener("click", () => {
                activeCategory = button.dataset.filterCategory;
                els.category.value = activeCategory;
                renderGrammarCards();
            });
        });
        document.querySelectorAll("[data-filter-level]").forEach(button => {
            button.addEventListener("click", () => {
                els.level.value = button.dataset.filterLevel;
                renderGrammarCards();
            });
        });
        els.grid.addEventListener("click", event => {
            const button = event.target.closest("[data-action]");
            if (!button) return;
            handleCardAction(button.dataset.action, findLesson(button.dataset.lesson));
        });
        els.modal.addEventListener("click", event => {
            if (event.target === els.modal) closeModal();
            handleModalClick(event);
        });
        document.getElementById("gfModalClose").addEventListener("click", closeModal);
        document.querySelectorAll("[data-game]").forEach(button => {
            button.addEventListener("click", () => renderGame(button.dataset.game));
        });
        els.gamePanel.addEventListener("click", handleGameClick);
        document.getElementById("gfCompleteSection").addEventListener("click", () => {
            addPoints("complete", 50, { completed: true });
        });
        document.getElementById("gfThemeToggle")?.addEventListener("click", toggleTheme);
    }

    document.addEventListener("DOMContentLoaded", () => {
        applyTheme(preferredTheme());
        els.grid = document.getElementById("gfGrid");
        els.empty = document.getElementById("gfEmpty");
        els.search = document.getElementById("gfSearch");
        els.category = document.getElementById("gfCategory");
        els.level = document.getElementById("gfLevel");
        els.points = document.getElementById("gfPoints");
        els.actions = document.getElementById("gfActions");
        els.status = document.getElementById("gfStatus");
        els.mastered = document.getElementById("gfMastered");
        els.progressFill = document.getElementById("gfProgressFill");
        els.modal = document.getElementById("gfModal");
        els.modalContent = document.getElementById("gfModalContent");
        els.gamePanel = document.getElementById("gfGamePanel");
        renderCategoryOptions();
        updateGrammarStats();
        renderGrammarCards();
        bindEvents();
    });
})();
