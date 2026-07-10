const levelFourSections = {
    reading: {
        title: "Reading Passages",
        ar: "قطع القراءة",
        items: ["My School Day", "My Favorite Hobby", "A Trip to Jazan", "Healthy Food"],
        note: "Sprint Level 4.1 is active: choose a passage, read it, answer questions, use the microphone, or try the speed test.",
        points: 1,
    },
    listening: {
        title: "Listening Practice",
        ar: "تدريبات الاستماع",
        items: ["School Morning", "At the Airport", "Listen and fill the missing word", "اختبار الاستماع السريع"],
        note: "Sprint Level 4.2 is active: listen, answer, review, and try the quick listening quiz.",
        points: 1,
    },
    speaking: {
        title: "Speaking Missions",
        ar: "مهام التحدث",
        items: ["Introduce Yourself", "Talk About Your School", "Speaking Challenge", "Role Play Mini"],
        note: "Sprint Level 4.3 is active: open a mission, listen to the model, speak with the microphone, and get feedback.",
        points: 1,
    },
    writing: {
        title: "Writing Practice",
        ar: "تدريب الكتابة",
        items: ["Write About Yourself", "Write About Your School", "Writing Challenge", "مساعد بناء الجملة"],
        note: "Sprint Level 4.4 is active: write, count words and sentences, evaluate, save attempts, and build sentences.",
        points: 1,
    },
    stories: {
        title: "Story Mode",
        ar: "القصص القصيرة",
        items: ["The Lost Bag", "The Helpful Friend", "تحدي القصص", "اكتب نهاية مختلفة"],
        note: "Sprint Level 4.5 is active: read stories, answer questions, order events, practice with the microphone, and write a different ending.",
        points: 1,
    },
    exam: {
        title: "Level 4 Exam",
        ar: "اختبار المستوى الرابع",
        items: ["Vocabulary + Grammar", "Reading + Listening", "Speaking + Writing", "Certificate"],
        note: "Sprint Level 4.6 is active: start the comprehensive exam, review your score, and print the certificate when you reach 80% or more.",
        points: 1,
    },
};

const LEVEL_FOUR_THEME_KEY = "level_four_theme";

function getSavedLevelFourTheme() {
    try {
        return localStorage.getItem(LEVEL_FOUR_THEME_KEY) === "dark" ? "dark" : "light";
    } catch {
        return "light";
    }
}

function applyLevelFourTheme(theme) {
    const safeTheme = theme === "dark" ? "dark" : "light";
    document.body.classList.toggle("dark", safeTheme === "dark");
    document.body.dataset.theme = safeTheme;
    updateLevelFourThemeButton(safeTheme);
}

function updateLevelFourThemeButton(theme = getSavedLevelFourTheme()) {
    const button = document.querySelector("[data-level-four-theme-toggle]");
    if (!button) return;
    const isDark = theme === "dark";
    button.textContent = isDark ? "☀️ الوضع النهاري" : "🌙 الوضع الليلي";
    button.setAttribute("aria-pressed", String(isDark));
}

function toggleLevelFourTheme() {
    const nextTheme = getSavedLevelFourTheme() === "dark" ? "light" : "dark";
    try {
        localStorage.setItem(LEVEL_FOUR_THEME_KEY, nextTheme);
    } catch {
        // Theme still changes for the current page if storage is unavailable.
    }
    applyLevelFourTheme(nextTheme);
}

function initLevelFourTheme() {
    applyLevelFourTheme(getSavedLevelFourTheme());
}

const readingPassages = [
    passage("school-day", "My School Day", "يومي الدراسي", "School", "Easy", "SD",
        "Every morning, I wake up at six o'clock and get ready for school. I eat breakfast with my family, then I put my books in my bag. At school, I study English, math, science, and Arabic. My favorite lesson is English because I like reading short stories and learning new words. During the break, I talk with my friends and eat a small snack. After school, I do my homework and prepare my books for the next day. A good school day helps me learn, meet friends, and become more responsible.",
        "كل صباح أستيقظ الساعة السادسة وأستعد للمدرسة. أتناول الإفطار مع عائلتي ثم أضع كتبي في الحقيبة. في المدرسة أدرس الإنجليزية والرياضيات والعلوم والعربية. مادتي المفضلة هي الإنجليزية لأنني أحب قراءة القصص القصيرة وتعلم كلمات جديدة. أثناء الفسحة أتحدث مع أصدقائي وأتناول وجبة خفيفة. بعد المدرسة أحل واجباتي وأجهز كتبي لليوم التالي.",
        ["wake up", "breakfast", "school", "favorite", "break", "homework", "responsible"],
        "Talk about your school day in four sentences.",
        ["I wake up at six o'clock.", "I eat breakfast with my family.", "I study English at school.", "I prepare my books for the next day."]),
    passage("favorite-hobby", "My Favorite Hobby", "هوايتي المفضلة", "Daily Life", "Easy", "HB",
        "My favorite hobby is drawing. I started drawing when I was young, and now I draw almost every week. I like drawing animals, houses, and places from my city. Drawing helps me relax after school and makes me notice small details around me. Sometimes I use colored pencils, and sometimes I use a tablet. My family encourages me and keeps my best drawings in a folder. In the future, I want to improve my hobby and learn how to design posters and simple stories with pictures.",
        "هوايتي المفضلة هي الرسم. بدأت الرسم عندما كنت صغيرا، والآن أرسم تقريبا كل أسبوع. أحب رسم الحيوانات والبيوت والأماكن من مدينتي. يساعدني الرسم على الاسترخاء بعد المدرسة ويجعلني ألاحظ التفاصيل الصغيرة حولي. أحيانا أستخدم أقلاما ملونة وأحيانا أستخدم جهازا لوحيا. عائلتي تشجعني وتحتفظ بأفضل رسوماتي.",
        ["hobby", "drawing", "relax", "details", "colored pencils", "tablet", "encourages"],
        "Describe your favorite hobby and why you like it.",
        ["I started drawing when I was young.", "Drawing helps me relax.", "My family encourages me.", "I want to improve my hobby."]),
    passage("trip-jazan", "A Trip to Jazan", "رحلة إلى جازان", "Travel", "Medium", "JZ",
        "Last weekend, my family and I took a trip to Jazan. We left early in the morning because we wanted to enjoy the cool weather. On the way, I saw mountains, farms, and beautiful trees. When we arrived, we visited the sea and walked near the water. My father bought fresh fruit, and my mother took photos of the view. I learned that Jazan is famous for its nature, islands, and kind people. The trip was short, but it gave me happy memories and made me proud of my country.",
        "في نهاية الأسبوع الماضي ذهبت أنا وعائلتي في رحلة إلى جازان. غادرنا مبكرا لأننا أردنا الاستمتاع بالجو الجميل. في الطريق رأيت الجبال والمزارع والأشجار الجميلة. عندما وصلنا زرنا البحر ومشينا قرب الماء. اشترى والدي فاكهة طازجة، والتقطت والدتي صورا للمنظر. تعلمت أن جازان مشهورة بطبيعتها وجزرها وناسها الطيبين.",
        ["trip", "weekend", "weather", "mountains", "fresh fruit", "islands", "memories"],
        "Talk about a place you visited in Saudi Arabia.",
        ["We left early in the morning.", "I saw mountains and farms.", "We visited the sea.", "The trip gave me happy memories."]),
    passage("healthy-food", "Healthy Food", "الغذاء الصحي", "Health", "Easy", "HF",
        "Healthy food gives our bodies energy and helps us grow well. I try to eat fruit, vegetables, rice, eggs, fish, and milk. My mother says that breakfast is important because it helps me think clearly at school. I also drink water during the day and avoid too many sweets. Healthy food does not mean we cannot enjoy meals; it means we choose food that helps our body every day. When I eat well, I feel active, focused, and ready to learn.",
        "الغذاء الصحي يعطي أجسامنا الطاقة ويساعدنا على النمو بشكل جيد. أحاول أن آكل الفواكه والخضار والأرز والبيض والسمك والحليب. تقول أمي إن الإفطار مهم لأنه يساعدني على التفكير بوضوح في المدرسة. أشرب الماء خلال اليوم وأتجنب الكثير من الحلويات. الغذاء الصحي لا يعني أننا لا نستمتع بالطعام، بل يعني اختيار طعام يساعد أجسامنا.",
        ["healthy", "energy", "vegetables", "breakfast", "avoid", "active", "focused"],
        "Explain three healthy habits you can do every day.",
        ["Healthy food gives us energy.", "Breakfast helps me think clearly.", "I drink water during the day.", "I feel active when I eat well."]),
    passage("airport", "At the Airport", "في المطار", "Travel", "Medium", "AP",
        "At the airport, people travel to different cities and countries. When my uncle traveled, we went with him to say goodbye. First, he checked his ticket and passport. Then he put his bag on the scale. The airport was busy, but the workers were helpful and organized. I saw screens with flight times and gates. Before my uncle entered the gate, he smiled and told us he would call when he arrived. Airports can feel exciting because every traveler has a story and a destination.",
        "في المطار يسافر الناس إلى مدن ودول مختلفة. عندما سافر عمي ذهبنا معه لنودعه. أولا فحص تذكرته وجوازه، ثم وضع حقيبته على الميزان. كان المطار مزدحما، لكن العاملين كانوا متعاونين ومنظمين. رأيت شاشات تعرض أوقات الرحلات والبوابات. قبل أن يدخل عمي البوابة ابتسم وقال إنه سيتصل عندما يصل.",
        ["airport", "ticket", "passport", "scale", "workers", "flight", "destination"],
        "Describe what people do at the airport.",
        ["People travel to different places.", "He checked his ticket and passport.", "The workers were helpful.", "Every traveler has a destination."]),
    passage("future-job", "My Future Job", "وظيفتي المستقبلية", "Future", "Medium", "FJ",
        "When I think about my future job, I imagine myself helping people. I may become a teacher, doctor, engineer, or computer programmer. Each job needs hard work, patience, and good communication. I know that English can help me learn from books, videos, and people around the world. To prepare for my future, I study every day and ask questions when I do not understand. A future job is not only about money; it is also about serving others and using our talents well.",
        "عندما أفكر في وظيفتي المستقبلية أتخيل نفسي أساعد الناس. قد أصبح معلما أو طبيبا أو مهندسا أو مبرمج حاسوب. كل وظيفة تحتاج إلى عمل جاد وصبر وتواصل جيد. أعرف أن الإنجليزية تساعدني على التعلم من الكتب والفيديوهات والناس حول العالم. للاستعداد لمستقبلي أدرس كل يوم وأسأل عندما لا أفهم.",
        ["future", "teacher", "engineer", "programmer", "patience", "communication", "talents"],
        "Talk about a job you may choose in the future.",
        ["I imagine myself helping people.", "Each job needs hard work.", "English can help me learn.", "A job is about serving others."]),
    passage("good-friend", "A Good Friend", "الصديق الجيد", "Values", "Easy", "GF",
        "A good friend is someone who respects you and helps you become better. My friend listens when I speak and tells the truth kindly. We study together before tests and share useful ideas. When I feel sad, my friend reminds me to be patient and hopeful. Good friends do not laugh at mistakes; they help each other learn from them. I try to be a good friend too by being honest, polite, and helpful. Friendship makes school and life happier.",
        "الصديق الجيد هو الشخص الذي يحترمك ويساعدك لتصبح أفضل. صديقي يستمع عندما أتكلم ويقول الحقيقة بلطف. ندرس معا قبل الاختبارات ونتبادل الأفكار المفيدة. عندما أشعر بالحزن يذكرني صديقي بالصبر والأمل. الأصدقاء الجيدون لا يسخرون من الأخطاء، بل يساعدون بعضهم على التعلم منها.",
        ["friend", "respects", "truth", "patient", "hopeful", "honest", "friendship"],
        "Describe the qualities of a good friend.",
        ["A good friend respects you.", "We study together before tests.", "Good friends help each other.", "Friendship makes life happier."]),
    passage("doctor-visit", "A Visit to the Doctor", "زيارة الطبيب", "Health", "Medium", "DR",
        "One day, I had a sore throat and felt tired. My mother took me to the doctor after school. The doctor asked me questions, checked my temperature, and listened to my breathing. He said I needed rest, warm drinks, and medicine. He also told me to wash my hands and sleep early. I was nervous at first, but the doctor spoke kindly and explained everything clearly and carefully to me. After two days, I felt much better and returned to school.",
        "في يوم من الأيام كان حلقي يؤلمني وشعرت بالتعب. أخذتني أمي إلى الطبيب بعد المدرسة. سألني الطبيب أسئلة، وقاس حرارتي، واستمع إلى تنفسي. قال إنني أحتاج إلى الراحة والمشروبات الدافئة والدواء. أخبرني أيضا أن أغسل يدي وأنام مبكرا. كنت قلقا في البداية، لكن الطبيب تكلم بلطف وشرح كل شيء بوضوح.",
        ["sore throat", "temperature", "breathing", "rest", "medicine", "nervous", "clearly"],
        "Explain what happened when you visited a doctor.",
        ["I had a sore throat.", "The doctor checked my temperature.", "I needed rest and medicine.", "After two days, I felt better."]),
    passage("technology-life", "Technology in Our Life", "التقنية في حياتنا", "Technology", "Challenge", "TL",
        "Technology is part of our daily life. We use phones, tablets, and computers to study, communicate, and solve problems. In school, technology can help students watch lessons, search for information, and practice English. However, we must use it wisely. Spending too much time on screens can make us tired and less active. I think technology is useful when it has a clear purpose. We should use it to learn, create, connect with others, and stay safe online. Parents and teachers can guide us.",
        "التقنية جزء من حياتنا اليومية. نستخدم الهواتف والأجهزة اللوحية والحواسيب للدراسة والتواصل وحل المشكلات. في المدرسة تساعد التقنية الطلاب على مشاهدة الدروس والبحث عن المعلومات وممارسة الإنجليزية. لكن يجب أن نستخدمها بحكمة. قضاء وقت طويل أمام الشاشات قد يجعلنا متعبين وأقل نشاطا.",
        ["technology", "communicate", "solve", "information", "wisely", "screens", "purpose"],
        "Give advice about using technology wisely.",
        ["Technology is part of daily life.", "It can help students practice English.", "We must use it wisely.", "Technology should have a clear purpose."]),
    passage("saving-water", "Saving Water", "توفير الماء", "Environment", "Medium", "SW",
        "Water is a great blessing, and we should not waste it. At home, I turn off the tap while brushing my teeth. My family fixes leaks quickly and uses water carefully when washing the car or cleaning the yard. In school, teachers remind us that saving water protects the environment and helps other people. Small actions can make a big difference when many people do them. I believe every student can help by using only the water they truly need.",
        "الماء نعمة عظيمة ولا ينبغي أن نهدره. في البيت أغلق الصنبور أثناء تنظيف أسناني. تصلح عائلتي التسريبات بسرعة وتستخدم الماء بعناية عند غسل السيارة أو تنظيف الفناء. في المدرسة يذكرنا المعلمون أن توفير الماء يحمي البيئة ويساعد الآخرين. الأعمال الصغيرة تصنع فرقا كبيرا عندما يفعلها كثير من الناس.",
        ["water", "blessing", "waste", "tap", "leaks", "environment", "difference"],
        "Tell your classmates how they can save water.",
        ["We should not waste water.", "I turn off the tap.", "Saving water protects the environment.", "Small actions make a difference."]),
    passage("football-match", "A Football Match", "مباراة كرة قدم", "Sports", "Easy", "FM",
        "Yesterday, our class played a football match after school. The weather was nice, and many students came to watch. I played with my team as a defender. At first, the other team scored a goal, but we did not give up. We passed the ball carefully and encouraged each other. Near the end, my friend scored a goal and the match ended in a draw. I learned that teamwork, respect, and practice are more important than winning in every game.",
        "أمس لعب فصلنا مباراة كرة قدم بعد المدرسة. كان الجو جميلا وجاء كثير من الطلاب للمشاهدة. لعبت مع فريقي كمدافع. في البداية سجل الفريق الآخر هدفا، لكننا لم نستسلم. مررنا الكرة بعناية وشجعنا بعضنا. قرب النهاية سجل صديقي هدفا وانتهت المباراة بالتعادل.",
        ["football", "defender", "scored", "goal", "teamwork", "respect", "winning"],
        "Talk about a sport match you watched or played.",
        ["Our class played a football match.", "I played as a defender.", "We encouraged each other.", "Teamwork is important."]),
    passage("helping-family", "Helping My Family", "مساعدة عائلتي", "Family", "Easy", "HF2",
        "Helping my family makes our home more comfortable. I help by cleaning my room, setting the table, and carrying light bags from the car. On weekends, I sometimes help my father wash the yard and help my mother organize the kitchen. These jobs may look small, but they show respect and responsibility. When everyone helps, the work becomes easier and the family feels closer. I feel proud when my parents thank me for helping at home each week and doing my part.",
        "مساعدة عائلتي تجعل بيتنا أكثر راحة. أساعد بتنظيف غرفتي وترتيب الطاولة وحمل الأكياس الخفيفة من السيارة. في نهاية الأسبوع أساعد والدي أحيانا في غسل الفناء وأساعد والدتي في ترتيب المطبخ. قد تبدو هذه الأعمال صغيرة لكنها تظهر الاحترام والمسؤولية.",
        ["family", "comfortable", "setting the table", "organize", "respect", "responsibility", "proud"],
        "Describe how you help your family at home.",
        ["Helping makes home comfortable.", "I clean my room.", "Small jobs show responsibility.", "I feel proud when I help."]),
];

const listeningPracticeData = [
    {
        id: "school-morning",
        title_en: "School Morning",
        title_ar: "صباح المدرسة",
        category: "School",
        level: "Easy",
        emoji: "🎧",
        audio_text: "Good morning. Are you ready for class?",
        audio_text_ar: "صباح الخير. هل أنت مستعد للحصة؟",
        question_type: "choice",
        question_ar: "اختر الترجمة الصحيحة للجملة التي سمعتها.",
        choices: ["صباح الخير. هل أنت مستعد للحصة؟", "تصبح على خير. هل أنت في البيت؟", "أين حقيبتك المدرسية؟"],
        correct_answer: "صباح الخير. هل أنت مستعد للحصة؟",
        explanation_ar: "الجملة تسأل عن الاستعداد للحصة في الصباح.",
        points: 10,
    },
    {
        id: "homework",
        title_en: "Homework",
        title_ar: "الواجب المنزلي",
        category: "School",
        level: "Easy",
        emoji: "🎧",
        audio_text: "I finished my homework yesterday.",
        audio_text_ar: "أنهيت واجبي أمس.",
        question_type: "true_false",
        question_ar: "صح أو خطأ: المتحدث أنهى واجبه أمس.",
        choices: ["True", "False"],
        correct_answer: "True",
        explanation_ar: "كلمة finished تعني أن العمل انتهى، وyesterday تعني أمس.",
        points: 10,
    },
    {
        id: "airport-listening",
        title_en: "At the Airport",
        title_ar: "في المطار",
        category: "Travel",
        level: "Medium",
        emoji: "🎧",
        audio_text: "I have a ticket and a small suitcase.",
        audio_text_ar: "لدي تذكرة وحقيبة صغيرة.",
        question_type: "choice",
        question_ar: "اختر المعنى الصحيح للجملة.",
        choices: ["لدي تذكرة وحقيبة صغيرة.", "أحتاج إلى طبيب الآن.", "أريد قميصا أزرق."],
        correct_answer: "لدي تذكرة وحقيبة صغيرة.",
        explanation_ar: "ticket تعني تذكرة، وsuitcase تعني حقيبة سفر.",
        points: 10,
    },
    {
        id: "healthy-food-listening",
        title_en: "Healthy Food",
        title_ar: "الغذاء الصحي",
        category: "Health",
        level: "Easy",
        emoji: "🎧",
        audio_text: "Fruits and vegetables are healthy food.",
        audio_text_ar: "الفواكه والخضروات طعام صحي.",
        question_type: "fill_blank",
        question_ar: "أكمل الكلمة الناقصة: Fruits and vegetables are ______ food.",
        choices: [],
        correct_answer: "healthy",
        explanation_ar: "الكلمة الناقصة هي healthy ومعناها صحي.",
        points: 10,
    },
    {
        id: "asking-help",
        title_en: "Asking for Help",
        title_ar: "طلب المساعدة",
        category: "Conversation",
        level: "Easy",
        emoji: "🎧",
        audio_text: "Can you help me, please?",
        audio_text_ar: "هل يمكنك مساعدتي من فضلك؟",
        question_type: "reply",
        question_ar: "اختر الرد المناسب.",
        choices: ["Sure, I can help you.", "It is sunny today.", "I have a red bag."],
        correct_answer: "Sure, I can help you.",
        explanation_ar: "عند طلب المساعدة يكون الرد المناسب: بالتأكيد أستطيع مساعدتك.",
        points: 10,
    },
    {
        id: "daily-routine",
        title_en: "Daily Routine",
        title_ar: "الروتين اليومي",
        category: "Daily Life",
        level: "Medium",
        emoji: "🎧",
        audio_text: "I usually wake up early and go to school by bus.",
        audio_text_ar: "عادة أستيقظ مبكرا وأذهب إلى المدرسة بالحافلة.",
        question_type: "choice",
        question_ar: "اختر المعنى الصحيح للجملة.",
        choices: ["يستيقظ مبكرا ويذهب للمدرسة بالحافلة.", "يلعب كرة القدم بعد المدرسة.", "يسافر بالطائرة إلى مدينة أخرى."],
        correct_answer: "يستيقظ مبكرا ويذهب للمدرسة بالحافلة.",
        explanation_ar: "wake up early تعني يستيقظ مبكرا، وby bus تعني بالحافلة.",
        points: 10,
    },
    {
        id: "market",
        title_en: "At the Market",
        title_ar: "في السوق",
        category: "Shopping",
        level: "Medium",
        emoji: "🎧",
        audio_text: "How much is this blue shirt?",
        audio_text_ar: "كم سعر هذا القميص الأزرق؟",
        question_type: "choice",
        question_ar: "اختر الترجمة الصحيحة.",
        choices: ["كم سعر هذا القميص الأزرق؟", "أين المدرسة الجديدة؟", "هل تريد ماء باردا؟"],
        correct_answer: "كم سعر هذا القميص الأزرق؟",
        explanation_ar: "How much تسأل عن السعر، وblue shirt تعني قميص أزرق.",
        points: 10,
    },
    {
        id: "hospital",
        title_en: "At the Hospital",
        title_ar: "في المستشفى",
        category: "Health",
        level: "Medium",
        emoji: "🎧",
        audio_text: "I have a headache and I need a doctor.",
        audio_text_ar: "لدي صداع وأحتاج إلى طبيب.",
        question_type: "true_false",
        question_ar: "صح أو خطأ: المتحدث يحتاج إلى طبيب.",
        choices: ["True", "False"],
        correct_answer: "True",
        explanation_ar: "الجملة تقول: I need a doctor أي أحتاج إلى طبيب.",
        points: 10,
    },
    {
        id: "weather",
        title_en: "Weather",
        title_ar: "الطقس",
        category: "Daily Life",
        level: "Easy",
        emoji: "🎧",
        audio_text: "The weather is sunny today.",
        audio_text_ar: "الطقس مشمس اليوم.",
        question_type: "fill_blank",
        question_ar: "أكمل الكلمة الناقصة: The weather is ______ today.",
        choices: [],
        correct_answer: "sunny",
        explanation_ar: "الكلمة الناقصة هي sunny وتعني مشمس.",
        points: 10,
    },
    {
        id: "future-dream",
        title_en: "Future Dream",
        title_ar: "حلم المستقبل",
        category: "Future",
        level: "Medium",
        emoji: "🎧",
        audio_text: "I want to be an engineer in the future.",
        audio_text_ar: "أريد أن أصبح مهندسا في المستقبل.",
        question_type: "choice",
        question_ar: "اختر المعنى الصحيح.",
        choices: ["يريد أن يصبح مهندسا في المستقبل.", "يريد شراء حقيبة صغيرة.", "يريد لعب كرة القدم الآن."],
        correct_answer: "يريد أن يصبح مهندسا في المستقبل.",
        explanation_ar: "engineer تعني مهندس، وfuture تعني المستقبل.",
        points: 10,
    },
    {
        id: "directions",
        title_en: "Directions",
        title_ar: "الاتجاهات",
        category: "Directions",
        level: "Challenge",
        emoji: "🎧",
        audio_text: "Go straight and turn left.",
        audio_text_ar: "اذهب إلى الأمام ثم انعطف يسارا.",
        question_type: "order",
        question_ar: "رتب الاتجاهات حسب ما سمعت.",
        choices: ["Go straight", "Turn left", "Stop here"],
        correct_answer: "Go straight|Turn left",
        explanation_ar: "الترتيب الصحيح هو: اذهب للأمام ثم انعطف يسارا.",
        points: 10,
    },
    {
        id: "sports",
        title_en: "Sports",
        title_ar: "الرياضة",
        category: "Sports",
        level: "Easy",
        emoji: "🎧",
        audio_text: "Our team won the football match.",
        audio_text_ar: "فاز فريقنا بمباراة كرة القدم.",
        question_type: "true_false",
        question_ar: "صح أو خطأ: فريق المتحدث فاز بالمباراة.",
        choices: ["True", "False"],
        correct_answer: "True",
        explanation_ar: "won تعني فاز، والجملة تقول إن الفريق فاز بمباراة كرة القدم.",
        points: 10,
    },
];

const speakingMissionsData = [
    speakingMission("introduce-yourself", "Introduce Yourself", "عرّف بنفسك", "Personal", "Easy", "🎙️",
        "Introduce yourself in English.", "عرّف بنفسك باللغة الإنجليزية.",
        ["name", "age", "student", "school", "like"],
        ["My name is...", "I am ... years old.", "I am a student.", "I like..."],
        "My name is Ahmed. I am twelve years old. I am a student. I like English and football.",
        "اسمي أحمد. عمري اثنا عشر عاما. أنا طالب. أحب الإنجليزية وكرة القدم.",
        ["name", "student", "like"], 12, 30, 15),
    speakingMission("talk-school", "Talk About Your School", "تحدث عن مدرستك", "School", "Easy", "🎙️",
        "Talk about your school and what you do there.", "تحدث عن مدرستك وما تفعل فيها.",
        ["school", "class", "teacher", "friends", "learn"],
        ["My school is...", "I study...", "My teachers are...", "I learn..."],
        "My school is big and clean. I study English, math, science, and Arabic. My teachers are kind. I learn with my friends every day.",
        "مدرستي كبيرة ونظيفة. أدرس الإنجليزية والرياضيات والعلوم والعربية. معلموّي لطفاء. أتعلم مع أصدقائي كل يوم.",
        ["school", "study", "teachers", "learn"], 16, 40, 15),
    speakingMission("talk-hobby", "Talk About Your Hobby", "تحدث عن هوايتك", "Daily Life", "Easy", "🎙️",
        "Talk about your favorite hobby and why you like it.", "تحدث عن هوايتك المفضلة ولماذا تحبها.",
        ["hobby", "draw", "play", "read", "enjoy"],
        ["My favorite hobby is...", "I like it because...", "I do it...", "It helps me..."],
        "My favorite hobby is drawing. I like it because it helps me relax. I draw animals and places. I practice my hobby on weekends.",
        "هوايتي المفضلة هي الرسم. أحبها لأنها تساعدني على الاسترخاء. أرسم الحيوانات والأماكن. أمارس هوايتي في نهاية الأسبوع.",
        ["hobby", "like", "because", "practice"], 16, 40, 15),
    speakingMission("talk-family", "Talk About Your Family", "تحدث عن عائلتك", "Family", "Easy", "🎙️",
        "Talk about your family members and what you do together.", "تحدث عن أفراد عائلتك وما تفعلونه معا.",
        ["family", "father", "mother", "brother", "sister"],
        ["I live with...", "My family is...", "We like to...", "I help my family by..."],
        "I live with my family. My father and mother help me every day. I have kind brothers and sisters. We eat dinner together and talk.",
        "أعيش مع عائلتي. يساعدني والدي ووالدتي كل يوم. لدي إخوة وأخوات لطفاء. نتناول العشاء معا ونتحدث.",
        ["family", "father", "mother", "together"], 16, 40, 15),
    speakingMission("describe-day", "Describe Your Day", "صف يومك", "Daily Life", "Medium", "🎙️",
        "Describe your day from morning to evening.", "صف يومك من الصباح إلى المساء.",
        ["wake up", "breakfast", "school", "homework", "sleep"],
        ["First, I...", "After that, I...", "In the afternoon...", "At night..."],
        "First, I wake up early and eat breakfast. Then I go to school. In the afternoon, I do my homework. At night, I sleep early.",
        "أولا أستيقظ مبكرا وأتناول الإفطار. ثم أذهب إلى المدرسة. في العصر أحل واجباتي. في الليل أنام مبكرا.",
        ["wake", "school", "homework", "night"], 18, 45, 15),
    speakingMission("order-food", "Order Food", "اطلب طعاما", "Restaurant", "Medium", "🎙️",
        "Order food politely at a restaurant.", "اطلب طعاما بأدب في مطعم.",
        ["please", "would like", "chicken", "rice", "water"],
        ["I would like...", "Can I have...", "Please bring...", "Thank you."],
        "Hello. I would like chicken and rice, please. Can I have a bottle of water? Thank you very much.",
        "مرحبا. أود دجاجا وأرزا من فضلك. هل يمكنني الحصول على زجاجة ماء؟ شكرا جزيلا.",
        ["would", "please", "water", "thank"], 14, 35, 15),
    speakingMission("ask-directions", "Ask for Directions", "اسأل عن الاتجاهات", "Directions", "Medium", "🎙️",
        "Ask someone how to go to a place.", "اسأل شخصا كيف تذهب إلى مكان.",
        ["where", "library", "straight", "left", "right"],
        ["Excuse me...", "Where is...", "How can I go to...", "Thank you."],
        "Excuse me, where is the library? How can I go there? Thank you for your help.",
        "عفوا، أين المكتبة؟ كيف أستطيع الذهاب إلى هناك؟ شكرا لمساعدتك.",
        ["excuse", "where", "library", "thank"], 12, 35, 15),
    speakingMission("favorite-sport", "Talk About Your Favorite Sport", "تحدث عن رياضتك المفضلة", "Sports", "Easy", "🎙️",
        "Talk about your favorite sport.", "تحدث عن رياضتك المفضلة.",
        ["sport", "football", "team", "practice", "healthy"],
        ["My favorite sport is...", "I play it...", "It helps me...", "My team..."],
        "My favorite sport is football. I play it with my friends after school. It helps me stay healthy. I like teamwork.",
        "رياضتي المفضلة هي كرة القدم. ألعبها مع أصدقائي بعد المدرسة. تساعدني على البقاء بصحة جيدة. أحب العمل الجماعي.",
        ["sport", "football", "friends", "healthy"], 16, 40, 15),
    speakingMission("future-job-speaking", "Talk About Your Future Job", "تحدث عن وظيفتك المستقبلية", "Future", "Medium", "🎙️",
        "Talk about the job you want in the future.", "تحدث عن الوظيفة التي تريدها في المستقبل.",
        ["future", "engineer", "doctor", "teacher", "help"],
        ["In the future...", "I want to be...", "This job helps...", "I will study..."],
        "In the future, I want to be an engineer. I like building things and solving problems. I will study hard to reach my dream.",
        "في المستقبل أريد أن أصبح مهندسا. أحب بناء الأشياء وحل المشكلات. سأدرس بجد لأصل إلى حلمي.",
        ["future", "want", "engineer", "study"], 16, 45, 15),
    speakingMission("advice-friend", "Give Advice to a Friend", "قدّم نصيحة لصديق", "Values", "Challenge", "🎙️",
        "Give helpful advice to a friend.", "قدّم نصيحة مفيدة لصديق.",
        ["advice", "should", "study", "sleep", "try"],
        ["You should...", "Try to...", "Do not...", "I think..."],
        "You should study a little every day. Try to sleep early before exams. Do not give up. I think you can improve.",
        "ينبغي أن تدرس قليلا كل يوم. حاول أن تنام مبكرا قبل الاختبارات. لا تستسلم. أعتقد أنك تستطيع التحسن.",
        ["should", "try", "study", "improve"], 18, 45, 15),
    speakingMission("healthy-habits-speaking", "Talk About Healthy Habits", "تحدث عن العادات الصحية", "Health", "Medium", "🎙️",
        "Talk about healthy habits you can do every day.", "تحدث عن عادات صحية تستطيع فعلها كل يوم.",
        ["healthy", "water", "exercise", "sleep", "food"],
        ["I drink...", "I eat...", "I do exercise...", "I sleep..."],
        "I drink water every day. I eat fruits and vegetables. I do exercise with my family. I sleep early to feel active.",
        "أشرب الماء كل يوم. آكل الفواكه والخضروات. أمارس الرياضة مع عائلتي. أنام مبكرا لأشعر بالنشاط.",
        ["water", "eat", "exercise", "sleep"], 16, 40, 15),
    speakingMission("describe-picture", "Describe a Picture", "صف صورة", "Description", "Challenge", "🎙️",
        "Describe a picture using clear sentences.", "صف صورة باستخدام جمل واضحة.",
        ["picture", "see", "there is", "colors", "people"],
        ["In the picture...", "I can see...", "There is...", "The colors are..."],
        "In the picture, I can see a family in a park. There are trees and flowers. The children are playing. The colors are bright.",
        "في الصورة أرى عائلة في حديقة. توجد أشجار وزهور. الأطفال يلعبون. الألوان زاهية.",
        ["picture", "see", "there", "colors"], 18, 45, 15),
];

const rolePlayData = [
    { id: "role-school", place: "At school", line_a: "Are you ready for class?", target_b: "Yes, I am ready.", target_ar: "نعم، أنا مستعد." },
    { id: "role-restaurant", place: "At the restaurant", line_a: "What would you like to eat?", target_b: "I would like chicken and rice.", target_ar: "أود دجاجا وأرزا." },
    { id: "role-directions", place: "Asking for directions", line_a: "Where is the library?", target_b: "Go straight and turn left.", target_ar: "اذهب للأمام ثم انعطف يسارا." },
    { id: "role-help", place: "Asking for help", line_a: "Can you help me, please?", target_b: "Yes, of course.", target_ar: "نعم، بالتأكيد." },
];

const writingTasksData = [
    writingTask("write-yourself", "Write About Yourself", "اكتب عن نفسك", "Personal", "Easy", "✍️",
        "Write 5 sentences about yourself.", "اكتب 5 جمل عن نفسك باللغة الإنجليزية.",
        ["name", "age", "student", "school", "like"],
        ["My name is...", "I am ... years old.", "I am a student.", "I live in...", "I like..."],
        "My name is Ahmed. I am twelve years old. I am a student. I live in Saudi Arabia. I like English and football.",
        "اسمي أحمد. عمري اثنا عشر عاما. أنا طالب. أعيش في السعودية. أحب الإنجليزية وكرة القدم.",
        25, ["name", "student", "like"]),
    writingTask("write-school", "Write About Your School", "اكتب عن مدرستك", "School", "Easy", "✍️",
        "Write a short paragraph about your school.", "اكتب فقرة قصيرة عن مدرستك.",
        ["school", "class", "teacher", "friends", "learn"],
        ["My school is...", "I study...", "My classroom is...", "My teachers are...", "I learn..."],
        "My school is big and clean. I study English, math, science, and Arabic. My teachers are kind. I learn with my friends every day.",
        "مدرستي كبيرة ونظيفة. أدرس الإنجليزية والرياضيات والعلوم والعربية. معلموّي لطفاء. أتعلم مع أصدقائي كل يوم.",
        28, ["school", "study", "teacher", "learn"]),
    writingTask("write-best-friend", "Write About Your Best Friend", "اكتب عن أفضل صديق لك", "Values", "Easy", "✍️",
        "Write about your best friend.", "اكتب عن أفضل صديق لك.",
        ["friend", "kind", "helpful", "study", "play"],
        ["My best friend is...", "He/She is...", "We like to...", "My friend helps me...", "I feel..."],
        "My best friend is kind and helpful. We study together before tests. We play football after school. I feel happy with my friend.",
        "أفضل صديق لي لطيف ومتعاون. ندرس معا قبل الاختبارات. نلعب كرة القدم بعد المدرسة. أشعر بالسعادة مع صديقي.",
        25, ["friend", "kind", "helpful"]),
    writingTask("write-hobby", "Write About Your Favorite Hobby", "اكتب عن هوايتك المفضلة", "Daily Life", "Easy", "✍️",
        "Write about your favorite hobby.", "اكتب عن هوايتك المفضلة.",
        ["hobby", "drawing", "reading", "practice", "enjoy"],
        ["My favorite hobby is...", "I like it because...", "I practice it...", "It helps me...", "In the future..."],
        "My favorite hobby is drawing. I like it because it helps me relax. I practice drawing on weekends. I want to improve my hobby.",
        "هوايتي المفضلة هي الرسم. أحبها لأنها تساعدني على الاسترخاء. أمارس الرسم في نهاية الأسبوع. أريد تحسين هوايتي.",
        26, ["hobby", "like", "practice"]),
    writingTask("write-family", "Write About Your Family", "اكتب عن عائلتك", "Family", "Easy", "✍️",
        "Write about your family.", "اكتب عن عائلتك.",
        ["family", "father", "mother", "brother", "sister"],
        ["My family is...", "I live with...", "My father...", "My mother...", "We like to..."],
        "My family is loving and helpful. I live with my father, mother, brothers, and sisters. We eat dinner together. I help my family at home.",
        "عائلتي محبة ومتعاونة. أعيش مع والدي ووالدتي وإخوتي وأخواتي. نتناول العشاء معا. أساعد عائلتي في البيت.",
        28, ["family", "father", "mother"]),
    writingTask("write-routine", "Write About Your Daily Routine", "اكتب عن روتينك اليومي", "Daily Life", "Medium", "✍️",
        "Write about your daily routine from morning to night.", "اكتب عن روتينك اليومي من الصباح إلى الليل.",
        ["wake up", "breakfast", "school", "homework", "sleep"],
        ["First, I...", "Then I...", "After school...", "In the evening...", "At night..."],
        "First, I wake up early and eat breakfast. Then I go to school by bus. After school, I do my homework. At night, I sleep early.",
        "أولا أستيقظ مبكرا وأتناول الإفطار. ثم أذهب إلى المدرسة بالحافلة. بعد المدرسة أحل واجباتي. في الليل أنام مبكرا.",
        32, ["wake", "school", "homework", "sleep"]),
    writingTask("write-healthy-food", "Write About Healthy Food", "اكتب عن الطعام الصحي", "Health", "Medium", "✍️",
        "Write about healthy food and why it is important.", "اكتب عن الطعام الصحي ولماذا هو مهم.",
        ["healthy", "fruit", "vegetables", "water", "energy"],
        ["Healthy food...", "I eat...", "I drink...", "It gives me...", "I avoid..."],
        "Healthy food is important for our bodies. I eat fruit, vegetables, eggs, and fish. I drink water every day. Healthy food gives me energy.",
        "الطعام الصحي مهم لأجسامنا. آكل الفواكه والخضروات والبيض والسمك. أشرب الماء كل يوم. الطعام الصحي يعطيني الطاقة.",
        30, ["healthy", "food", "water", "energy"]),
    writingTask("write-dialogue", "Write a Short Dialogue", "اكتب حوارا قصيرا", "Conversation", "Challenge", "✍️",
        "Write a short dialogue between two people.", "اكتب حوارا قصيرا بين شخصين.",
        ["hello", "please", "thank you", "can", "would like"],
        ["A: Hello...", "B: Hi...", "A: Can you...", "B: Yes...", "A: Thank you."],
        "A: Hello, can you help me, please? B: Yes, of course. A: Where is the library? B: Go straight and turn left.",
        "أ: مرحبا، هل يمكنك مساعدتي من فضلك؟ ب: نعم بالتأكيد. أ: أين المكتبة؟ ب: اذهب للأمام ثم انعطف يسارا.",
        28, ["hello", "please", "thank"]),
    writingTask("write-picture", "Describe a Picture", "صف صورة", "Description", "Challenge", "✍️",
        "Describe a picture using clear sentences.", "صف صورة باستخدام جمل واضحة.",
        ["picture", "see", "there is", "people", "colors"],
        ["In the picture...", "I can see...", "There is...", "The people are...", "The colors are..."],
        "In the picture, I can see a family in a park. There are trees and flowers. The children are playing. The colors are bright.",
        "في الصورة أرى عائلة في حديقة. توجد أشجار وزهور. الأطفال يلعبون. الألوان زاهية.",
        30, ["picture", "see", "there"]),
    writingTask("write-future-dream", "Write About Your Future Dream", "اكتب عن حلمك في المستقبل", "Future", "Medium", "✍️",
        "Write about your future dream.", "اكتب عن حلمك في المستقبل.",
        ["future", "dream", "engineer", "doctor", "study"],
        ["In the future...", "I want to be...", "My dream is...", "I will study...", "I hope..."],
        "In the future, I want to be an engineer. My dream is to build useful things. I will study hard. I hope to help my country.",
        "في المستقبل أريد أن أصبح مهندسا. حلمي أن أبني أشياء مفيدة. سأدرس بجد. أتمنى أن أساعد وطني.",
        30, ["future", "dream", "study"]),
];

const sentenceHelperData = {
    subjects: ["I", "My friend", "My teacher", "My family", "The student"],
    verbs: ["like", "play", "study", "visit", "help", "want to be"],
    objects: ["English", "football", "my school", "my family", "a doctor", "a teacher"],
};

const storiesData = [
    storyItem("lost-bag", "The Lost Bag", "الحقيبة المفقودة", "Daily Life", "Easy", "🎒",
        "Maha was walking to class when she saw a small black bag under a bench. At first, she thought it belonged to one of her friends, but nobody was near it. She picked it up carefully and took it to her teacher. Inside the bag, there was a notebook, a pencil case, and a lunch box with the name Sami on it. The teacher called Sami from the next classroom. Sami was worried because he had looked everywhere for his bag. When he saw it, he smiled and thanked Maha. The teacher praised Maha for being honest and helpful. The class also learned why lost things should be returned quickly. At the end of the day, Sami shared his fruit with Maha, and they became good friends.",
        "رأت مها حقيبة سوداء صغيرة تحت المقعد وهي تمشي إلى الصف. أخذتها إلى المعلمة، فوجدت المعلمة اسم سامي داخلها. كان سامي قلقا لأنه بحث عن حقيبته في كل مكان. شكر مها، ومدحتها المعلمة على الأمانة والمساعدة.",
        ["bag = حقيبة", "bench = مقعد", "belonged = تخص", "carefully = بعناية", "notebook = دفتر", "worried = قلق", "honest = أمين", "praised = مدح", "shared = شارك"],
        "الأمانة ومساعدة الآخرين من الصفات المهمة.",
        ["Maha saw a bag under a bench.", "She took it to her teacher.", "The teacher found Sami's name.", "Sami thanked Maha.", "They became good friends."]),
    storyItem("helpful-friend", "The Helpful Friend", "الصديق المتعاون", "Values", "Easy", "🤝",
        "Omar and Faisal were working on a science poster. Omar was good at drawing, but Faisal was better at writing clear sentences. The poster had to be ready before Thursday. On Tuesday, Faisal became sick and stayed at home. Omar felt nervous because he thought he could not finish the work alone. After school, he called Faisal and asked how he was feeling. Faisal said he could help by sending ideas and short sentences from home. Omar drew the pictures, and Faisal sent the writing by phone. The next day, Omar printed the sentences and added them to the poster. Their teacher liked the project because both boys helped each other. Omar learned that real friends do not leave each other during hard times.",
        "كان عمر وفيصل يعملان على ملصق علوم. مرض فيصل، فساعد من البيت بإرسال أفكار وجمل قصيرة. رسم عمر الصور وأضاف الجمل، وأعجبت المعلمة بالمشروع لأنهما تعاونا.",
        ["poster = ملصق", "drawing = رسم", "sentences = جمل", "nervous = متوتر", "alone = وحده", "ideas = أفكار", "printed = طبع", "project = مشروع", "real friends = أصدقاء حقيقيون"],
        "الصديق الحقيقي يساعد وقت الحاجة.",
        ["Omar and Faisal worked on a poster.", "Faisal became sick.", "Faisal sent ideas from home.", "Omar finished the poster.", "They learned about friendship."]),
    storyItem("smart-student", "The Smart Student", "الطالب الذكي", "School", "Medium", "🧠",
        "Noura was a quiet student, but she loved solving problems. One morning, the class computer stopped working before an English presentation. The students became upset because their pictures and sentences were saved on it. The teacher asked everyone to stay calm. Noura noticed that the screen was black, but the small light on the computer was still on. She checked the cable and saw that it was loose. She gently pushed it back into place and waited for a moment. The screen turned on again, and the class cheered. The teacher thanked Noura and asked her to explain what she had done. Noura said, 'I looked carefully before I touched anything.' Her classmates learned that smart thinking begins with calm observation.",
        "كانت نورة طالبة هادئة تحب حل المشكلات. توقف الحاسوب قبل عرض إنجليزي، ولاحظت نورة أن السلك غير مثبت جيدا. أعادته لمكانه فعاد الجهاز للعمل.",
        ["quiet = هادئ", "solving = حل", "presentation = عرض", "upset = منزعج", "calm = هادئ", "cable = سلك", "loose = غير مثبت", "cheered = هلل", "observation = ملاحظة"],
        "التفكير الهادئ يساعد على حل المشكلات.",
        ["The computer stopped working.", "Noura stayed calm.", "She checked the cable.", "The screen turned on.", "The class thanked her."]),
    storyItem("market-day", "A Day at the Market", "يوم في السوق", "Shopping", "Medium", "🛒",
        "On Friday afternoon, Ali went to the market with his mother. The market was busy, colorful, and full of sounds. They needed tomatoes, rice, bread, and a blue shirt for Ali's brother. Ali carried a small list so they would not forget anything. First, they bought vegetables from an old man who smiled kindly. Then they went to a clothing shop. Ali compared two shirts and chose the one with better cloth. His mother asked him to check the price and count the change. Ali felt proud because he used English numbers to read the price tag. He also greeted the seller politely and said thank you. Before they left, his mother bought fresh dates. Ali learned that shopping can teach responsibility, math, and polite conversation.",
        "ذهب علي مع والدته إلى السوق. حمل قائمة صغيرة، واشتروا الخضروات ثم قميصا أزرق. قرأ علي السعر وعد النقود، وتعلم أن التسوق يعلم المسؤولية والحساب.",
        ["market = سوق", "busy = مزدحم", "colorful = ملون", "list = قائمة", "vegetables = خضروات", "compared = قارن", "price = سعر", "change = باقي النقود", "responsibility = مسؤولية"],
        "يمكن أن نتعلم المسؤولية من المواقف اليومية.",
        ["Ali went to the market.", "He carried a list.", "They bought vegetables.", "Ali chose a shirt.", "He counted the change."]),
    storyItem("football-match-story", "The Football Match", "مباراة كرة القدم", "Sports", "Easy", "⚽",
        "The school football match started after the last lesson. Hamad's team wore green shirts, and the other team wore white shirts. Many students stood near the field and cheered. In the first half, the white team scored a goal. Hamad felt disappointed, but his captain told him to stay focused. In the second half, Hamad passed the ball to Yasser, who ran quickly and scored. The game became exciting. Near the end, Hamad had a chance to score, but he saw Yasser in a better place, so he passed the ball. Yasser scored again, and their team won. Everyone shook hands after the final whistle. After the match, the coach said that teamwork was more important than one player being famous.",
        "بدأت مباراة المدرسة بعد الحصة الأخيرة. تأخر فريق حمد بهدف، لكنه تعاون مع ياسر. مرر حمد الكرة بدل أن يسجل وحده، فسجل ياسر وفاز الفريق.",
        ["match = مباراة", "field = ملعب", "cheered = شجع", "disappointed = محبط", "captain = قائد", "focused = مركز", "passed = مرر", "chance = فرصة", "teamwork = عمل جماعي"],
        "العمل الجماعي أهم من الشهرة الفردية.",
        ["The white team scored first.", "The captain told Hamad to focus.", "Yasser scored a goal.", "Hamad passed the ball.", "The team won."]),
    storyItem("little-scientist", "The Little Scientist", "العالم الصغير", "Science", "Challenge", "🔬",
        "Salma liked asking questions about everything around her. One evening, she wondered why plants near the window looked stronger than plants in the dark corner. She decided to do a small experiment. She put two bean plants in similar cups. One cup was near the window, and the other was inside a box with small holes. Every day, she gave both plants the same amount of water. After one week, the plant near the window was taller and greener. Salma wrote her notes in a notebook and drew the two plants. When she showed her family, her father explained that plants need light to make food. Salma felt excited because she had discovered the answer by observing, testing, and recording carefully.",
        "كانت سلمى تحب الأسئلة. وضعت نبتتين في مكانين مختلفين وأعطتهما نفس كمية الماء. بعد أسبوع، كانت نبتة النافذة أطول وأخضر، فعرفت أهمية الضوء للنبات.",
        ["scientist = عالم", "wondered = تساءلت", "stronger = أقوى", "experiment = تجربة", "similar = مشابه", "amount = كمية", "notes = ملاحظات", "observing = ملاحظة", "recording = تسجيل"],
        "التجربة والملاحظة تساعداننا على التعلم.",
        ["Salma asked a question.", "She prepared two plants.", "She gave them water.", "One plant grew better.", "She recorded her discovery."]),
    storyItem("rainy-day", "The Rainy Day", "اليوم الممطر", "Weather", "Medium", "🌧️",
        "It was a rainy morning, and the sky was dark. Fahad wanted to stay at home, but he had an important English test. His mother gave him an umbrella and told him to walk carefully. On the way to school, Fahad saw a young student standing near a large puddle. The student was afraid to cross because his shoes might get wet. Fahad held the umbrella over both of them and showed him a safer path. They reached school a little late, but the teacher smiled when she heard the story. Fahad took his test and did well. Later, the young student thanked him in the hallway. He learned that rainy days may be difficult, but they can also give us a chance to help someone.",
        "كان الصباح ممطرا، وذهب فهد إلى المدرسة لاختبار مهم. في الطريق ساعد طالبا صغيرا على عبور طريق آمن بالمظلة. تأخر قليلا لكنه تعلم أن الأيام الصعبة تمنحنا فرصة للمساعدة.",
        ["rainy = ممطر", "umbrella = مظلة", "carefully = بحذر", "puddle = بركة ماء", "afraid = خائف", "cross = يعبر", "path = طريق", "late = متأخر", "chance = فرصة"],
        "حتى الأيام الصعبة يمكن أن تكون فرصة لفعل الخير.",
        ["Fahad went to school in the rain.", "He saw a young student.", "He helped him cross safely.", "The teacher heard the story.", "Fahad did well on the test."]),
    storyItem("new-library", "The New Library", "المكتبة الجديدة", "Reading", "Challenge", "📚",
        "The school opened a new library with bright shelves, quiet tables, and many English books. Sara loved the place from the first day. She chose a short story about space, but some words were difficult. Instead of closing the book, she wrote the new words in her notebook and looked for their meanings. The librarian showed her how to use a simple dictionary. After a few days, Sara finished the story and told her classmates about it. More students started visiting the library because Sara made reading sound exciting. At the end of the month, the librarian gave Sara a small certificate. Sara learned that a library is not only a room with books; it is a place where questions become discoveries.",
        "افتتحت المدرسة مكتبة جديدة. اختارت سارة قصة عن الفضاء وكتبت الكلمات الصعبة في دفترها. ساعدتها أمينة المكتبة على استخدام القاموس، ثم شجعت زميلاتها على القراءة.",
        ["library = مكتبة", "shelves = رفوف", "quiet = هادئ", "space = الفضاء", "difficult = صعب", "dictionary = قاموس", "classmates = زملاء", "certificate = شهادة", "discoveries = اكتشافات"],
        "القراءة تفتح باب الأسئلة والاكتشاف.",
        ["The school opened a library.", "Sara chose a space story.", "She wrote new words.", "The librarian helped her.", "Sara encouraged others to read."]),
];

const levelFourExamData = {
    weights: { vocabulary: 15, grammar: 15, reading: 20, listening: 15, speaking: 15, writing: 20 },
    vocabulary: [
        { q: "Choose the Arabic meaning of: honest", options: ["أمين", "سريع", "بارد"], a: "أمين" },
        { q: "Complete: I drink ____ every day.", options: ["water", "table", "shoe"], a: "water" },
        { q: "Choose the right word: My favorite ____ is football.", options: ["sport", "airport", "doctor"], a: "sport" },
        { q: "Ticket means:", options: ["تذكرة", "قلم", "مطر"], a: "تذكرة" },
        { q: "Choose the meaning of: future", options: ["المستقبل", "السوق", "الصديق"], a: "المستقبل" },
        { q: "Complete: Fruits and vegetables are ____ food.", options: ["healthy", "late", "lost"], a: "healthy" },
        { q: "Library means:", options: ["مكتبة", "ملعب", "حقيبة"], a: "مكتبة" },
        { q: "Choose the suitable word: I need a ____ when I am sick.", options: ["doctor", "shirt", "team"], a: "doctor" },
        { q: "Helpful means:", options: ["متعاون", "مفقود", "مظلم"], a: "متعاون" },
        { q: "Choose the word for: مظلة", options: ["umbrella", "notebook", "poster"], a: "umbrella" },
    ],
    grammar: [
        { q: "Choose: She ____ happy.", options: ["is", "are", "am"], a: "is" },
        { q: "Choose: They ____ students.", options: ["are", "is", "am"], a: "are" },
        { q: "Correct: He play football.", options: ["He plays football.", "He playing football.", "He play football."], a: "He plays football." },
        { q: "Choose: I ____ English every day.", options: ["study", "studies", "studying"], a: "study" },
        { q: "Choose: My friend ____ a book.", options: ["has", "have", "having"], a: "has" },
        { q: "Complete: There ____ trees in the park.", options: ["are", "is", "am"], a: "are" },
        { q: "Choose: ____ is your name?", options: ["What", "Where", "When"], a: "What" },
        { q: "Correct: I am go to school.", options: ["I go to school.", "I goes to school.", "I going school."], a: "I go to school." },
        { q: "Choose: The bag is ____ the table.", options: ["under", "happy", "run"], a: "under" },
        { q: "Complete: Yesterday, I ____ my homework.", options: ["finished", "finish", "finishes"], a: "finished" },
    ],
    readingText: "Lina wanted to improve her English before the end of the school year. Every afternoon, she read a short story, wrote five new words, and listened to one English sentence. At first, she made mistakes and felt shy when she spoke. Her teacher told her that learning a language needs practice and patience. Lina started speaking with her friend for five minutes each day. She also used a small notebook to review difficult words before class. After one month, she could understand stories faster and write better sentences. Her family noticed her confidence, and Lina learned that small daily steps can make a big difference.",
    reading: [
        { q: "What did Lina want to improve?", options: ["Her English", "Her football", "Her cooking"], a: "Her English" },
        { q: "What did she read every afternoon?", options: ["A short story", "A menu", "A ticket"], a: "A short story" },
        { q: "How many new words did she write?", options: ["Five", "Ten", "Two"], a: "Five" },
        { q: "How did she feel at first?", options: ["Shy", "Angry", "Sleepy"], a: "Shy" },
        { q: "What does learning a language need?", options: ["Practice and patience", "Only money", "No effort"], a: "Practice and patience" },
        { q: "Who did Lina speak with?", options: ["Her friend", "A doctor", "A seller"], a: "Her friend" },
        { q: "How long did she speak each day?", options: ["Five minutes", "One hour", "Two seconds"], a: "Five minutes" },
        { q: "What improved after one month?", options: ["Reading and writing", "Only running", "Only drawing"], a: "Reading and writing" },
        { q: "What is the lesson?", options: ["Small steps help", "Never practice", "Stories are bad"], a: "Small steps help" },
        { q: "The text is mainly about:", options: ["Learning English", "Buying clothes", "A rainy day"], a: "Learning English" },
    ],
    listening: [
        { audio_text: "I finished my homework yesterday.", q: "What did the speaker finish?", options: ["homework", "breakfast", "a match"], a: "homework" },
        { audio_text: "The weather is sunny today.", q: "How is the weather?", options: ["sunny", "rainy", "cold"], a: "sunny" },
        { audio_text: "I have a ticket and a small suitcase.", q: "What does the speaker have?", options: ["ticket and suitcase", "doctor and water", "book and pencil"], a: "ticket and suitcase" },
        { audio_text: "Can you help me, please?", q: "What does the speaker ask for?", options: ["help", "food", "a shirt"], a: "help" },
        { audio_text: "Our team won the football match.", q: "Who won?", options: ["our team", "the teacher", "the doctor"], a: "our team" },
    ],
    speaking: {
        prompt: "Introduce yourself and talk about your favorite hobby.",
        model: "My name is Sara. I am a student. I like English. My favorite hobby is drawing because it helps me relax.",
        keywords: ["name", "student", "like", "hobby"],
    },
    writing: {
        prompt: "Write a short paragraph about your school day.",
        target_words: ["school", "study", "friends", "homework"],
        min_words: 35,
    },
};

let levelFourProgress = { points: 0, actions: 0, opened: [] };
let readingProgress = { points: 0, actions: 0, completed: [], fiveBonus: false, masteredBonus: false };
let listeningProgress = { points: 0, actions: 0, completed: [], review: [], tenBonus: false, masteredBonus: false };
let speakingProgress = { points: 0, actions: 0, completed: [], review: [], attempts: [], tenBonus: false, masteredBonus: false };
let writingProgress = { points: 0, actions: 0, completed: [], review: [], attempts: [], eightBonus: false, masteredBonus: false };
let storyProgress = { points: 0, actions: 0, opened: [], completed: [], endings: [], bestScore: 0, lastRead: "", fiveBonus: false, masteredBonus: false };
let examProgress = { points: 0, actions: 0, bestScore: 0, lastScore: null, certificate: false, awarded: [] };
let activeSpeed = null;
let activeListeningItem = null;
let listeningQuickQuiz = { active: false, items: [], index: 0, score: 0, answered: false };
let activeSpeakingMission = null;
let activeRecognition = null;
let currentTranscript = "";
let speakingChallenge = { active: false, items: [], index: 0, scores: [], words: 0 };
let rolePlaySession = { active: false, index: 0, scores: [], words: 0 };
let activeWritingTask = null;
let writingChallenge = { active: false, items: [], index: 0, scores: [], words: 0, completed: 0 };
let activeStory = null;
let storyChallenge = { active: false, items: [], index: 0, score: 0, total: 0 };
let activeExam = { questions: [], index: 0, answers: {}, speakingTranscript: "", result: null };

function speakingMission(id, title_en, title_ar, category, level, emoji, prompt_en, prompt_ar, helpful_words, sentence_starters, model_answer, model_answer_ar, target_keywords, min_words, speaking_time_seconds, points) {
    return {
        id,
        title_en,
        title_ar,
        category,
        level,
        emoji,
        prompt_en,
        prompt_ar,
        helpful_words,
        sentence_starters,
        model_answer,
        model_answer_ar,
        target_keywords,
        min_words,
        speaking_time_seconds,
        points,
    };
}

function writingTask(id, title_en, title_ar, category, level, emoji, prompt_en, prompt_ar, helpful_words, sentence_starters, model_answer, model_answer_ar, min_words, target_words) {
    return {
        id,
        title_en,
        title_ar,
        category,
        level,
        emoji,
        prompt_en,
        prompt_ar,
        helpful_words,
        sentence_starters,
        model_answer,
        model_answer_ar,
        min_words,
        target_words,
        checklist: [
            "بدأت الجمل بحرف كبير",
            "استخدمت نقطة أو علامة استفهام في نهاية الجملة",
            "كتبت عدد كلمات كاف",
            "استخدمت كلمات من القائمة",
        ],
        points: 15,
    };
}

function storyItem(id, title_en, title_ar, category, level, emoji, story_en, story_ar, vocabulary_focus, lesson_ar, event_order) {
    const words = story_en.split(/\s+/).filter(Boolean).length;
    const firstVocab = vocabulary_focus.slice(0, 3).map((entry) => entry.split("=")[0].trim());
    return {
        id,
        title_en,
        title_ar,
        category,
        level,
        emoji,
        story_en,
        story_ar,
        vocabulary_focus,
        lesson_ar,
        event_order,
        word_count: words,
        missing_words_activity: firstVocab.map((word) => ({ prompt: story_en.replace(new RegExp(`\\b${escapeRegExp(word)}\\b`, "i"), "____"), answer: word })),
        speaking_prompt: "Read the first part of the story aloud.",
        writing_prompt: "Write three sentences about what happened.",
        alternate_ending_prompt: "Write a different ending for the story.",
        points: 20,
        comprehension_questions: [
            { q: "What is the main idea of the story?", a: lesson_ar, options: [lesson_ar, "Buying a phone only", "Sleeping all day"] },
            { q: "Where does the story happen?", a: category, options: [category, "Under the sea", "On another planet"] },
            { q: "What should the student learn?", a: "The lesson of the story", options: ["The lesson of the story", "Only new colors", "A phone number"] },
            { q: "How many events should you order?", a: "Five", options: ["Two", "Five", "Ten"] },
            { q: "What can you write after reading?", a: "A different ending", options: ["A different ending", "A shopping list only", "Nothing"] },
        ],
        true_false_questions: [
            { q: "The story has an English text.", a: "True" },
            { q: "The story includes Arabic translation.", a: "True" },
            { q: "The story has vocabulary words.", a: "True" },
            { q: "Students can write an alternate ending.", a: "True" },
            { q: "There are no events in the story.", a: "False" },
        ],
    };
}

function escapeRegExp(value) {
    return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function passage(id, title_en, title_ar, category, level, emoji, passage_en, passage_ar, vocabulary_focus, speaking_prompt, sentence_order) {
    const words = passage_en.split(/\s+/).filter(Boolean).length;
    return {
        id,
        title_en,
        title_ar,
        category,
        level,
        emoji,
        passage_en,
        passage_ar,
        vocabulary_focus,
        speaking_prompt,
        sentence_order,
        reading_speed_words: words,
        comprehension_questions: [
            { q: "What is the main topic of the passage?", a: category, options: [category, "Weather only", "A phone problem"] },
            { q: "Which skill does the passage help you practice?", a: "Reading", options: ["Reading", "Cooking", "Drawing only"] },
            { q: "How many important words should you review?", a: "The vocabulary focus words", options: ["No words", "The vocabulary focus words", "Only names"] },
            { q: "What should you do after reading?", a: "Answer the questions", options: ["Close the page", "Answer the questions", "Skip everything"] },
            { q: "Is the passage suitable for Level 4?", a: "Yes", options: ["Yes", "No", "Only for teachers"] },
        ],
        true_false_questions: [
            { q: "The passage has an English text.", a: "True" },
            { q: "The passage includes Arabic translation.", a: "True" },
            { q: "The passage has no vocabulary focus.", a: "False" },
            { q: "Students can practice speaking after reading.", a: "True" },
            { q: "The speed test calculates WPM.", a: "True" },
        ],
    };
}

function loadLevelFourProgress() {
    try {
        const saved = JSON.parse(localStorage.getItem("levelFourProgress") || "{}");
        levelFourProgress = {
            points: Number(saved.points || 0),
            actions: Number(saved.actions || 0),
            opened: Array.isArray(saved.opened) ? saved.opened : [],
        };
        const reading = JSON.parse(localStorage.getItem("levelFourReadingProgress") || "{}");
        readingProgress = {
            points: Number(reading.points || 0),
            actions: Number(reading.actions || 0),
            completed: Array.isArray(reading.completed) ? reading.completed : [],
            fiveBonus: Boolean(reading.fiveBonus),
            masteredBonus: Boolean(reading.masteredBonus),
        };
        const listening = JSON.parse(localStorage.getItem("levelFourListeningProgress") || "{}");
        listeningProgress = {
            points: Number(listening.points || 0),
            actions: Number(listening.actions || 0),
            completed: Array.isArray(listening.completed) ? listening.completed : [],
            review: Array.isArray(listening.review) ? listening.review : [],
            tenBonus: Boolean(listening.tenBonus),
            masteredBonus: Boolean(listening.masteredBonus),
        };
        const speaking = JSON.parse(localStorage.getItem("levelFourSpeakingProgress") || "{}");
        speakingProgress = {
            points: Number(speaking.points || 0),
            actions: Number(speaking.actions || 0),
            completed: Array.isArray(speaking.completed) ? speaking.completed : [],
            review: Array.isArray(speaking.review) ? speaking.review : [],
            attempts: Array.isArray(speaking.attempts) ? speaking.attempts : [],
            tenBonus: Boolean(speaking.tenBonus),
            masteredBonus: Boolean(speaking.masteredBonus),
        };
        const writing = JSON.parse(localStorage.getItem("levelFourWritingProgress") || "{}");
        writingProgress = {
            points: Number(writing.points || 0),
            actions: Number(writing.actions || 0),
            completed: Array.isArray(writing.completed) ? writing.completed : [],
            review: Array.isArray(writing.review) ? writing.review : [],
            attempts: Array.isArray(writing.attempts) ? writing.attempts : [],
            eightBonus: Boolean(writing.eightBonus),
            masteredBonus: Boolean(writing.masteredBonus),
        };
        const stories = JSON.parse(localStorage.getItem("levelFourStoriesProgress") || "{}");
        storyProgress = {
            points: Number(stories.points || 0),
            actions: Number(stories.actions || 0),
            opened: Array.isArray(stories.opened) ? stories.opened : [],
            completed: Array.isArray(stories.completed) ? stories.completed : [],
            endings: Array.isArray(stories.endings) ? stories.endings : [],
            bestScore: Number(stories.bestScore || 0),
            lastRead: String(stories.lastRead || ""),
            fiveBonus: Boolean(stories.fiveBonus),
            masteredBonus: Boolean(stories.masteredBonus),
        };
        const exam = JSON.parse(localStorage.getItem("levelFourExamProgress") || "{}");
        examProgress = {
            points: Number(exam.points || 0),
            actions: Number(exam.actions || 0),
            bestScore: Number(exam.bestScore || 0),
            lastScore: exam.lastScore ?? null,
            certificate: Boolean(exam.certificate),
        };
    } catch {
        levelFourProgress = { points: 0, actions: 0, opened: [] };
        readingProgress = { points: 0, actions: 0, completed: [], fiveBonus: false, masteredBonus: false };
        listeningProgress = { points: 0, actions: 0, completed: [], review: [], tenBonus: false, masteredBonus: false };
        speakingProgress = { points: 0, actions: 0, completed: [], review: [], attempts: [], tenBonus: false, masteredBonus: false };
        writingProgress = { points: 0, actions: 0, completed: [], review: [], attempts: [], eightBonus: false, masteredBonus: false };
        storyProgress = { points: 0, actions: 0, opened: [], completed: [], endings: [], bestScore: 0, lastRead: "", fiveBonus: false, masteredBonus: false };
        examProgress = { points: 0, actions: 0, bestScore: 0, lastScore: null, certificate: false };
    }
}

function saveLevelFourProgress() {
    localStorage.setItem("levelFourProgress", JSON.stringify(levelFourProgress));
    localStorage.setItem("levelFourReadingProgress", JSON.stringify(readingProgress));
    saveLevelFourListeningProgress();
    saveLevelFourSpeakingProgress();
    saveLevelFourWritingProgress();
    saveLevelFourStoriesProgress();
    saveLevelFourExamProgress();
}

function saveLevelFourListeningProgress() {
    localStorage.setItem("levelFourListeningProgress", JSON.stringify(listeningProgress));
}

function loadLevelFourListeningProgress() {
    try {
        const listening = JSON.parse(localStorage.getItem("levelFourListeningProgress") || "{}");
        listeningProgress = {
            points: Number(listening.points || 0),
            actions: Number(listening.actions || 0),
            completed: Array.isArray(listening.completed) ? listening.completed : [],
            review: Array.isArray(listening.review) ? listening.review : [],
            tenBonus: Boolean(listening.tenBonus),
            masteredBonus: Boolean(listening.masteredBonus),
        };
    } catch {
        listeningProgress = { points: 0, actions: 0, completed: [], review: [], tenBonus: false, masteredBonus: false };
    }
}

function saveLevelFourSpeakingProgress() {
    localStorage.setItem("levelFourSpeakingProgress", JSON.stringify(speakingProgress));
}

function loadLevelFourSpeakingProgress() {
    try {
        const speaking = JSON.parse(localStorage.getItem("levelFourSpeakingProgress") || "{}");
        speakingProgress = {
            points: Number(speaking.points || 0),
            actions: Number(speaking.actions || 0),
            completed: Array.isArray(speaking.completed) ? speaking.completed : [],
            review: Array.isArray(speaking.review) ? speaking.review : [],
            attempts: Array.isArray(speaking.attempts) ? speaking.attempts : [],
            tenBonus: Boolean(speaking.tenBonus),
            masteredBonus: Boolean(speaking.masteredBonus),
        };
    } catch {
        speakingProgress = { points: 0, actions: 0, completed: [], review: [], attempts: [], tenBonus: false, masteredBonus: false };
    }
}

function saveLevelFourWritingProgress() {
    localStorage.setItem("levelFourWritingProgress", JSON.stringify(writingProgress));
}

function loadLevelFourWritingProgress() {
    try {
        const writing = JSON.parse(localStorage.getItem("levelFourWritingProgress") || "{}");
        writingProgress = {
            points: Number(writing.points || 0),
            actions: Number(writing.actions || 0),
            completed: Array.isArray(writing.completed) ? writing.completed : [],
            review: Array.isArray(writing.review) ? writing.review : [],
            attempts: Array.isArray(writing.attempts) ? writing.attempts : [],
            eightBonus: Boolean(writing.eightBonus),
            masteredBonus: Boolean(writing.masteredBonus),
        };
    } catch {
        writingProgress = { points: 0, actions: 0, completed: [], review: [], attempts: [], eightBonus: false, masteredBonus: false };
    }
}

function saveLevelFourStoriesProgress() {
    localStorage.setItem("levelFourStoriesProgress", JSON.stringify(storyProgress));
}

function loadLevelFourStoriesProgress() {
    try {
        const stories = JSON.parse(localStorage.getItem("levelFourStoriesProgress") || "{}");
        storyProgress = {
            points: Number(stories.points || 0),
            actions: Number(stories.actions || 0),
            opened: Array.isArray(stories.opened) ? stories.opened : [],
            completed: Array.isArray(stories.completed) ? stories.completed : [],
            endings: Array.isArray(stories.endings) ? stories.endings : [],
            bestScore: Number(stories.bestScore || 0),
            lastRead: String(stories.lastRead || ""),
            fiveBonus: Boolean(stories.fiveBonus),
            masteredBonus: Boolean(stories.masteredBonus),
        };
    } catch {
        storyProgress = { points: 0, actions: 0, opened: [], completed: [], endings: [], bestScore: 0, lastRead: "", fiveBonus: false, masteredBonus: false };
    }
}

function saveLevelFourExamProgress() {
    localStorage.setItem("levelFourExamProgress", JSON.stringify(examProgress));
}

function loadLevelFourExamProgress() {
    try {
        const exam = JSON.parse(localStorage.getItem("levelFourExamProgress") || "{}");
        examProgress = {
            points: Number(exam.points || 0),
            actions: Number(exam.actions || 0),
            bestScore: Number(exam.bestScore || 0),
            lastScore: exam.lastScore ?? null,
            certificate: Boolean(exam.certificate),
            awarded: Array.isArray(exam.awarded) ? exam.awarded : [],
        };
    } catch {
        examProgress = { points: 0, actions: 0, bestScore: 0, lastScore: null, certificate: false, awarded: [] };
    }
}

function csrfToken() {
    return document.cookie.split(";").map((value) => value.trim()).find((value) => value.startsWith("csrftoken="))?.split("=")[1] || "";
}

async function awardReadingPoints(activityType, points, passageId = "", completed = false) {
    let pointsToAward = points;
    readingProgress.actions += 1;
    if (completed && passageId && !readingProgress.completed.includes(passageId)) {
        readingProgress.completed.push(passageId);
    }
    if (readingProgress.completed.length >= 5 && !readingProgress.fiveBonus) {
        pointsToAward += 20;
        readingProgress.fiveBonus = true;
    }
    if (readingProgress.completed.length >= readingPassages.length && !readingProgress.masteredBonus) {
        pointsToAward += 50;
        readingProgress.masteredBonus = true;
    }
    readingProgress.points += pointsToAward;
    saveLevelFourProgress();
    updateReadingStats();

    try {
        const response = await fetch(window.LEVEL_FOUR_PROGRESS_URL || "/api/english-foundation/progress/", {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
            body: JSON.stringify({ section: "level_four_reading", activity_type: activityType, points: pointsToAward, completed }),
        });
        const data = await response.json();
        if (data.status === "ok") {
            readingProgress.points = data.points;
            readingProgress.actions = data.actions_count;
            saveLevelFourProgress();
            updateReadingStats();
        }
    } catch {
        // TODO: integrate level_four_reading with StudentActivity leaderboard.
    }
}

function statusFromPoints(points) {
    if (points >= 300) return "متقن";
    if (points >= 150) return "ممتاز";
    if (points >= 50) return "جيد";
    return "قيد التدريب";
}

function setText(id, value) {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
}

function setProgress(id, value) {
    const element = document.getElementById(id);
    if (element) element.style.width = value;
}

function updateLevelFourStats() {
    const totalPoints = levelFourProgress.points + readingProgress.points + listeningProgress.points + speakingProgress.points + writingProgress.points + storyProgress.points + examProgress.points;
    setText("levelFourPoints", totalPoints);
    setText("levelFourActions", levelFourProgress.actions + readingProgress.actions + listeningProgress.actions + speakingProgress.actions + writingProgress.actions + storyProgress.actions + examProgress.actions);
    setText("levelFourOpened", levelFourProgress.opened.length);
    setText("levelFourStatus", statusFromPoints(totalPoints));
    setProgress("levelFourProgress", `${Math.min(100, Math.round((totalPoints / 1400) * 100))}%`);
}

function updateReadingStats() {
    setText("readingPoints", readingProgress.points);
    setText("readingActions", readingProgress.actions);
    setText("readingCompleted", `${readingProgress.completed.length} / ${readingPassages.length}`);
    setProgress("readingProgress", `${Math.min(100, Math.round((readingProgress.completed.length / readingPassages.length) * 100))}%`);
    updateLevelFourStats();
}

function updateListeningStats() {
    setText("listeningPoints", listeningProgress.points);
    setText("listeningActions", listeningProgress.actions);
    setText("listeningCompleted", `${listeningProgress.completed.length} / ${listeningPracticeData.length}`);
    setProgress("listeningProgress", `${Math.min(100, Math.round((listeningProgress.completed.length / listeningPracticeData.length) * 100))}%`);
    updateLevelFourStats();
}

function updateSpeakingStats() {
    setText("speakingPoints", speakingProgress.points);
    setText("speakingActions", speakingProgress.actions);
    setText("speakingCompleted", `${speakingProgress.completed.length} / ${speakingMissionsData.length}`);
    setProgress("speakingProgress", `${Math.min(100, Math.round((speakingProgress.completed.length / speakingMissionsData.length) * 100))}%`);
    updateLevelFourStats();
}

function updateWritingStats() {
    setText("writingPoints", writingProgress.points);
    setText("writingActions", writingProgress.actions);
    setText("writingCompleted", `${writingProgress.completed.length} / ${writingTasksData.length}`);
    setProgress("writingProgress", `${Math.min(100, Math.round((writingProgress.completed.length / writingTasksData.length) * 100))}%`);
    updateLevelFourStats();
}

function updateStoryStats() {
    setText("storyPoints", storyProgress.points);
    setText("storyOpened", storyProgress.opened.length);
    setText("storyCompleted", `${storyProgress.completed.length} / ${storiesData.length}`);
    setText("storyBestScore", `${storyProgress.bestScore}%`);
    setText("storyLastRead", storyProgress.lastRead || "-");
    setText("storyEndings", storyProgress.endings.length);
    setProgress("storyProgress", `${Math.min(100, Math.round((storyProgress.completed.length / storiesData.length) * 100))}%`);
    updateLevelFourStats();
}

function updateExamStats() {
    setText("examPoints", examProgress.points);
    setText("examBestScore", `${examProgress.bestScore}%`);
    setText("examLastScore", examProgress.lastScore === null ? "-" : `${examProgress.lastScore}%`);
    setProgress("examProgress", `${Math.min(100, examProgress.bestScore)}%`);
    updateLevelFourStats();
}

function passageCard(item) {
    return `
        <article class="passage-card" data-passage-id="${item.id}">
            <div class="card-icon">${item.emoji}</div>
            <h3>${item.title_en}</h3>
            <p class="passage-title-ar">${item.title_ar}</p>
            <div class="passage-meta">
                <span>${item.category}</span>
                <span>${item.level}</span>
                <span>${item.reading_speed_words} words</span>
            </div>
            <p class="passage-preview">${escapeHtml(item.passage_en.split(".").slice(0, 2).join(". "))}.</p>
            <div class="vocab-list">${item.vocabulary_focus.slice(0, 6).map((word) => `<span>${escapeHtml(word)}</span>`).join("")}</div>
            <div class="passage-actions">
                <button type="button" data-reading-action="read" data-id="${item.id}">اقرأ القطعة</button>
                <button type="button" data-reading-action="listen" data-id="${item.id}">استمع</button>
                <button type="button" data-reading-action="slow" data-id="${item.id}">قراءة بطيئة</button>
                <button type="button" data-reading-action="quiz" data-id="${item.id}">حل أسئلة الفهم</button>
                <button type="button" data-reading-action="mic" data-id="${item.id}">اقرأ بالمايك</button>
                <button type="button" data-reading-action="speed" data-id="${item.id}">اختبار سرعة القراءة</button>
            </div>
        </article>
    `;
}

function renderReadingPassages() {
    const grid = document.getElementById("readingPassagesGrid");
    if (grid) grid.innerHTML = readingPassages.map(passageCard).join("");
}

async function awardListeningPoints(activityType, points, listeningId = "", completed = false) {
    let pointsToAward = points;
    listeningProgress.actions += 1;
    if (completed && listeningId && !listeningProgress.completed.includes(listeningId)) {
        listeningProgress.completed.push(listeningId);
    }
    if (listeningProgress.completed.length >= 10 && !listeningProgress.tenBonus) {
        pointsToAward += 30;
        listeningProgress.tenBonus = true;
    }
    if (listeningProgress.completed.length >= listeningPracticeData.length && !listeningProgress.masteredBonus) {
        pointsToAward += 50;
        listeningProgress.masteredBonus = true;
    }
    listeningProgress.points += pointsToAward;
    saveLevelFourListeningProgress();
    updateListeningStats();

    try {
        const response = await fetch(window.LEVEL_FOUR_PROGRESS_URL || "/api/english-foundation/progress/", {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
            body: JSON.stringify({ section: "level_four_listening", activity_type: activityType, points: pointsToAward, completed }),
        });
        const data = await response.json();
        if (data.status === "ok") {
            listeningProgress.points = data.points;
            listeningProgress.actions = data.actions_count;
            saveLevelFourListeningProgress();
            updateListeningStats();
        }
    } catch {
        // TODO: integrate level_four_listening with StudentActivity leaderboard.
    }
}

function listeningCard(item) {
    return `
        <article class="listening-card" data-listening-id="${item.id}">
            <div class="card-icon">${item.emoji}</div>
            <h3>${escapeHtml(item.title_en)}</h3>
            <p class="passage-title-ar">${escapeHtml(item.title_ar)}</p>
            <div class="passage-meta">
                <span>${escapeHtml(item.category)}</span>
                <span>${escapeHtml(item.level)}</span>
                <span>${escapeHtml(typeLabel(item.question_type))}</span>
            </div>
            <p class="listening-prompt">${escapeHtml(item.question_ar)}</p>
            <div class="passage-actions listening-actions">
                <button type="button" data-listening-action="listen" data-id="${item.id}">استمع</button>
                <button type="button" data-listening-action="slow" data-id="${item.id}">استماع بطيء</button>
                <button type="button" data-listening-action="solve" data-id="${item.id}">حل التدريب</button>
                <button type="button" data-listening-action="replay" data-id="${item.id}">إعادة الاستماع</button>
                <button type="button" data-listening-action="review" data-id="${item.id}">أضف للمراجعة</button>
            </div>
        </article>
    `;
}

function typeLabel(type) {
    const labels = {
        choice: "اختيار",
        true_false: "صح أو خطأ",
        fill_blank: "أكمل الفراغ",
        order: "ترتيب",
        reply: "رد مناسب",
    };
    return labels[type] || type;
}

function renderListeningPractice() {
    const grid = document.getElementById("listeningPracticeGrid");
    if (grid) grid.innerHTML = listeningPracticeData.map(listeningCard).join("");
}

function getListeningItem(id) {
    return listeningPracticeData.find((item) => item.id === id);
}

function openListeningModal(item) {
    activeListeningItem = item;
    listeningQuickQuiz = { active: false, items: [], index: 0, score: 0, answered: false };
    document.getElementById("listeningModal").hidden = false;
    document.getElementById("listeningModalMeta").textContent = `${item.category} / ${item.level} / ${typeLabel(item.question_type)}`;
    document.getElementById("listeningModalTitle").textContent = item.title_en;
    document.getElementById("listeningFeedback").hidden = true;
    document.getElementById("listeningModalBody").innerHTML = `
        <div class="audio-text-card">
            <p class="audio-hidden-note">استمع للجملة الإنجليزية ثم أجب.</p>
            <div class="passage-actions">
                <button class="primary-action" type="button" data-listening-modal-action="listen">استمع</button>
                <button type="button" data-listening-modal-action="slow">استماع بطيء</button>
            </div>
        </div>
        <form id="listeningAnswerForm">
            <h3>${escapeHtml(item.question_ar)}</h3>
            ${listeningAnswerControl(item)}
        </form>
        <div class="passage-actions modal-actions">
            <button class="primary-action" type="button" id="checkListeningAnswer">تحقق</button>
            <button type="button" data-listening-modal-action="retry">إعادة المحاولة</button>
            <button type="button" data-listening-modal-action="next">التالي</button>
        </div>
    `;
    awardListeningPoints("open", 1, item.id);
}

function listeningAnswerControl(item) {
    if (item.question_type === "fill_blank") {
        return `<input class="listening-input" id="listeningTextAnswer" type="text" autocomplete="off" placeholder="اكتب الكلمة الناقصة">`;
    }
    if (item.question_type === "order") {
        return `
            <p class="translation-text">اكتب الإجابة بهذا الشكل: Go straight | Turn left</p>
            <div class="vocab-list">${item.choices.map((choice) => `<span>${escapeHtml(choice)}</span>`).join("")}</div>
            <input class="listening-input" id="listeningTextAnswer" type="text" autocomplete="off" placeholder="رتب الجمل هنا">
        `;
    }
    return `
        <div class="option-grid">
            ${item.choices.map((choice) => `
                <label>
                    <input type="radio" name="listeningAnswer" value="${escapeHtml(choice)}">
                    <span>${escapeHtml(choice)}</span>
                </label>
            `).join("")}
        </div>
    `;
}

function speakListeningText(item = activeListeningItem, rate = 0.9) {
    if (!item) return;
    try {
        if (!("speechSynthesis" in window)) {
            showListeningFeedback("النطق غير مدعوم في هذا المتصفح.", "warn");
            return;
        }
        const utterance = new SpeechSynthesisUtterance(item.audio_text);
        utterance.lang = "en-US";
        utterance.rate = rate;
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utterance);
    } catch {
        showListeningFeedback("تعذر تشغيل الاستماع الآن.", "warn");
    }
}

function speakListeningSlow(item = activeListeningItem) {
    speakListeningText(item, 0.65);
}

function selectedListeningAnswer() {
    const typed = document.getElementById("listeningTextAnswer");
    if (typed) return typed.value;
    return document.querySelector("#listeningAnswerForm input[name='listeningAnswer']:checked")?.value || "";
}

function checkListeningAnswer(item = activeListeningItem) {
    if (!item) return false;
    const answer = selectedListeningAnswer();
    const isCorrect = normalizeListeningAnswer(answer) === normalizeListeningAnswer(item.correct_answer);
    const message = isCorrect
        ? `صحيح. ${item.explanation_ar}`
        : `حاول مرة أخرى. ${item.explanation_ar}`;
    showListeningFeedback(message, isCorrect ? "good" : "warn");
    if (isCorrect) {
        awardListeningPoints("correct_answer", 5, item.id);
        awardListeningPoints("complete", item.points, item.id, true);
    }
    if (listeningQuickQuiz.active && !listeningQuickQuiz.answered) {
        listeningQuickQuiz.answered = true;
        if (isCorrect) listeningQuickQuiz.score += 1;
    }
    return isCorrect;
}

function normalizeListeningAnswer(value) {
    return String(value || "")
        .toLowerCase()
        .replace(/\s*\|\s*/g, "|")
        .replace(/[^\w\s|']/g, "")
        .replace(/\s+/g, " ")
        .trim();
}

function addListeningReview(item) {
    if (!listeningProgress.review.includes(item.id)) {
        listeningProgress.review.push(item.id);
        saveLevelFourListeningProgress();
    }
    showListeningFeedback("تمت إضافة التدريب للمراجعة.", "good");
}

function startListeningQuickQuiz() {
    const shuffled = listeningPracticeData.slice().sort(() => Math.random() - 0.5).slice(0, 5);
    listeningQuickQuiz = { active: true, items: shuffled, index: 0, score: 0, answered: false };
    document.getElementById("listeningModal").hidden = false;
    renderListeningQuickQuizItem();
}

function renderListeningQuickQuizItem() {
    const item = listeningQuickQuiz.items[listeningQuickQuiz.index];
    if (!item) {
        finishListeningQuickQuiz();
        return;
    }
    activeListeningItem = item;
    listeningQuickQuiz.answered = false;
    document.getElementById("listeningModalMeta").textContent = `Quick Quiz ${listeningQuickQuiz.index + 1} / ${listeningQuickQuiz.items.length}`;
    document.getElementById("listeningModalTitle").textContent = "اختبار الاستماع السريع";
    document.getElementById("listeningFeedback").hidden = true;
    document.getElementById("listeningModalBody").innerHTML = `
        <div class="audio-text-card">
            <h3>${escapeHtml(item.title_en)}</h3>
            <p>${escapeHtml(item.question_ar)}</p>
            <div class="passage-actions">
                <button class="primary-action" type="button" data-listening-modal-action="listen">استمع</button>
                <button type="button" data-listening-modal-action="slow">استماع بطيء</button>
            </div>
        </div>
        <form id="listeningAnswerForm">${listeningAnswerControl(item)}</form>
        <div class="passage-actions modal-actions">
            <button class="primary-action" type="button" id="checkListeningAnswer">تحقق</button>
            <button type="button" data-listening-modal-action="quick-next">التالي</button>
        </div>
    `;
}

function finishListeningQuickQuiz() {
    const score = listeningQuickQuiz.score;
    const rating = score <= 2 ? "يحتاج تدريب" : score <= 4 ? "جيد" : "ممتاز";
    document.getElementById("listeningModalMeta").textContent = "Sprint Level 4.2";
    document.getElementById("listeningModalTitle").textContent = "اختبار الاستماع السريع";
    document.getElementById("listeningModalBody").innerHTML = `
        <div class="quick-result">
            <strong>${score} / 5</strong>
            <p>التقييم: ${rating}</p>
            <button class="primary-action" type="button" id="startListeningQuickQuizAgain">إعادة الاختبار</button>
        </div>
    `;
    showListeningFeedback("تم إكمال اختبار الاستماع السريع.", score >= 3 ? "good" : "warn");
    awardListeningPoints("quick_quiz", 20, "quick-quiz", false);
    listeningQuickQuiz = { active: false, items: [], index: 0, score: 0, answered: false };
}

function showListeningFeedback(message, tone = "") {
    const box = document.getElementById("listeningFeedback");
    if (!box) return;
    box.hidden = false;
    box.className = `reading-feedback ${tone}`;
    box.textContent = message;
}

async function awardSpeakingPoints(activityType, points, missionId = "", completed = false) {
    let pointsToAward = points;
    speakingProgress.actions += 1;
    if (completed && missionId && !speakingProgress.completed.includes(missionId) && missionId !== "speaking-challenge" && missionId !== "role-play-mini") {
        speakingProgress.completed.push(missionId);
    }
    if (speakingProgress.completed.length >= 10 && !speakingProgress.tenBonus) {
        pointsToAward += 30;
        speakingProgress.tenBonus = true;
    }
    if (speakingProgress.completed.length >= speakingMissionsData.length && !speakingProgress.masteredBonus) {
        pointsToAward += 50;
        speakingProgress.masteredBonus = true;
    }
    speakingProgress.points += pointsToAward;
    saveLevelFourSpeakingProgress();
    updateSpeakingStats();

    try {
        const response = await fetch(window.LEVEL_FOUR_PROGRESS_URL || "/api/english-foundation/progress/", {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
            body: JSON.stringify({ section: "level_four_speaking", activity_type: activityType, points: pointsToAward, completed }),
        });
        const data = await response.json();
        if (data.status === "ok") {
            speakingProgress.points = data.points;
            speakingProgress.actions = data.actions_count;
            saveLevelFourSpeakingProgress();
            updateSpeakingStats();
        }
    } catch {
        // TODO: integrate level_four_speaking with StudentActivity leaderboard.
    }
}

function speakingCard(item) {
    return `
        <article class="speaking-card" data-speaking-id="${item.id}">
            <div class="card-icon">${item.emoji}</div>
            <h3>${escapeHtml(item.title_en)}</h3>
            <p class="passage-title-ar">${escapeHtml(item.title_ar)}</p>
            <div class="passage-meta">
                <span>${escapeHtml(item.category)}</span>
                <span>${escapeHtml(item.level)}</span>
                <span>${item.speaking_time_seconds}s</span>
                <span>${item.min_words}+ words</span>
            </div>
            <div class="vocab-list">${item.helpful_words.slice(0, 6).map((word) => `<span>${escapeHtml(word)}</span>`).join("")}</div>
            <div class="passage-actions speaking-actions">
                <button type="button" data-speaking-action="open" data-id="${item.id}">افتح المهمة</button>
                <button type="button" data-speaking-action="listen" data-id="${item.id}">استمع للنموذج</button>
                <button type="button" data-speaking-action="slow" data-id="${item.id}">قراءة بطيئة</button>
                <button type="button" data-speaking-action="mic" data-id="${item.id}">ابدأ المايك</button>
                <button type="button" data-speaking-action="help" data-id="${item.id}">عرض الكلمات المساعدة</button>
                <button type="button" data-speaking-action="review" data-id="${item.id}">أضف للمراجعة</button>
            </div>
        </article>
    `;
}

function renderSpeakingMissions() {
    const grid = document.getElementById("speakingMissionsGrid");
    if (grid) grid.innerHTML = speakingMissionsData.map(speakingCard).join("");
}

function getSpeakingMission(id) {
    return speakingMissionsData.find((item) => item.id === id);
}

function openSpeakingModal(item) {
    activeSpeakingMission = item;
    currentTranscript = "";
    document.getElementById("speakingModal").hidden = false;
    document.getElementById("speakingModalMeta").textContent = `${item.category} / ${item.level} / ${item.speaking_time_seconds}s`;
    document.getElementById("speakingModalTitle").textContent = item.title_en;
    document.getElementById("speakingFeedback").hidden = true;
    document.getElementById("speakingModalBody").innerHTML = `
        <div class="speaking-focus-box">
            <p><strong>${escapeHtml(item.prompt_ar)}</strong></p>
            <p class="model-answer">${escapeHtml(item.prompt_en)}</p>
            <div class="vocab-list">${item.helpful_words.map((word) => `<span>${escapeHtml(word)}</span>`).join("")}</div>
        </div>
        <div class="speaking-focus-box">
            <h3>Sentence Starters</h3>
            <div class="sentence-starters">${item.sentence_starters.map((sentence) => `<div>${escapeHtml(sentence)}</div>`).join("")}</div>
        </div>
        <div class="speaking-focus-box">
            <h3>Model Answer</h3>
            <p class="model-answer">${escapeHtml(item.model_answer)}</p>
            <p>${escapeHtml(item.model_answer_ar)}</p>
            <div class="passage-actions">
                <button class="primary-action" type="button" data-speaking-modal-action="listen">استمع للنموذج</button>
                <button type="button" data-speaking-modal-action="slow">قراءة بطيئة</button>
                <button type="button" data-speaking-modal-action="stop-speech">إيقاف</button>
            </div>
        </div>
        <div class="passage-actions">
            <button class="primary-action" type="button" data-speaking-modal-action="start-mic">ابدأ التسجيل</button>
            <button type="button" data-speaking-modal-action="stop-mic">إيقاف</button>
            <button type="button" data-speaking-modal-action="retry">إعادة المحاولة</button>
            <button type="button" data-speaking-modal-action="save">حفظ المحاولة</button>
        </div>
        <span class="mic-status" id="speakingMicStatus">الميكروفون جاهز</span>
        <div class="spoken-text-panel" id="spokenTextPanel">النص الذي تقوله سيظهر هنا.</div>
        <div id="speakingScorePanel"></div>
    `;
    awardSpeakingPoints("open", 1, item.id);
}

function speakModelAnswer(item = activeSpeakingMission, rate = 0.9) {
    if (!item) return;
    try {
        if (!("speechSynthesis" in window)) {
            showSpeakingFeedback("النطق غير مدعوم في هذا المتصفح.", "warn");
            return;
        }
        const utterance = new SpeechSynthesisUtterance(item.model_answer);
        utterance.lang = "en-US";
        utterance.rate = rate;
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utterance);
        awardSpeakingPoints("listen_model", 1, item.id);
    } catch {
        showSpeakingFeedback("تعذر تشغيل النطق الآن.", "warn");
    }
}

function speakModelSlow(item = activeSpeakingMission) {
    speakModelAnswer(item, 0.65);
}

function stopModelSpeech() {
    if ("speechSynthesis" in window) window.speechSynthesis.cancel();
}

function startSpeakingRecognition(item = activeSpeakingMission, expectedText = "", mode = "mission") {
    activeSpeakingMission = item;
    currentTranscript = "";
    setMicStatus(SpeechService.messages.listening, true);
    SpeechService.startRecognition({
        targetText: expectedText || item.model_answer,
        type: "long_sentence",
        section: "level_four_speaking",
        level: mode,
        onResult: (speechResult) => {
            currentTranscript = speechResult.spokenText || speechResult.spoken || "";
            const panel = document.getElementById("spokenTextPanel");
            if (panel) panel.textContent = currentTranscript;
            const result = evaluateSpeaking(currentTranscript, expectedText || item.model_answer, item);
            result.status = speechResult.status;
            result.failure_reason = speechResult.failure_reason || null;
            result.browser_error = speechResult.browser_error || null;
            result.spoken_text = currentTranscript;
            renderSpeakingResult(result);
            saveSpeakingAttempt(item, result, mode);
            if (mode === "mission") {
                awardSpeakingPoints("mic", 5, item.id);
                if (result.wordCount >= item.min_words && result.score >= 60) awardSpeakingPoints("complete", item.points, item.id, true);
                if (result.score >= 85) awardSpeakingPoints("excellent", 10, item.id);
            }
            if (mode === "challenge") {
                speakingChallenge.scores.push(result.score);
                speakingChallenge.words += result.wordCount;
            }
            if (mode === "roleplay") {
                rolePlaySession.scores.push(result.score);
                rolePlaySession.words += result.wordCount;
            }
            setMicStatus("انتهى التسجيل", false);
        },
        onError: (result) => {
            setMicStatus("الميكروفون جاهز", false);
            showSpeakingFeedback(result.message || SpeechService.messages.unknown, "warn");
        },
        onEnd: () => setMicStatus("الميكروفون جاهز", false)
    });
    return;
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) {
        showSpeakingFeedback("الميكروفون غير مدعوم في هذا المتصفح، جرّب Google Chrome.", "warn");
        return;
    }
    try {
        activeSpeakingMission = item;
        currentTranscript = "";
        activeRecognition = new Recognition();
        activeRecognition.lang = "en-US";
        activeRecognition.interimResults = false;
        activeRecognition.maxAlternatives = 1;
        setMicStatus("التسجيل يعمل...", true);
        activeRecognition.onresult = (event) => {
            currentTranscript = event.results[0][0].transcript;
            const panel = document.getElementById("spokenTextPanel");
            if (panel) panel.textContent = currentTranscript;
            const result = evaluateSpeaking(currentTranscript, expectedText || item.model_answer, item);
            renderSpeakingResult(result);
            saveSpeakingAttempt(item, result, mode);
            if (mode === "mission") {
                awardSpeakingPoints("mic", 5, item.id);
                if (result.wordCount >= item.min_words && result.score >= 60) awardSpeakingPoints("complete", item.points, item.id, true);
                if (result.score >= 85) awardSpeakingPoints("excellent", 10, item.id);
            }
            if (mode === "challenge") {
                speakingChallenge.scores.push(result.score);
                speakingChallenge.words += result.wordCount;
            }
            if (mode === "roleplay") {
                rolePlaySession.scores.push(result.score);
                rolePlaySession.words += result.wordCount;
            }
            setMicStatus("انتهى التسجيل", false);
        };
        activeRecognition.onerror = () => {
            setMicStatus("تعذر تشغيل المايك", false);
            showSpeakingFeedback("تعذر تشغيل المايك الآن. اسمح للمتصفح باستخدام الميكروفون ثم حاول مرة أخرى.", "warn");
        };
        activeRecognition.onend = () => setMicStatus("الميكروفون جاهز", false);
        activeRecognition.start();
    } catch {
        showSpeakingFeedback("تعذر بدء التسجيل الآن.", "warn");
    }
}

function stopSpeakingRecognition() {
    if (activeRecognition) activeRecognition.stop();
    setMicStatus("تم إيقاف التسجيل", false);
}

function setMicStatus(message, listening = false) {
    const status = document.getElementById("speakingMicStatus");
    if (!status) return;
    status.textContent = message;
    status.classList.toggle("listening", listening);
}

function evaluateSpeaking(transcript, expectedText, item = activeSpeakingMission) {
    const spoken = normalizeSpeechText(transcript);
    const expected = normalizeSpeechText(expectedText);
    const spokenWords = spoken.split(" ").filter(Boolean);
    const expectedWords = expected.split(" ").filter(Boolean);
    const hits = expectedWords.filter((word) => spokenWords.includes(word)).length;
    const similarity = expectedWords.length ? Math.round((hits / expectedWords.length) * 100) : 0;
    const keywordResult = checkTargetKeywords(transcript, item?.target_keywords || []);
    const keywordBonus = keywordResult.total ? Math.round((keywordResult.used.length / keywordResult.total) * 20) : 0;
    const score = Math.min(100, Math.round(similarity * 0.8 + keywordBonus));
    const wordCount = countSpokenWords(transcript);
    let rating = score >= 85 ? "ممتاز" : score >= 60 ? "جيد" : "حاول مرة أخرى";
    let message = "";
    if (item && wordCount < item.min_words) {
        rating = "حاول مرة أخرى";
        message = "تحدث أكثر وحاول استخدام كلمات أكثر.";
    }
    return { score, similarity, wordCount, rating, usedKeywords: keywordResult.used, totalKeywords: keywordResult.total, message };
}

function normalizeSpeechText(value) {
    return String(value || "").toLowerCase().replace(/[^\w\s']/g, "").replace(/\s+/g, " ").trim();
}

function countSpokenWords(value) {
    return normalizeSpeechText(value).split(" ").filter(Boolean).length;
}

function checkTargetKeywords(transcript, keywords) {
    const normalized = normalizeSpeechText(transcript);
    const used = keywords.filter((keyword) => normalized.includes(normalizeSpeechText(keyword)));
    return { used, total: keywords.length };
}

function renderSpeakingResult(result) {
    const panel = document.getElementById("speakingScorePanel");
    if (!panel) return;
    panel.innerHTML = `
        <div class="score-panel">
            <div class="score-circle">${result.score}%</div>
            <p><strong>${result.rating}</strong></p>
            <p>Similarity: ${result.similarity}% | Words: ${result.wordCount} | Keywords: ${result.usedKeywords.length} / ${result.totalKeywords}</p>
            ${result.message ? `<p>${escapeHtml(result.message)}</p>` : ""}
        </div>
    `;
    showSpeakingFeedback(result.rating, result.score >= 60 && !result.message ? "good" : "warn");
}

function saveSpeakingAttempt(item, result, mode = "mission") {
    speakingProgress.attempts.unshift({
        id: item?.id || mode,
        mode,
        score: result.score,
        words: result.wordCount,
        spoken_text: result.spoken_text || currentTranscript || "",
        status: result.status || "",
        failure_reason: result.failure_reason || null,
        browser_error: result.browser_error || null,
        at: new Date().toISOString(),
    });
    speakingProgress.attempts = speakingProgress.attempts.slice(0, 30);
    saveLevelFourSpeakingProgress();
}

function addSpeakingReview(item) {
    if (!speakingProgress.review.includes(item.id)) {
        speakingProgress.review.push(item.id);
        saveLevelFourSpeakingProgress();
    }
    showSpeakingFeedback("تمت إضافة المهمة للمراجعة.", "good");
}

function startSpeakingChallenge() {
    speakingChallenge = {
        active: true,
        items: speakingMissionsData.slice().sort(() => Math.random() - 0.5).slice(0, 3),
        index: 0,
        scores: [],
        words: 0,
    };
    document.getElementById("speakingModal").hidden = false;
    renderSpeakingChallengeItem();
}

function renderSpeakingChallengeItem() {
    const item = speakingChallenge.items[speakingChallenge.index];
    if (!item) {
        finishSpeakingChallenge();
        return;
    }
    activeSpeakingMission = item;
    document.getElementById("speakingModalMeta").textContent = `Speaking Challenge ${speakingChallenge.index + 1} / ${speakingChallenge.items.length}`;
    document.getElementById("speakingModalTitle").textContent = item.title_en;
    document.getElementById("speakingFeedback").hidden = true;
    document.getElementById("speakingModalBody").innerHTML = `
        <div class="speaking-focus-box">
            <p><strong>${escapeHtml(item.prompt_ar)}</strong></p>
            <p class="model-answer">${escapeHtml(item.prompt_en)}</p>
            <div class="vocab-list">${item.helpful_words.map((word) => `<span>${escapeHtml(word)}</span>`).join("")}</div>
        </div>
        <div class="passage-actions">
            <button class="primary-action" type="button" data-speaking-modal-action="challenge-mic">ابدأ المايك</button>
            <button type="button" data-speaking-modal-action="challenge-next">التالي</button>
        </div>
        <span class="mic-status" id="speakingMicStatus">الميكروفون جاهز</span>
        <div class="spoken-text-panel" id="spokenTextPanel">النص الذي تقوله سيظهر هنا.</div>
        <div id="speakingScorePanel"></div>
    `;
}

function finishSpeakingChallenge() {
    const completed = speakingChallenge.scores.length;
    const average = completed ? Math.round(speakingChallenge.scores.reduce((sum, value) => sum + value, 0) / completed) : 0;
    const rating = average >= 85 ? "ممتاز" : average >= 60 ? "جيد" : "يحتاج تدريب";
    document.getElementById("speakingModalMeta").textContent = "Sprint Level 4.3";
    document.getElementById("speakingModalTitle").textContent = "تحدي التحدث السريع";
    document.getElementById("speakingModalBody").innerHTML = `
        <div class="score-panel">
            <div class="score-circle">${average}%</div>
            <p>المهام المكتملة: ${completed} / 3</p>
            <p>متوسط نسبة النطق: ${average}%</p>
            <p>عدد الكلمات: ${speakingChallenge.words}</p>
            <p>النتيجة النهائية: <strong>${rating}</strong></p>
            <button class="primary-action" type="button" id="startSpeakingChallengeAgain">إعادة التحدي</button>
        </div>
    `;
    showSpeakingFeedback("تم إكمال تحدي التحدث السريع.", average >= 60 ? "good" : "warn");
    awardSpeakingPoints("speaking_challenge", 25, "speaking-challenge", false);
    speakingChallenge = { active: false, items: [], index: 0, scores: [], words: 0 };
}

function startRolePlayMini() {
    rolePlaySession = { active: true, index: 0, scores: [], words: 0 };
    document.getElementById("speakingModal").hidden = false;
    renderRolePlayItem();
}

function renderRolePlayItem() {
    const item = rolePlayData[rolePlaySession.index];
    if (!item) {
        finishRolePlayMini();
        return;
    }
    const mission = {
        id: item.id,
        title_en: item.place,
        target_keywords: normalizeSpeechText(item.target_b).split(" ").filter(Boolean),
        min_words: Math.max(3, countSpokenWords(item.target_b)),
        model_answer: item.target_b,
    };
    activeSpeakingMission = mission;
    document.getElementById("speakingModalMeta").textContent = `Role Play Mini ${rolePlaySession.index + 1} / ${rolePlayData.length}`;
    document.getElementById("speakingModalTitle").textContent = item.place;
    document.getElementById("speakingFeedback").hidden = true;
    document.getElementById("speakingModalBody").innerHTML = `
        <div class="role-play-panel">
            <p><strong>A:</strong> <span class="model-answer">${escapeHtml(item.line_a)}</span></p>
            <p><strong>B target:</strong> <span class="model-answer">${escapeHtml(item.target_b)}</span></p>
            <p>${escapeHtml(item.target_ar)}</p>
            <div class="passage-actions">
                <button class="primary-action" type="button" data-speaking-modal-action="role-listen">استمع للطرف A</button>
                <button type="button" data-speaking-modal-action="role-mic">رد بالمايك</button>
                <button type="button" data-speaking-modal-action="role-next">التالي</button>
            </div>
        </div>
        <span class="mic-status" id="speakingMicStatus">الميكروفون جاهز</span>
        <div class="spoken-text-panel" id="spokenTextPanel">ردك سيظهر هنا.</div>
        <div id="speakingScorePanel"></div>
    `;
}

function speakRolePlayLine() {
    const item = rolePlayData[rolePlaySession.index];
    if (!item) return;
    try {
        if (!("speechSynthesis" in window)) {
            showSpeakingFeedback("النطق غير مدعوم في هذا المتصفح.", "warn");
            return;
        }
        const utterance = new SpeechSynthesisUtterance(item.line_a);
        utterance.lang = "en-US";
        utterance.rate = 0.9;
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utterance);
    } catch {
        showSpeakingFeedback("تعذر تشغيل النطق الآن.", "warn");
    }
}

function checkRolePlayAnswer() {
    const item = rolePlayData[rolePlaySession.index];
    if (!item) return;
    startSpeakingRecognition(activeSpeakingMission, item.target_b, "roleplay");
}

function finishRolePlayMini() {
    const completed = rolePlaySession.scores.length;
    const average = completed ? Math.round(rolePlaySession.scores.reduce((sum, value) => sum + value, 0) / completed) : 0;
    const rating = average >= 85 ? "ممتاز" : average >= 60 ? "جيد" : "يحتاج تدريب";
    document.getElementById("speakingModalMeta").textContent = "Sprint Level 4.3";
    document.getElementById("speakingModalTitle").textContent = "Role Play Mini";
    document.getElementById("speakingModalBody").innerHTML = `
        <div class="score-panel">
            <div class="score-circle">${average}%</div>
            <p>المواقف المكتملة: ${completed} / ${rolePlayData.length}</p>
            <p>متوسط التقييم: ${average}%</p>
            <p>عدد الكلمات: ${rolePlaySession.words}</p>
            <p>النتيجة النهائية: <strong>${rating}</strong></p>
            <button class="primary-action" type="button" id="startRolePlayMiniAgain">إعادة Role Play</button>
        </div>
    `;
    showSpeakingFeedback("تم إكمال Role Play Mini.", average >= 60 ? "good" : "warn");
    awardSpeakingPoints("role_play", 20, "role-play-mini", false);
    rolePlaySession = { active: false, index: 0, scores: [], words: 0 };
}

function showSpeakingFeedback(message, tone = "") {
    const box = document.getElementById("speakingFeedback");
    if (!box) return;
    box.hidden = false;
    box.className = `reading-feedback ${tone}`;
    box.textContent = message;
}

async function awardWritingPoints(activityType, points, taskId = "", completed = false) {
    let pointsToAward = points;
    writingProgress.actions += 1;
    if (completed && taskId && !writingProgress.completed.includes(taskId) && taskId !== "writing-challenge") {
        writingProgress.completed.push(taskId);
    }
    if (writingProgress.completed.length >= 8 && !writingProgress.eightBonus) {
        pointsToAward += 30;
        writingProgress.eightBonus = true;
    }
    if (writingProgress.completed.length >= writingTasksData.length && !writingProgress.masteredBonus) {
        pointsToAward += 50;
        writingProgress.masteredBonus = true;
    }
    writingProgress.points += pointsToAward;
    saveLevelFourWritingProgress();
    updateWritingStats();

    try {
        const response = await fetch(window.LEVEL_FOUR_PROGRESS_URL || "/api/english-foundation/progress/", {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
            body: JSON.stringify({ section: "level_four_writing", activity_type: activityType, points: pointsToAward, completed }),
        });
        const data = await response.json();
        if (data.status === "ok") {
            writingProgress.points = data.points;
            writingProgress.actions = data.actions_count;
            saveLevelFourWritingProgress();
            updateWritingStats();
        }
    } catch {
        // TODO: integrate level_four_writing with StudentActivity leaderboard.
    }
}

function writingCard(item) {
    return `
        <article class="writing-card" data-writing-id="${item.id}">
            <div class="card-icon">${item.emoji}</div>
            <h3>${escapeHtml(item.title_en)}</h3>
            <p class="passage-title-ar">${escapeHtml(item.title_ar)}</p>
            <div class="passage-meta">
                <span>${escapeHtml(item.category)}</span>
                <span>${escapeHtml(item.level)}</span>
                <span>${item.min_words}+ words</span>
            </div>
            <div class="vocab-list">${item.helpful_words.slice(0, 6).map((word) => `<span>${escapeHtml(word)}</span>`).join("")}</div>
            <div class="passage-actions writing-actions">
                <button type="button" data-writing-action="open" data-id="${item.id}">افتح المهمة</button>
                <button type="button" data-writing-action="model" data-id="${item.id}">عرض النموذج</button>
                <button type="button" data-writing-action="start" data-id="${item.id}">ابدأ الكتابة</button>
                <button type="button" data-writing-action="save" data-id="${item.id}">حفظ المحاولة</button>
                <button type="button" data-writing-action="review" data-id="${item.id}">أضف للمراجعة</button>
            </div>
        </article>
    `;
}

function renderWritingPractice() {
    const grid = document.getElementById("writingPracticeGrid");
    if (grid) grid.innerHTML = writingTasksData.map(writingCard).join("");
}

function getWritingTask(id) {
    return writingTasksData.find((item) => item.id === id);
}

function openWritingModal(item) {
    activeWritingTask = item;
    const saved = loadWritingAttempt(item.id);
    document.getElementById("writingModal").hidden = false;
    document.getElementById("writingModalMeta").textContent = `${item.category} / ${item.level} / ${item.min_words}+ words`;
    document.getElementById("writingModalTitle").textContent = item.title_en;
    document.getElementById("writingFeedback").hidden = true;
    document.getElementById("writingModalBody").innerHTML = `
        <div class="writing-editor-box">
            <p><strong>${escapeHtml(item.prompt_ar)}</strong></p>
            <p class="model-answer">${escapeHtml(item.prompt_en)}</p>
            <div class="vocab-list">${item.helpful_words.map((word) => `<span>${escapeHtml(word)}</span>`).join("")}</div>
        </div>
        <div class="speaking-focus-box">
            <h3>Sentence Starters</h3>
            <div class="sentence-starters">${item.sentence_starters.map((sentence) => `<div>${escapeHtml(sentence)}</div>`).join("")}</div>
        </div>
        <div class="writing-editor-box">
            <button class="primary-action" type="button" data-writing-modal-action="toggle-model">إظهار/إخفاء النموذج</button>
            <div id="writingModelAnswer" hidden>
                <p class="model-answer">${escapeHtml(item.model_answer)}</p>
                <p>${escapeHtml(item.model_answer_ar)}</p>
            </div>
        </div>
        <textarea class="writing-textarea" id="writingStudentText" placeholder="Write your answer here...">${escapeHtml(saved)}</textarea>
        <div class="writing-counter-row">
            <span>Words: <strong id="writingWordCount">0</strong></span>
            <span>Sentences: <strong id="writingSentenceCount">0</strong></span>
            <span>Minimum: ${item.min_words}</span>
        </div>
        <div class="writing-checklist">
            ${item.checklist.map((entry, index) => `
                <label>
                    <input type="checkbox" id="writingCheck${index}">
                    <span>${escapeHtml(entry)}</span>
                </label>
            `).join("")}
        </div>
        <div class="passage-actions">
            <button class="primary-action" type="button" data-writing-modal-action="evaluate">تقييم الكتابة</button>
            <button type="button" data-writing-modal-action="save">حفظ المحاولة</button>
            <button type="button" data-writing-modal-action="clear">مسح وإعادة المحاولة</button>
        </div>
        <div id="writingResultPanel"></div>
    `;
    updateWritingCounters();
    awardWritingPoints("open", 1, item.id);
}

function toggleModelAnswer() {
    const model = document.getElementById("writingModelAnswer");
    if (!model) return;
    model.hidden = !model.hidden;
    if (!model.hidden && activeWritingTask) awardWritingPoints("show_model", 1, activeWritingTask.id);
}

function writingTextValue() {
    return document.getElementById("writingStudentText")?.value || "";
}

function countWritingWords(text) {
    return String(text || "").trim().split(/\s+/).filter(Boolean).length;
}

function countWritingSentences(text) {
    return String(text || "").split(/[.!?]+/).map((sentence) => sentence.trim()).filter(Boolean).length;
}

function updateWritingCounters() {
    const text = writingTextValue();
    const wordCount = countWritingWords(text);
    const sentenceCount = countWritingSentences(text);
    const words = document.getElementById("writingWordCount");
    const sentences = document.getElementById("writingSentenceCount");
    if (words) words.textContent = wordCount;
    if (sentences) sentences.textContent = sentenceCount;
}

function evaluateWriting(item = activeWritingTask, text = writingTextValue()) {
    if (!item) return null;
    const wordCount = countWritingWords(text);
    const sentenceCount = countWritingSentences(text);
    const target = checkTargetWords(text, item.target_words);
    const hasPunctuation = checkPunctuation(text);
    const hasCapital = checkCapitalLetters(text);
    let score = 0;
    if (wordCount >= item.min_words) score += 35;
    else score += Math.min(30, Math.round((wordCount / item.min_words) * 30));
    score += item.target_words.length ? Math.round((target.used.length / item.target_words.length) * 25) : 0;
    if (hasPunctuation) score += 20;
    if (hasCapital) score += 20;
    score = Math.min(100, score);
    const lengthLabel = wordCount < item.min_words ? "قصير" : wordCount >= item.min_words + 20 ? "ممتاز" : "مناسب";
    const rating = score >= 85 ? "ممتاز" : score >= 60 ? "جيد" : "يحتاج تحسين";
    const notes = [];
    if (wordCount < item.min_words) notes.push("حاول كتابة كلمات أكثر.");
    if (target.used.length) notes.push("ممتاز، استخدمت كلمات مهمة.");
    if (!hasPunctuation) notes.push("أضف نقطة في نهاية الجملة.");
    if (!hasCapital) notes.push("حاول أن تبدأ الجملة بحرف كبير.");
    return { score, rating, wordCount, sentenceCount, usedTargetWords: target.used, totalTargetWords: item.target_words.length, hasPunctuation, hasCapital, lengthLabel, notes };
}

function checkTargetWords(text, targetWords) {
    const normalized = normalizeSpeechText(text);
    return { used: targetWords.filter((word) => normalized.includes(normalizeSpeechText(word))) };
}

function checkCapitalLetters(text) {
    const trimmed = String(text || "").trim();
    return /^[A-Z]/.test(trimmed);
}

function checkPunctuation(text) {
    return /[.!?]\s*$/.test(String(text || "").trim());
}

function renderWritingEvaluation(result, item = activeWritingTask) {
    const panel = document.getElementById("writingResultPanel");
    if (!panel || !result) return;
    panel.innerHTML = `
        <div class="writing-feedback-panel">
            <h3>${result.rating} - ${result.score}%</h3>
            <div class="writing-result-grid">
                <span>Words: ${result.wordCount}</span>
                <span>Sentences: ${result.sentenceCount}</span>
                <span>Target words: ${result.usedTargetWords.length} / ${result.totalTargetWords}</span>
                <span>Length: ${result.lengthLabel}</span>
            </div>
            <ul>${result.notes.map((note) => `<li>${escapeHtml(note)}</li>`).join("")}</ul>
        </div>
    `;
    showWritingFeedback(result.rating, result.score >= 60 ? "good" : "warn");
    if (item) {
        if (result.wordCount >= 20) awardWritingPoints("twenty_words", 5, item.id);
        awardWritingPoints("evaluate", 10, item.id);
        if (result.wordCount >= item.min_words && result.score >= 60) awardWritingPoints("complete", item.points, item.id, true);
        if (result.score >= 85) awardWritingPoints("excellent", 10, item.id);
    }
}

function saveWritingAttempt(item = activeWritingTask, text = writingTextValue()) {
    if (!item) return;
    const result = evaluateWriting(item, text) || { score: 0, wordCount: 0 };
    const key = `levelFourWritingAttempt:${item.id}`;
    localStorage.setItem(key, text);
    writingProgress.attempts.unshift({
        id: item.id,
        text,
        score: result.score,
        words: result.wordCount,
        at: new Date().toISOString(),
    });
    writingProgress.attempts = writingProgress.attempts.slice(0, 30);
    saveLevelFourWritingProgress();
    awardWritingPoints("save_attempt", 10, item.id);
    showWritingFeedback("تم حفظ المحاولة.", "good");
}

function loadWritingAttempt(taskId) {
    return localStorage.getItem(`levelFourWritingAttempt:${taskId}`) || "";
}

function addWritingReview(item) {
    if (!writingProgress.review.includes(item.id)) {
        writingProgress.review.push(item.id);
        saveLevelFourWritingProgress();
    }
    showWritingFeedback("تمت إضافة المهمة للمراجعة.", "good");
}

function clearWritingAttempt() {
    const textarea = document.getElementById("writingStudentText");
    if (textarea) textarea.value = "";
    document.getElementById("writingResultPanel").innerHTML = "";
    updateWritingCounters();
    showWritingFeedback("تم مسح المحاولة.", "warn");
}

function startWritingChallenge() {
    writingChallenge = {
        active: true,
        items: writingTasksData.slice().sort(() => Math.random() - 0.5).slice(0, 3),
        index: 0,
        scores: [],
        words: 0,
        completed: 0,
    };
    document.getElementById("writingModal").hidden = false;
    renderWritingChallengeItem();
}

function renderWritingChallengeItem() {
    const item = writingChallenge.items[writingChallenge.index];
    if (!item) {
        finishWritingChallenge();
        return;
    }
    activeWritingTask = item;
    document.getElementById("writingModalMeta").textContent = `Writing Challenge ${writingChallenge.index + 1} / ${writingChallenge.items.length}`;
    document.getElementById("writingModalTitle").textContent = item.title_en;
    document.getElementById("writingFeedback").hidden = true;
    document.getElementById("writingModalBody").innerHTML = `
        <div class="writing-editor-box">
            <p><strong>${escapeHtml(item.prompt_ar)}</strong></p>
            <p class="model-answer">${escapeHtml(item.prompt_en)}</p>
            <div class="vocab-list">${item.helpful_words.map((word) => `<span>${escapeHtml(word)}</span>`).join("")}</div>
        </div>
        <textarea class="writing-textarea" id="writingStudentText" placeholder="Write a short answer..."></textarea>
        <div class="writing-counter-row">
            <span>Words: <strong id="writingWordCount">0</strong></span>
            <span>Sentences: <strong id="writingSentenceCount">0</strong></span>
        </div>
        <div class="passage-actions">
            <button class="primary-action" type="button" data-writing-modal-action="challenge-next">تقييم ثم التالي</button>
        </div>
        <div id="writingResultPanel"></div>
    `;
}

function finishWritingChallenge() {
    const completed = writingChallenge.completed;
    const average = writingChallenge.scores.length ? Math.round(writingChallenge.scores.reduce((sum, score) => sum + score, 0) / writingChallenge.scores.length) : 0;
    const rating = average >= 85 ? "ممتاز" : average >= 60 ? "جيد" : "يحتاج تدريب";
    document.getElementById("writingModalMeta").textContent = "Sprint Level 4.4";
    document.getElementById("writingModalTitle").textContent = "تحدي الكتابة السريع";
    document.getElementById("writingModalBody").innerHTML = `
        <div class="writing-feedback-panel">
            <h3>${rating} - ${average}%</h3>
            <div class="writing-result-grid">
                <span>المهام المكتملة: ${completed} / 3</span>
                <span>مجموع الكلمات: ${writingChallenge.words}</span>
                <span>متوسط التقييم: ${average}%</span>
            </div>
            <button class="primary-action" type="button" id="startWritingChallengeAgain">إعادة التحدي</button>
        </div>
    `;
    showWritingFeedback("تم إكمال تحدي الكتابة السريع.", average >= 60 ? "good" : "warn");
    awardWritingPoints("writing_challenge", 25, "writing-challenge", false);
    writingChallenge = { active: false, items: [], index: 0, scores: [], words: 0, completed: 0 };
}

function setupSentenceHelper() {
    const subject = document.getElementById("sentenceSubject");
    const verb = document.getElementById("sentenceVerb");
    const object = document.getElementById("sentenceObject");
    if (!subject || !verb || !object) return;
    subject.innerHTML = sentenceHelperData.subjects.map((item) => `<option value="${escapeHtml(item)}">${escapeHtml(item)}</option>`).join("");
    verb.innerHTML = sentenceHelperData.verbs.map((item) => `<option value="${escapeHtml(item)}">${escapeHtml(item)}</option>`).join("");
    object.innerHTML = sentenceHelperData.objects.map((item) => `<option value="${escapeHtml(item)}">${escapeHtml(item)}</option>`).join("");
    buildSentenceHelper(false);
}

function buildSentenceHelper(award = true) {
    const subject = document.getElementById("sentenceSubject")?.value || "I";
    const baseVerb = document.getElementById("sentenceVerb")?.value || "like";
    const object = document.getElementById("sentenceObject")?.value || "English";
    const thirdPerson = ["My friend", "My teacher", "The student"].includes(subject);
    let verb = baseVerb;
    if (thirdPerson && baseVerb === "study") verb = "studies";
    else if (thirdPerson && baseVerb === "play") verb = "plays";
    else if (thirdPerson && baseVerb === "like") verb = "likes";
    else if (thirdPerson && baseVerb === "visit") verb = "visits";
    else if (thirdPerson && baseVerb === "help") verb = "helps";
    const sentence = `${subject} ${verb} ${object}.`;
    const output = document.getElementById("sentenceHelperOutput");
    if (output) output.textContent = sentence;
    if (award) awardWritingPoints("sentence_helper", 5, "sentence-helper", false);
    return sentence;
}

function showWritingFeedback(message, tone = "") {
    const box = document.getElementById("writingFeedback");
    if (!box) return;
    box.hidden = false;
    box.className = `reading-feedback ${tone}`;
    box.textContent = message;
}

async function awardStoryPoints(activityType, points, storyId = "", completed = false) {
    let pointsToAward = points;
    storyProgress.actions += 1;
    if (storyId && !storyProgress.opened.includes(storyId) && activityType === "open") {
        storyProgress.opened.push(storyId);
    }
    if (completed && storyId && !storyProgress.completed.includes(storyId) && storyId !== "story-challenge") {
        storyProgress.completed.push(storyId);
    }
    if (storyProgress.completed.length >= 5 && !storyProgress.fiveBonus) {
        pointsToAward += 30;
        storyProgress.fiveBonus = true;
    }
    if (storyProgress.completed.length >= storiesData.length && !storyProgress.masteredBonus) {
        pointsToAward += 50;
        storyProgress.masteredBonus = true;
    }
    storyProgress.points += pointsToAward;
    saveLevelFourStoriesProgress();
    updateStoryStats();

    try {
        const response = await fetch(window.LEVEL_FOUR_PROGRESS_URL || "/api/english-foundation/progress/", {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
            body: JSON.stringify({ section: "level_four_stories", activity_type: activityType, points: pointsToAward, completed }),
        });
        const data = await response.json();
        if (data.status === "ok") {
            storyProgress.points = data.points;
            storyProgress.actions = data.actions_count;
            saveLevelFourStoriesProgress();
            updateStoryStats();
        }
    } catch {
        // TODO: integrate level_four_stories with StudentActivity leaderboard.
    }
}

function storyCard(item) {
    return `
        <article class="story-card" data-story-id="${item.id}">
            <div class="card-icon">${item.emoji}</div>
            <h3>${escapeHtml(item.title_en)}</h3>
            <p class="passage-title-ar">${escapeHtml(item.title_ar)}</p>
            <div class="passage-meta">
                <span>${escapeHtml(item.category)}</span>
                <span>${escapeHtml(item.level)}</span>
                <span>${item.word_count} words</span>
            </div>
            <div class="vocab-list">${item.vocabulary_focus.slice(0, 5).map((word) => `<span>${escapeHtml(word.split("=")[0].trim())}</span>`).join("")}</div>
            <p class="story-lesson-box">${escapeHtml(item.lesson_ar)}</p>
            <div class="passage-actions story-actions">
                <button type="button" data-story-action="open" data-id="${item.id}">افتح القصة</button>
                <button type="button" data-story-action="listen" data-id="${item.id}">استمع للقصة</button>
                <button type="button" data-story-action="slow" data-id="${item.id}">قراءة بطيئة</button>
                <button type="button" data-story-action="quiz" data-id="${item.id}">حل أسئلة الفهم</button>
                <button type="button" data-story-action="order" data-id="${item.id}">رتب الأحداث</button>
                <button type="button" data-story-action="mic" data-id="${item.id}">اقرأ بالمايك</button>
                <button type="button" data-story-action="ending" data-id="${item.id}">اكتب نهاية مختلفة</button>
            </div>
        </article>
    `;
}

function renderStoryMode() {
    const grid = document.getElementById("storyModeGrid");
    if (grid) grid.innerHTML = storiesData.map(storyCard).join("");
}

function getStory(id) {
    return storiesData.find((item) => item.id === id);
}

function openStoryModal(item, mode = "read") {
    activeStory = item;
    storyProgress.lastRead = item.title_en;
    document.getElementById("storyModal").hidden = false;
    document.getElementById("storyModalMeta").textContent = `${item.category} / ${item.level} / ${item.word_count} words`;
    document.getElementById("storyModalTitle").textContent = item.title_en;
    document.getElementById("storyFeedback").hidden = true;
    renderStoryReadMode(item);
    if (mode === "quiz") renderStoryQuiz(item);
    if (mode === "order") renderEventOrder(item);
    if (mode === "ending") renderAlternateEnding(item);
    awardStoryPoints("open", 1, item.id);
}

function renderStoryReadMode(item) {
    document.getElementById("storyModalBody").innerHTML = `
        <div class="story-text-panel">${escapeHtml(item.story_en)}</div>
        <div class="translation-text">${escapeHtml(item.story_ar)}</div>
        <h3>Vocabulary from Story</h3>
        <div class="vocab-list">${item.vocabulary_focus.map((word) => `<span>${escapeHtml(word)}</span>`).join("")}</div>
        <div class="story-lesson-box">${escapeHtml(item.lesson_ar)}</div>
        <div class="passage-actions">
            <button class="primary-action" type="button" data-story-modal-action="listen">استمع للقصة</button>
            <button type="button" data-story-modal-action="slow">قراءة بطيئة</button>
            <button type="button" data-story-modal-action="stop">إيقاف النطق</button>
            <button type="button" data-story-modal-action="quiz">حل أسئلة الفهم</button>
            <button type="button" data-story-modal-action="tf">صح أو خطأ</button>
            <button type="button" data-story-modal-action="order">رتب الأحداث</button>
            <button type="button" data-story-modal-action="missing">أكمل الكلمات</button>
            <button type="button" data-story-modal-action="vocab">طابق الكلمات</button>
            <button type="button" data-story-modal-action="mic">اقرأ بالمايك</button>
            <button type="button" data-story-modal-action="ending">اكتب نهاية مختلفة</button>
            <button type="button" data-story-modal-action="complete">إكمال القصة</button>
        </div>
        <div id="storyActivityPanel"></div>
    `;
}

function speakStory(item = activeStory, rate = 0.85) {
    if (!item) return;
    try {
        if (!("speechSynthesis" in window)) {
            showStoryFeedback("النطق غير مدعوم في هذا المتصفح.", "warn");
            return;
        }
        const utterance = new SpeechSynthesisUtterance(item.story_en);
        utterance.lang = "en-US";
        utterance.rate = rate;
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utterance);
        awardStoryPoints(rate < 0.7 ? "slow_listen" : "listen", rate < 0.7 ? 1 : 2, item.id);
    } catch {
        showStoryFeedback("تعذر تشغيل النطق الآن.", "warn");
    }
}

function speakStorySlow(item = activeStory) {
    speakStory(item, 0.6);
}

function stopStorySpeech() {
    if ("speechSynthesis" in window) window.speechSynthesis.cancel();
}

function startStoryMicPractice(item = activeStory) {
    if (!item) return;
    const speechStoryTarget = item.story_en.split(".").slice(0, 3).join(". ") + ".";
    document.getElementById("storyActivityPanel").innerHTML = `
        <div class="story-progress-box">
            <h3>اقرأ هذا الجزء بالمايك</h3>
            <p class="model-answer">${escapeHtml(speechStoryTarget)}</p>
            <div id="storySpokenText">النص المنطوق سيظهر هنا.</div>
            <div id="storyMicResult"></div>
        </div>
    `;
    SpeechService.startRecognition({
        targetText: speechStoryTarget,
        type: "story",
        section: "level_four_stories",
        level: item.level || "",
        onResult: (speechResult) => {
            const transcript = speechResult.spokenText || speechResult.spoken || "";
            document.getElementById("storySpokenText").textContent = transcript;
            const result = evaluateStoryReading(transcript, speechStoryTarget);
            SpeechService.renderResult("#storyMicResult", { ...speechResult, score: result.score, status: SpeechService.getStatus(result.score, "story") });
            showStoryFeedback(result.rating, result.score >= 60 ? "good" : "warn");
            awardStoryPoints("mic", 5, item.id, result.score >= 60);
        },
        onError: (result) => {
            SpeechService.renderResult("#storyMicResult", result);
            showStoryFeedback(result.message || SpeechService.messages.unknown, "warn");
        }
    });
    return;
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) {
        showStoryFeedback("الميكروفون غير مدعوم في هذا المتصفح، جرّب Google Chrome.", "warn");
        return;
    }
    const targetText = item.story_en.split(".").slice(0, 3).join(". ") + ".";
    document.getElementById("storyActivityPanel").innerHTML = `
        <div class="story-progress-box">
            <h3>اقرأ هذا الجزء بالمايك</h3>
            <p class="model-answer">${escapeHtml(targetText)}</p>
            <div id="storySpokenText">النص المنطوق سيظهر هنا.</div>
            <div id="storyMicResult"></div>
        </div>
    `;
    try {
        const recognition = new Recognition();
        recognition.lang = "en-US";
        recognition.interimResults = false;
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            document.getElementById("storySpokenText").textContent = transcript;
            const result = evaluateStoryReading(transcript, targetText);
            document.getElementById("storyMicResult").innerHTML = `
                <div class="writing-result-grid">
                    <span>${result.rating}</span>
                    <span>Similarity: ${result.score}%</span>
                    <span>Words: ${result.wordCount}</span>
                    <span>Missing: ${result.missingKeywords.join(", ") || "-"}</span>
                </div>
            `;
            showStoryFeedback(result.rating, result.score >= 60 ? "good" : "warn");
            awardStoryPoints("mic", 5, item.id, result.score >= 60);
        };
        recognition.onerror = () => showStoryFeedback("تعذر تشغيل المايك الآن. اسمح للمتصفح باستخدام الميكروفون ثم حاول مرة أخرى.", "warn");
        recognition.start();
    } catch {
        showStoryFeedback("تعذر بدء المايك الآن.", "warn");
    }
}

function evaluateStoryReading(transcript, targetText) {
    const spokenWords = normalizeSpeechText(transcript).split(" ").filter(Boolean);
    const targetWords = normalizeSpeechText(targetText).split(" ").filter(Boolean);
    const hits = targetWords.filter((word) => spokenWords.includes(word)).length;
    const score = targetWords.length ? Math.round((hits / targetWords.length) * 100) : 0;
    const keywords = targetWords.filter((word) => word.length > 4).slice(0, 8);
    const missingKeywords = keywords.filter((word) => !spokenWords.includes(word));
    const rating = score >= 85 ? "ممتاز" : score >= 60 ? "جيد" : "حاول مرة أخرى";
    return { score, wordCount: spokenWords.length, missingKeywords, rating };
}

function startStoryComprehension(item = activeStory) {
    renderStoryQuiz(item);
}

function renderStoryQuiz(item = activeStory) {
    document.getElementById("storyActivityPanel").innerHTML = `
        <form id="storyQuizForm">
            ${item.comprehension_questions.map((question, index) => questionBlock(question, `storyq${index}`)).join("")}
        </form>
        <button class="primary-action" type="button" id="checkStoryComprehension">تحقق من أسئلة الفهم</button>
    `;
}

function checkStoryComprehension(item = activeStory) {
    const inputs = Array.from(document.querySelectorAll("#storyQuizForm input[type='radio']:checked"));
    let correct = 0;
    inputs.forEach((input) => {
        if (normalizeText(input.value) === normalizeText(input.dataset.answer)) correct += 1;
    });
    const score = Math.round((correct / item.comprehension_questions.length) * 100);
    storyProgress.bestScore = Math.max(storyProgress.bestScore, score);
    saveLevelFourStoriesProgress();
    showStoryFeedback(`النتيجة: ${correct} / ${item.comprehension_questions.length}`, score >= 60 ? "good" : "warn");
    awardStoryPoints("comprehension", 10, item.id, score >= 60);
}

function startStoryTrueFalse(item = activeStory) {
    document.getElementById("storyActivityPanel").innerHTML = `
        <form id="storyTrueFalseForm">
            ${item.true_false_questions.map((question, index) => questionBlock({ q: question.q, a: question.a, options: ["True", "False"] }, `storytf${index}`)).join("")}
        </form>
        <button class="primary-action" type="button" id="checkStoryTrueFalse">تحقق من صح أو خطأ</button>
    `;
}

function checkStoryTrueFalse(item = activeStory) {
    const inputs = Array.from(document.querySelectorAll("#storyTrueFalseForm input[type='radio']:checked"));
    let correct = 0;
    inputs.forEach((input) => {
        if (normalizeText(input.value) === normalizeText(input.dataset.answer)) correct += 1;
    });
    const score = Math.round((correct / item.true_false_questions.length) * 100);
    storyProgress.bestScore = Math.max(storyProgress.bestScore, score);
    saveLevelFourStoriesProgress();
    showStoryFeedback(`صح أو خطأ: ${correct} / ${item.true_false_questions.length}`, score >= 60 ? "good" : "warn");
}

function startEventOrder(item = activeStory) {
    renderEventOrder(item);
}

function renderEventOrder(item = activeStory) {
    document.getElementById("storyActivityPanel").innerHTML = `
        <div class="event-order-box">
            ${item.event_order.map((eventText, index) => `
                <label>
                    <select data-event-index="${index}">
                        ${item.event_order.map((_, optionIndex) => `<option value="${optionIndex + 1}">${optionIndex + 1}</option>`).join("")}
                    </select>
                    <span>${escapeHtml(eventText)}</span>
                </label>
            `).join("")}
        </div>
        <button class="primary-action" type="button" id="checkEventOrder">تحقق من ترتيب الأحداث</button>
    `;
}

function checkEventOrder(item = activeStory) {
    const selects = Array.from(document.querySelectorAll("[data-event-index]"));
    const correct = selects.every((select, index) => Number(select.value) === index + 1);
    showStoryFeedback(correct ? "ترتيب الأحداث صحيح." : "حاول ترتيب الأحداث مرة أخرى.", correct ? "good" : "warn");
    if (correct) awardStoryPoints("event_order", 10, item.id);
}

function startMissingWords(item = activeStory) {
    document.getElementById("storyActivityPanel").innerHTML = `
        <form id="storyMissingWordsForm">
            ${item.missing_words_activity.map((entry, index) => `
                <label class="question-block">
                    <p class="model-answer">${escapeHtml(entry.prompt.split(".")[0])}.</p>
                    <input class="listening-input" type="text" data-missing-answer="${escapeHtml(entry.answer)}" placeholder="missing word">
                </label>
            `).join("")}
        </form>
        <button class="primary-action" type="button" id="checkMissingWords">تحقق من الكلمات الناقصة</button>
    `;
}

function checkMissingWords() {
    const inputs = Array.from(document.querySelectorAll("#storyMissingWordsForm input"));
    const correct = inputs.filter((input) => normalizeText(input.value) === normalizeText(input.dataset.missingAnswer)).length;
    showStoryFeedback(`الكلمات الناقصة: ${correct} / ${inputs.length}`, correct === inputs.length ? "good" : "warn");
}

function startStoryVocabularyMatch(item = activeStory) {
    document.getElementById("storyActivityPanel").innerHTML = `
        <div class="story-progress-box">
            <h3>Vocabulary from Story</h3>
            <div class="vocab-list">${item.vocabulary_focus.map((entry) => `<span>${escapeHtml(entry)}</span>`).join("")}</div>
        </div>
        <button class="primary-action" type="button" id="checkStoryVocabularyMatch">أنهيت مراجعة الكلمات</button>
    `;
}

function checkStoryVocabularyMatch(item = activeStory) {
    showStoryFeedback("تمت مراجعة كلمات القصة.", "good");
    awardStoryPoints("vocabulary", 5, item.id);
}

function renderAlternateEnding(item = activeStory) {
    document.getElementById("storyActivityPanel").innerHTML = `
        <div class="story-ending-box">
            <h3>${escapeHtml(item.alternate_ending_prompt)}</h3>
            <textarea id="alternateEndingText" placeholder="Write a different ending..."></textarea>
            <button class="primary-action" type="button" id="saveAlternateEnding">حفظ الإجابة</button>
        </div>
    `;
}

function saveAlternateEnding(item = activeStory) {
    const text = document.getElementById("alternateEndingText")?.value.trim() || "";
    if (!text) {
        showStoryFeedback("اكتب نهاية مختلفة أولا.", "warn");
        return;
    }
    storyProgress.endings.unshift({ id: item.id, text, at: new Date().toISOString() });
    storyProgress.endings = storyProgress.endings.slice(0, 20);
    saveLevelFourStoriesProgress();
    updateStoryStats();
    showStoryFeedback("تم حفظ النهاية المختلفة.", "good");
    awardStoryPoints("alternate_ending", 15, item.id);
}

function completeStory(item = activeStory) {
    showStoryFeedback("تم إكمال القصة.", "good");
    awardStoryPoints("complete_story", item.points, item.id, true);
}

function startStoryChallenge() {
    storyChallenge = { active: true, items: storiesData.slice().sort(() => Math.random() - 0.5).slice(0, 3), index: 0, score: 0, total: 0 };
    document.getElementById("storyModal").hidden = false;
    renderStoryChallengeItem();
}

function renderStoryChallengeItem() {
    const item = storyChallenge.items[storyChallenge.index];
    if (!item) {
        finishStoryChallenge();
        return;
    }
    activeStory = item;
    document.getElementById("storyModalMeta").textContent = `Story Challenge ${storyChallenge.index + 1} / ${storyChallenge.items.length}`;
    document.getElementById("storyModalTitle").textContent = item.title_en;
    document.getElementById("storyFeedback").hidden = true;
    document.getElementById("storyModalBody").innerHTML = `
        <div class="story-text-panel">${escapeHtml(item.story_en.split(".").slice(0, 3).join(". "))}.</div>
        <form id="storyChallengeForm">
            ${questionBlock(item.comprehension_questions[0], "challengeq")}
            ${questionBlock({ q: item.true_false_questions[0].q, a: item.true_false_questions[0].a, options: ["True", "False"] }, "challengetf")}
            <fieldset class="question-block">
                <p>Choose the first event.</p>
                <select class="listening-input" id="challengeFirstEvent">
                    ${item.event_order.map((eventText, index) => `<option value="${index}">${escapeHtml(eventText)}</option>`).join("")}
                </select>
            </fieldset>
            <fieldset class="question-block">
                <p>Choose the second event.</p>
                <select class="listening-input" id="challengeSecondEvent">
                    ${item.event_order.map((eventText, index) => `<option value="${index}">${escapeHtml(eventText)}</option>`).join("")}
                </select>
            </fieldset>
        </form>
        <button class="primary-action" type="button" id="nextStoryChallenge">تحقق ثم التالي</button>
    `;
}

function finishStoryChallenge() {
    const percent = storyChallenge.total ? Math.round((storyChallenge.score / storyChallenge.total) * 100) : 0;
    const rating = percent >= 85 ? "ممتاز" : percent >= 60 ? "جيد" : "يحتاج تدريب";
    storyProgress.bestScore = Math.max(storyProgress.bestScore, percent);
    saveLevelFourStoriesProgress();
    updateStoryStats();
    document.getElementById("storyModalMeta").textContent = "Sprint Level 4.5";
    document.getElementById("storyModalTitle").textContent = "تحدي القصص";
    document.getElementById("storyModalBody").innerHTML = `
        <div class="story-progress-box">
            <h3>${rating} - ${percent}%</h3>
            <p>النتيجة النهائية: ${storyChallenge.score} / ${storyChallenge.total}</p>
            <button class="primary-action" type="button" id="startStoryChallengeAgain">إعادة تحدي القصص</button>
        </div>
    `;
    showStoryFeedback("تم إكمال تحدي القصص.", percent >= 60 ? "good" : "warn");
    awardStoryPoints("story_challenge", 25, "story-challenge", false);
    storyChallenge = { active: false, items: [], index: 0, score: 0, total: 0 };
}

function scoreStoryChallengeItem() {
    const item = activeStory;
    if (!item) return;
    const selected = Array.from(document.querySelectorAll("#storyChallengeForm input[type='radio']:checked"));
    selected.forEach((input) => {
        storyChallenge.total += 1;
        if (normalizeText(input.value) === normalizeText(input.dataset.answer)) storyChallenge.score += 1;
    });
    storyChallenge.total += 2;
    if (Number(document.getElementById("challengeFirstEvent")?.value) === 0) storyChallenge.score += 1;
    if (Number(document.getElementById("challengeSecondEvent")?.value) === 1) storyChallenge.score += 1;
}

function showStoryFeedback(message, tone = "") {
    const box = document.getElementById("storyFeedback");
    if (!box) return;
    box.hidden = false;
    box.className = `reading-feedback ${tone}`;
    box.textContent = message;
}

function buildLevelFourExamQuestions() {
    const makeChoice = (section, item, index) => ({
        id: `${section}-${index}`,
        section,
        type: "choice",
        q: item.q,
        options: item.options,
        a: item.a,
        audio_text: item.audio_text || "",
    });
    return [
        ...levelFourExamData.vocabulary.map((item, index) => makeChoice("vocabulary", item, index)),
        ...levelFourExamData.grammar.map((item, index) => makeChoice("grammar", item, index)),
        ...levelFourExamData.reading.map((item, index) => makeChoice("reading", item, index)),
        ...levelFourExamData.listening.map((item, index) => makeChoice("listening", item, index)),
        {
            id: "speaking-task",
            section: "speaking",
            type: "speaking",
            q: levelFourExamData.speaking.prompt,
        },
        {
            id: "writing-task",
            section: "writing",
            type: "writing",
            q: levelFourExamData.writing.prompt,
        },
    ];
}

function renderLevelFourExam() {
    updateExamStats();
}

function startLevelFourExam() {
    activeExam = {
        questions: buildLevelFourExamQuestions(),
        index: 0,
        answers: loadExamAnswers(),
        speakingTranscript: loadExamAnswers()["speaking-task"] || "",
        result: null,
    };
    document.getElementById("examModal").hidden = false;
    document.getElementById("examFeedback").hidden = true;
    awardExamPoints("start_exam", 5);
    renderExamQuestion();
}

function currentExamQuestion() {
    return activeExam.questions[activeExam.index];
}

function examSectionLabel(section) {
    const labels = {
        vocabulary: "Vocabulary",
        grammar: "Grammar",
        reading: "Reading",
        listening: "Listening",
        speaking: "Speaking",
        writing: "Writing",
    };
    return labels[section] || section;
}

function renderExamQuestion() {
    const question = currentExamQuestion();
    if (!question) return renderExamResult(activeExam.result || calculateExamScore());
    const current = activeExam.index + 1;
    const total = activeExam.questions.length;
    document.getElementById("examModalMeta").textContent = `Level 4 Exam | ${examSectionLabel(question.section)} | ${current} / ${total}`;
    document.getElementById("examModalTitle").textContent = "اختبار المستوى الرابع";
    document.getElementById("examFeedback").hidden = true;
    document.getElementById("examModalBody").innerHTML = `
        <div class="exam-progress-line">
            <span style="width:${Math.round((current / total) * 100)}%"></span>
        </div>
        <div class="exam-question-card">
            <div class="exam-question-meta">
                <span>${examSectionLabel(question.section)}</span>
                <strong>Question ${current} / ${total}</strong>
            </div>
            ${examQuestionBody(question)}
        </div>
        <div class="exam-nav">
            <button type="button" data-exam-action="previous" ${activeExam.index === 0 ? "disabled" : ""}>السابق</button>
            <button type="button" data-exam-action="next">${activeExam.index === total - 1 ? "مراجعة" : "التالي"}</button>
            <button class="primary-action" type="button" data-exam-action="finish">إنهاء الاختبار</button>
        </div>
    `;
}

function examQuestionBody(question) {
    if (question.type === "speaking") {
        return `
            <h3>${escapeHtml(question.q)}</h3>
            <p class="model-answer">${escapeHtml(levelFourExamData.speaking.model)}</p>
            <div class="passage-actions">
                <button class="primary-action" type="button" data-exam-action="speak">ابدأ المايك</button>
            </div>
            <div class="spoken-text-panel" id="examSpeakingTranscript">${escapeHtml(activeExam.answers[question.id] || activeExam.speakingTranscript || "لم يتم تسجيل إجابة بعد.")}</div>
            <p class="exam-note">إذا كان المايك غير مدعوم، يمكنك إكمال الاختبار بدون درجة التحدث الآن.</p>
        `;
    }
    if (question.type === "writing") {
        return `
            <h3>${escapeHtml(question.q)}</h3>
            <textarea class="writing-textarea" id="examWritingAnswer" rows="8" placeholder="Write your paragraph here.">${escapeHtml(activeExam.answers[question.id] || "")}</textarea>
            <div class="writing-result-grid">
                <span>Minimum: ${levelFourExamData.writing.min_words} words</span>
                <span>Target: ${levelFourExamData.writing.target_words.join(", ")}</span>
            </div>
        `;
    }
    return `
        ${question.section === "reading" && question.id === "reading-0" ? `<div class="passage-text">${escapeHtml(levelFourExamData.readingText)}</div>` : ""}
        ${question.section === "listening" ? `<div class="passage-actions"><button class="primary-action" type="button" data-exam-action="listen">استمع</button></div>` : ""}
        <fieldset class="question-block">
            <p>${escapeHtml(question.q)}</p>
            <div class="option-grid">
                ${question.options.map((option) => `
                    <label>
                        <input type="radio" name="examAnswer" value="${escapeHtml(option)}" ${activeExam.answers[question.id] === option ? "checked" : ""}>
                        <span>${escapeHtml(option)}</span>
                    </label>
                `).join("")}
            </div>
        </fieldset>
    `;
}

function saveExamAnswer() {
    const question = currentExamQuestion();
    if (!question) return true;
    if (question.type === "choice") {
        const selected = document.querySelector("#examModalBody input[name='examAnswer']:checked");
        if (selected) activeExam.answers[question.id] = selected.value;
    }
    if (question.type === "speaking") {
        activeExam.answers[question.id] = activeExam.speakingTranscript || activeExam.answers[question.id] || "";
    }
    if (question.type === "writing") {
        activeExam.answers[question.id] = document.getElementById("examWritingAnswer")?.value || "";
    }
    try {
        localStorage.setItem("level_four_exam_answers", JSON.stringify(activeExam.answers));
    } catch {
        // TODO: keep level_four_exam answers in StudentActivity when the exam API is expanded.
    }
    return true;
}

function loadExamAnswers() {
    try {
        return JSON.parse(localStorage.getItem("level_four_exam_answers") || "{}");
    } catch {
        return {};
    }
}

function isExamQuestionAnswered(question) {
    if (question.type === "speaking") return true;
    const answer = activeExam.answers[question.id];
    return String(answer || "").trim().length > 0;
}

function nextExamQuestion() {
    saveExamAnswer();
    const question = currentExamQuestion();
    if (question && !isExamQuestionAnswered(question)) {
        showExamFeedback("أجب على السؤال قبل الانتقال.", "warn");
        return;
    }
    activeExam.index = Math.min(activeExam.questions.length - 1, activeExam.index + 1);
    renderExamQuestion();
}

function previousExamQuestion() {
    saveExamAnswer();
    activeExam.index = Math.max(0, activeExam.index - 1);
    renderExamQuestion();
}

function finishLevelFourExam() {
    saveExamAnswer();
    const unanswered = activeExam.questions.filter((question) => !isExamQuestionAnswered(question));
    if (unanswered.length) {
        showExamFeedback(`باقي ${unanswered.length} سؤال/مهمة بدون إجابة. يمكنك إكمالها قبل الإنهاء.`, "warn");
        return;
    }
    const result = calculateExamScore();
    activeExam.result = result;
    examProgress.lastScore = result.finalScore;
    examProgress.bestScore = Math.max(examProgress.bestScore, result.finalScore);
    try {
        localStorage.setItem("level_four_exam_result", JSON.stringify(result));
    } catch {
        // TODO: integrate level_four_exam_result with StudentActivity leaderboard.
    }
    saveLevelFourExamProgress();
    updateExamStats();
    awardExamPoints("complete_vocabulary", 10);
    awardExamPoints("complete_grammar", 10);
    awardExamPoints("complete_reading", 15);
    awardExamPoints("complete_listening", 15);
    awardExamPoints("attempt_speaking", 15);
    awardExamPoints("complete_writing", 15);
    awardExamPoints("finish_exam", 50);
    if (result.finalScore >= 80) awardExamPoints("pass_exam_80", 100);
    renderExamResult(result);
}

function calculateExamScore() {
    const sections = {
        vocabulary: scoreVocabularySection(),
        grammar: scoreGrammarSection(),
        reading: scoreReadingSection(),
        listening: scoreListeningSection(),
        speaking: scoreSpeakingSection(),
        writing: scoreWritingSection(),
    };
    const rawTotal = Object.values(sections).reduce((sum, item) => sum + item.score, 0);
    const finalScore = Math.min(100, Math.round(rawTotal));
    const rating = finalScore < 60 ? "يحتاج مراجعة" : finalScore < 80 ? "جيد" : finalScore < 90 ? "ممتاز" : "متقن";
    const recommendations = getExamRecommendations(sections);
    return { sections, finalScore, percent: finalScore, rating, recommendations, date: new Date().toISOString() };
}

function scoreChoiceExamSection(sectionName, questions, maxScore) {
    let correct = 0;
    questions.forEach((question, index) => {
        const answer = activeExam.answers[`${sectionName}-${index}`];
        if (normalizeText(answer) === normalizeText(question.a)) correct += 1;
    });
    const score = questions.length ? (correct / questions.length) * maxScore : 0;
    return { score: Math.round(score * 10) / 10, correct, total: questions.length, max: maxScore };
}

function scoreVocabularySection() {
    return scoreChoiceExamSection("vocabulary", levelFourExamData.vocabulary, levelFourExamData.weights.vocabulary);
}

function scoreGrammarSection() {
    return scoreChoiceExamSection("grammar", levelFourExamData.grammar, levelFourExamData.weights.grammar);
}

function scoreReadingSection() {
    return scoreChoiceExamSection("reading", levelFourExamData.reading, levelFourExamData.weights.reading);
}

function scoreListeningSection() {
    return scoreChoiceExamSection("listening", levelFourExamData.listening, levelFourExamData.weights.listening);
}

function scoreSpeakingSection() {
    const transcript = activeExam.answers["speaking-task"] || activeExam.speakingTranscript || "";
    const spoken = normalizeSpeechText(transcript);
    const keywords = levelFourExamData.speaking.keywords;
    const used = keywords.filter((keyword) => spoken.includes(normalizeSpeechText(keyword)));
    const similarity = similarityScore(transcript, levelFourExamData.speaking.model);
    const keywordScore = keywords.length ? (used.length / keywords.length) * 55 : 0;
    const wordScore = Math.min(25, countSpokenWords(transcript) * 3);
    const raw = Math.min(100, Math.round(keywordScore + wordScore + similarity * 0.2));
    return { score: Math.round((raw / 100) * levelFourExamData.weights.speaking), correct: used.length, total: keywords.length, max: levelFourExamData.weights.speaking, raw, transcript };
}

function scoreWritingSection() {
    const text = activeExam.answers["writing-task"] || "";
    const result = evaluateExamWriting(text);
    return { score: Math.round((result.score / 100) * levelFourExamData.weights.writing), correct: result.usedTargetWords.length, total: result.totalTargetWords, max: levelFourExamData.weights.writing, raw: result.score, result };
}

function evaluateExamWriting(text) {
    const wordCount = countWritingWords(text);
    const sentenceCount = countWritingSentences(text);
    const target = checkTargetWords(text, levelFourExamData.writing.target_words);
    const hasPunctuation = checkPunctuation(text);
    const hasCapital = checkCapitalLetters(text);
    let score = 0;
    score += Math.min(35, Math.round((wordCount / levelFourExamData.writing.min_words) * 35));
    score += Math.round((target.used.length / levelFourExamData.writing.target_words.length) * 25);
    if (sentenceCount >= 3) score += 15;
    if (hasPunctuation) score += 15;
    if (hasCapital) score += 10;
    score = Math.min(100, score);
    return { score, wordCount, sentenceCount, usedTargetWords: target.used, totalTargetWords: levelFourExamData.writing.target_words.length, hasPunctuation, hasCapital };
}

function renderExamResult(result) {
    const sectionRows = Object.entries(result.sections).map(([key, item]) => `
        <tr>
            <td>${examSectionLabel(key)}</td>
            <td>${item.score} / ${item.max}</td>
            <td>${item.total ? `${item.correct} / ${item.total}` : "-"}</td>
        </tr>
    `).join("");
    document.getElementById("examModalMeta").textContent = "Level 4 Exam Result";
    document.getElementById("examModalTitle").textContent = "نتيجة اختبار المستوى الرابع";
    document.getElementById("examFeedback").hidden = true;
    document.getElementById("examModalBody").innerHTML = `
        <div class="exam-result-dashboard ${result.finalScore >= 80 ? "pass" : "fail"}">
            <div class="score-circle">${result.finalScore}%</div>
            <h3>${result.rating}</h3>
            <p>Final score: ${result.finalScore} / 100</p>
        </div>
        <table class="exam-score-table">
            <thead><tr><th>Section</th><th>Score</th><th>Correct</th></tr></thead>
            <tbody>${sectionRows}</tbody>
        </table>
        <div class="exam-recommendations">
            <h3>نقاط القوة</h3>
            <ul>${result.recommendations.strengths.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
            <h3>توصيات المراجعة</h3>
            <ul>${result.recommendations.reviews.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
        </div>
        ${result.finalScore >= 80 ? renderLevelFourCertificate(result) : `<div class="exam-certificate-lock">تحتاج إلى 80% أو أكثر للحصول على شهادة المستوى الرابع.</div>`}
        <div class="exam-nav">
            <button type="button" data-exam-action="restart">إعادة الاختبار</button>
            ${result.finalScore >= 80 ? `<button class="primary-action" type="button" data-exam-action="print-certificate">طباعة الشهادة</button>` : ""}
        </div>
    `;
}

function getExamRecommendations(sections) {
    const strengths = [];
    const reviews = [];
    Object.entries(sections).forEach(([key, item]) => {
        const percent = item.max ? Math.round((item.score / item.max) * 100) : 0;
        if (percent >= 80) strengths.push(`${examSectionLabel(key)} ممتاز.`);
        if (percent < 70) {
            if (key === "grammar") reviews.push("راجع قسم القواعد التأسيسية.");
            else if (key === "listening") reviews.push("راجع Listening Practice.");
            else if (key === "speaking") reviews.push("تدرب على Speaking Missions.");
            else if (key === "writing") reviews.push("تدرب على Writing Practice.");
            else reviews.push(`راجع ${examSectionLabel(key)} قبل إعادة الاختبار.`);
        }
    });
    if (!strengths.length) strengths.push("إكمال الاختبار خطوة ممتازة، ونتيجتك ستتحسن مع المراجعة.");
    if (!reviews.length) reviews.push("استمر بالمراجعة الخفيفة وحافظ على التدريب اليومي.");
    return { strengths, reviews };
}

function renderLevelFourCertificate(result) {
    let saved = {};
    try {
        saved = JSON.parse(localStorage.getItem("level_four_certificate") || "{}");
    } catch {
        saved = {};
    }
    const studentName = saved.studentName || "";
    const date = new Date(result.date || Date.now()).toLocaleDateString("ar-SA");
    return `
        <section class="level-four-certificate" id="levelFourCertificate">
            <p class="eyebrow">Reading & Real English</p>
            <h2>شهادة إتقان المستوى الرابع</h2>
            <label class="certificate-name-label">
                اكتب اسم الطالب على الشهادة
                <input id="certificateStudentName" type="text" value="${escapeHtml(studentName)}" placeholder="اسم الطالب">
            </label>
            <p>يشهد الموقع أن الطالب <strong id="certificateNamePreview">${escapeHtml(studentName || "................")}</strong> قد أتم المستوى الرابع Reading & Real English بنجاح.</p>
            <div class="writing-result-grid">
                <span>Score: ${result.finalScore} / 100</span>
                <span>Rating: ${escapeHtml(result.rating)}</span>
                <span>Date: ${escapeHtml(date)}</span>
            </div>
            <p class="certificate-signature">Smart Learning</p>
        </section>
    `;
}

function printLevelFourCertificate() {
    saveLevelFourCertificate();
    window.print();
}

function saveLevelFourCertificate() {
    const result = activeExam.result || calculateExamScore();
    const studentName = document.getElementById("certificateStudentName")?.value || "";
    const certificate = {
        studentName,
        score: result.finalScore,
        rating: result.rating,
        date: result.date,
    };
    try {
        localStorage.setItem("level_four_certificate", JSON.stringify(certificate));
    } catch {
        // TODO: integrate level_four_certificate with StudentActivity leaderboard.
    }
    const preview = document.getElementById("certificateNamePreview");
    if (preview) preview.textContent = studentName || "................";
    if (result.finalScore >= 80 && !examProgress.certificate) {
        examProgress.certificate = true;
        awardExamPoints("level_four_certificate", 200);
    }
    saveLevelFourExamProgress();
}

function startExamSpeakingRecognition() {
    SpeechService.startRecognition({
        targetText: "speaking task",
        type: "long_sentence",
        section: "level_four_exam",
        level: "exam",
        onStart: () => showExamFeedback(SpeechService.messages.listening, "warn"),
        onResult: (result) => {
            activeExam.speakingTranscript = result.spokenText || result.spoken || "";
            activeExam.answers["speaking-task"] = activeExam.speakingTranscript;
            const panel = document.getElementById("examSpeakingTranscript");
            if (panel) panel.textContent = activeExam.speakingTranscript;
            saveExamAnswer();
            showExamFeedback("تم تسجيل إجابة التحدث.", "good");
        },
        onError: (result) => showExamFeedback(result.message || "يمكنك المحاولة مرة أخرى أو إكمال الاختبار.", "warn")
    });
    return;
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) {
        activeExam.speakingTranscript = activeExam.speakingTranscript || "";
        activeExam.answers["speaking-task"] = activeExam.speakingTranscript;
        saveExamAnswer();
        showExamFeedback("الميكروفون غير مدعوم، يمكنك إكمال الاختبار بدون درجة التحدث الآن.", "warn");
        return;
    }
    try {
        const recognition = new Recognition();
        recognition.lang = "en-US";
        recognition.interimResults = false;
        showExamFeedback("استمع الآن. تحدث بالإنجليزية بوضوح.", "warn");
        recognition.onresult = (event) => {
            activeExam.speakingTranscript = event.results[0][0].transcript;
            activeExam.answers["speaking-task"] = activeExam.speakingTranscript;
            const panel = document.getElementById("examSpeakingTranscript");
            if (panel) panel.textContent = activeExam.speakingTranscript;
            saveExamAnswer();
            showExamFeedback("تم تسجيل إجابة التحدث.", "good");
        };
        recognition.onerror = () => showExamFeedback("تعذر تشغيل المايك الآن. يمكنك المحاولة مرة أخرى أو إكمال الاختبار.", "warn");
        recognition.start();
    } catch {
        showExamFeedback("تعذر تشغيل المايك الآن. يمكنك إكمال الاختبار.", "warn");
    }
}

async function awardExamPoints(activityType, points, completed = true) {
    if (!Array.isArray(examProgress.awarded)) examProgress.awarded = [];
    if (examProgress.awarded.includes(activityType)) return;
    examProgress.awarded.push(activityType);
    examProgress.actions += 1;
    examProgress.points += points;
    saveLevelFourExamProgress();
    updateExamStats();
    try {
        const response = await fetch(window.LEVEL_FOUR_PROGRESS_URL || "/api/english-foundation/progress/", {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
            body: JSON.stringify({ section: "level_four_exam", activity_type: activityType, points, completed }),
        });
        const data = await response.json();
        if (data.status === "ok") {
            examProgress.points = data.points;
            examProgress.actions = data.actions_count;
            saveLevelFourExamProgress();
            updateExamStats();
        }
    } catch {
        // TODO: integrate level_four_exam with StudentActivity leaderboard.
    }
}

function showExamFeedback(message, tone = "") {
    const box = document.getElementById("examFeedback");
    if (!box) return;
    box.hidden = false;
    box.className = `reading-feedback ${tone}`;
    box.textContent = message;
}

function openLevelFourSection(key) {
    const section = levelFourSections[key];
    if (!section) return;
    if (!levelFourProgress.opened.includes(key)) levelFourProgress.opened.push(key);
    levelFourProgress.points += section.points;
    levelFourProgress.actions += 1;
    saveLevelFourProgress();
    updateLevelFourStats();

    document.querySelectorAll(".tabs button").forEach((button) => {
        button.classList.toggle("active", button.dataset.target === key);
    });
    document.getElementById("levelFourDetail").innerHTML = `
        <h2>${section.title}</h2>
        <p><strong>${section.ar}</strong></p>
        <p>${section.note}</p>
        <ul class="content-list">${section.items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
    `;
    if (key === "reading") {
        document.getElementById("readingPassagesSection").scrollIntoView({ behavior: "smooth", block: "start" });
    }
    if (key === "listening") {
        document.getElementById("listeningPracticeSection").scrollIntoView({ behavior: "smooth", block: "start" });
    }
    if (key === "speaking") {
        document.getElementById("speakingMissionsSection").scrollIntoView({ behavior: "smooth", block: "start" });
    }
    if (key === "writing") {
        document.getElementById("writingPracticeSection").scrollIntoView({ behavior: "smooth", block: "start" });
    }
    if (key === "stories") {
        document.getElementById("storyModeSection").scrollIntoView({ behavior: "smooth", block: "start" });
    }
    if (key === "exam") {
        document.getElementById("levelFourExamSection").scrollIntoView({ behavior: "smooth", block: "start" });
    }
}

function getPassage(id) {
    return readingPassages.find((item) => item.id === id);
}

function openReadingModal(item, mode) {
    document.getElementById("readingModal").hidden = false;
    document.getElementById("readingModalMeta").textContent = `${item.category} / ${item.level} / ${item.reading_speed_words} words`;
    document.getElementById("readingModalTitle").textContent = item.title_en;
    document.getElementById("readingFeedback").hidden = true;
    if (mode === "read") renderReadMode(item);
    if (mode === "quiz") renderQuizMode(item);
    if (mode === "speed") renderSpeedMode(item);
}

function renderReadMode(item) {
    document.getElementById("readingModalBody").innerHTML = `
        <div class="passage-text">${escapeHtml(item.passage_en)}</div>
        <div class="translation-text">${escapeHtml(item.passage_ar)}</div>
        <h3>Vocabulary Focus</h3>
        <div class="vocab-list">${item.vocabulary_focus.map((word) => `<span>${escapeHtml(word)}</span>`).join("")}</div>
        <h3>Sentence Order</h3>
        <div class="sentence-order-list">${item.sentence_order.map((sentence, index) => `<div>${index + 1}. ${escapeHtml(sentence)}</div>`).join("")}</div>
        <p><strong>Speaking prompt:</strong> ${escapeHtml(item.speaking_prompt)}</p>
    `;
    awardReadingPoints("open", 1, item.id);
}

function renderQuizMode(item) {
    document.getElementById("readingModalBody").innerHTML = `
        <form id="readingQuizForm">
            ${item.comprehension_questions.map((question, index) => questionBlock(question, `c${index}`)).join("")}
            ${item.true_false_questions.map((question, index) => questionBlock({ q: question.q, a: question.a, options: ["True", "False"] }, `t${index}`)).join("")}
        </form>
        <button class="primary-action" type="button" id="checkReadingQuiz">تصحيح أسئلة الفهم</button>
    `;
}

function questionBlock(question, name) {
    return `
        <fieldset class="question-block">
            <p>${escapeHtml(question.q)}</p>
            <div class="option-grid">
                ${question.options.map((option) => `
                    <label>
                        <input type="radio" name="${name}" value="${escapeHtml(option)}" data-answer="${escapeHtml(question.a)}">
                        <span>${escapeHtml(option)}</span>
                    </label>
                `).join("")}
            </div>
        </fieldset>
    `;
}

function checkReadingQuiz(item) {
    const inputs = Array.from(document.querySelectorAll("#readingQuizForm input[type='radio']:checked"));
    let correct = 0;
    inputs.forEach((input) => {
        if (normalizeText(input.value) === normalizeText(input.dataset.answer)) correct += 1;
    });
    const total = item.comprehension_questions.length + item.true_false_questions.length;
    showReadingFeedback(`النتيجة: ${correct} / ${total}`, correct >= 7 ? "good" : "warn");
    if (correct >= 7) awardReadingPoints("exercise", 10, item.id, true);
}

function renderSpeedMode(item) {
    activeSpeed = { id: item.id, title: item.title_en, words: item.reading_speed_words, start: 0 };
    document.getElementById("readingModalBody").innerHTML = `
        <div class="passage-text">${escapeHtml(item.passage_en)}</div>
        <div class="speed-box">
            <span>Words: <strong>${item.reading_speed_words}</strong></span>
            <button class="primary-action" type="button" id="startSpeedTest">ابدأ المؤقت</button>
            <button type="button" id="finishSpeedTest">أنهيت القراءة</button>
        </div>
    `;
}

function startSpeedTest() {
    activeSpeed.start = Date.now();
    showReadingFeedback("بدأ المؤقت. اقرأ القطعة ثم اضغط أنهيت القراءة.", "warn");
}

function finishSpeedTest() {
    if (!activeSpeed?.start) {
        showReadingFeedback("اضغط ابدأ المؤقت أولا.", "warn");
        return;
    }
    const seconds = Math.max(1, Math.round((Date.now() - activeSpeed.start) / 1000));
    const wpm = Math.round((activeSpeed.words / seconds) * 60);
    const rating = wpm < 50 ? "يحتاج تدريب" : wpm <= 90 ? "جيد" : "ممتاز";
    showReadingFeedback(`الوقت: ${seconds} ثانية | WPM: ${wpm} | التقييم: ${rating}`, wpm > 90 ? "good" : "warn");
    awardReadingPoints("speed", 10, activeSpeed.id, true);
}

function speakText(text, rate = 0.9) {
    try {
        if (!("speechSynthesis" in window)) {
            showReadingFeedback("النطق غير مدعوم في هذا المتصفح.", "warn");
            return;
        }
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = "en-US";
        utterance.rate = rate;
        window.speechSynthesis.speak(utterance);
    } catch {
        showReadingFeedback("تعذر تشغيل النطق الآن.", "warn");
    }
}

function startMicReading(item) {
    SpeechService.startRecognition({
        targetText: item.passage_en,
        type: "story",
        section: "level_four_reading",
        level: item.level || "",
        onStart: () => showReadingFeedback(SpeechService.messages.listening, "warn"),
        onResult: (result) => {
            const transcript = result.spokenText || result.spoken || "";
            const score = similarityScore(transcript, item.passage_en);
            showReadingFeedback(`قرأت: ${transcript} | تقييم تقريبي: ${score}%`, score >= 60 ? "good" : "warn");
            awardReadingPoints("mic", 5, item.id, score >= 60);
        },
        onError: (result) => showReadingFeedback(result.message || SpeechService.messages.unknown, "warn")
    });
    return;
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) {
        showReadingFeedback("الميكروفون غير مدعوم في هذا المتصفح، جرب Google Chrome.", "warn");
        return;
    }
    const recognition = new Recognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        const score = similarityScore(transcript, item.passage_en);
        showReadingFeedback(`قرأت: ${transcript} | تقييم تقريبي: ${score}%`, score >= 60 ? "good" : "warn");
        awardReadingPoints("mic", 5, item.id, score >= 60);
    };
    recognition.onerror = () => showReadingFeedback("تعذر تشغيل المايك الآن. اسمح للمتصفح باستخدام الميكروفون ثم حاول مرة أخرى.", "warn");
    recognition.start();
}

function similarityScore(source, target) {
    const sourceWords = normalizeText(source).split(" ").filter(Boolean);
    const targetWords = normalizeText(target).split(" ").filter(Boolean).slice(0, 40);
    if (!sourceWords.length || !targetWords.length) return 0;
    const hits = targetWords.filter((word) => sourceWords.includes(word)).length;
    return Math.round((hits / targetWords.length) * 100);
}

function normalizeText(value) {
    return String(value || "").toLowerCase().replace(/[^\w\s']/g, "").replace(/\s+/g, " ").trim();
}

function showReadingFeedback(message, tone = "") {
    const box = document.getElementById("readingFeedback");
    box.hidden = false;
    box.className = `reading-feedback ${tone}`;
    box.textContent = message;
}

function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;",
    })[char]);
}

document.addEventListener("DOMContentLoaded", () => {
    const levelFourMode = document.body.dataset.levelFourSection || "overview";
    initLevelFourTheme();
    loadLevelFourProgress();
    loadLevelFourListeningProgress();
    loadLevelFourSpeakingProgress();
    loadLevelFourWritingProgress();
    loadLevelFourStoriesProgress();
    loadLevelFourExamProgress();
    if (levelFourMode === "reading") renderReadingPassages();
    if (levelFourMode === "listening") renderListeningPractice();
    if (levelFourMode === "speaking") renderSpeakingMissions();
    if (levelFourMode === "writing") {
        renderWritingPractice();
        setupSentenceHelper();
    }
    if (levelFourMode === "stories") renderStoryMode();
    if (levelFourMode === "exam") renderLevelFourExam();
    updateLevelFourStats();
    updateReadingStats();
    updateListeningStats();
    updateSpeakingStats();
    updateWritingStats();
    updateStoryStats();
    updateExamStats();

    document.addEventListener("click", (event) => {
        if (event.target.closest("[data-level-four-theme-toggle]")) {
            toggleLevelFourTheme();
            return;
        }
        const sectionButton = event.target.closest("[data-open-section]");
        if (sectionButton) {
            openLevelFourSection(sectionButton.dataset.openSection);
            return;
        }
        const tabButton = event.target.closest("[data-target]");
        if (tabButton) {
            openLevelFourSection(tabButton.dataset.target);
            return;
        }
        const readingButton = event.target.closest("[data-reading-action]");
        if (readingButton) {
            const item = getPassage(readingButton.dataset.id);
            if (!item) return;
            const action = readingButton.dataset.readingAction;
            if (action === "read") openReadingModal(item, "read");
            if (action === "quiz") openReadingModal(item, "quiz");
            if (action === "speed") openReadingModal(item, "speed");
            if (action === "listen") {
                speakText(item.passage_en);
                awardReadingPoints("listen", 1, item.id);
            }
            if (action === "slow") {
                speakText(item.passage_en, 0.65);
                awardReadingPoints("listen", 1, item.id);
            }
            if (action === "mic") {
                openReadingModal(item, "read");
                startMicReading(item);
            }
            return;
        }
        const listeningButton = event.target.closest("[data-listening-action]");
        if (listeningButton) {
            const item = getListeningItem(listeningButton.dataset.id);
            if (!item) return;
            const action = listeningButton.dataset.listeningAction;
            if (action === "listen" || action === "replay") {
                speakListeningText(item);
                awardListeningPoints("listen", 1, item.id);
            }
            if (action === "slow") {
                speakListeningSlow(item);
                awardListeningPoints("slow_listen", 1, item.id);
            }
            if (action === "solve") {
                openListeningModal(item);
            }
            if (action === "review") {
                activeListeningItem = item;
                addListeningReview(item);
            }
            return;
        }
        const speakingButton = event.target.closest("[data-speaking-action]");
        if (speakingButton) {
            const item = getSpeakingMission(speakingButton.dataset.id);
            if (!item) return;
            const action = speakingButton.dataset.speakingAction;
            if (action === "open") openSpeakingModal(item);
            if (action === "listen") speakModelAnswer(item);
            if (action === "slow") speakModelSlow(item);
            if (action === "mic") {
                openSpeakingModal(item);
                startSpeakingRecognition(item);
            }
            if (action === "help") {
                openSpeakingModal(item);
                showSpeakingFeedback(`الكلمات المساعدة: ${item.helpful_words.join(", ")}`, "good");
            }
            if (action === "review") {
                activeSpeakingMission = item;
                addSpeakingReview(item);
            }
            return;
        }
        const writingButton = event.target.closest("[data-writing-action]");
        if (writingButton) {
            const item = getWritingTask(writingButton.dataset.id);
            if (!item) return;
            const action = writingButton.dataset.writingAction;
            if (action === "open" || action === "start") openWritingModal(item);
            if (action === "model") {
                openWritingModal(item);
                toggleModelAnswer();
            }
            if (action === "save") {
                openWritingModal(item);
                saveWritingAttempt(item, writingTextValue());
            }
            if (action === "review") addWritingReview(item);
            return;
        }
        const storyButton = event.target.closest("[data-story-action]");
        if (storyButton) {
            const item = getStory(storyButton.dataset.id);
            if (!item) return;
            const action = storyButton.dataset.storyAction;
            if (action === "open") openStoryModal(item);
            if (action === "listen") speakStory(item);
            if (action === "slow") speakStorySlow(item);
            if (action === "quiz") openStoryModal(item, "quiz");
            if (action === "order") openStoryModal(item, "order");
            if (action === "mic") {
                openStoryModal(item);
                startStoryMicPractice(item);
            }
            if (action === "ending") openStoryModal(item, "ending");
            return;
        }
        if (event.target.matches("#startLevelFourExam")) {
            startLevelFourExam();
            return;
        }
        const examButton = event.target.closest("[data-exam-action]");
        if (examButton) {
            const action = examButton.dataset.examAction;
            if (action === "previous") previousExamQuestion();
            if (action === "next") nextExamQuestion();
            if (action === "finish") finishLevelFourExam();
            if (action === "listen") {
                const question = currentExamQuestion();
                if (question?.audio_text) {
                    speakText(question.audio_text);
                    showExamFeedback("استمع للجملة ثم اختر الإجابة.", "good");
                }
            }
            if (action === "speak") startExamSpeakingRecognition();
            if (action === "restart") startLevelFourExam();
            if (action === "print-certificate") printLevelFourCertificate();
            return;
        }
        const listeningModalButton = event.target.closest("[data-listening-modal-action]");
        if (listeningModalButton) {
            const action = listeningModalButton.dataset.listeningModalAction;
            if (action === "listen") speakListeningText();
            if (action === "slow") speakListeningSlow();
            if (action === "retry" && activeListeningItem) openListeningModal(activeListeningItem);
            if (action === "next") {
                const currentIndex = listeningPracticeData.findIndex((item) => item.id === activeListeningItem?.id);
                const nextItem = listeningPracticeData[(currentIndex + 1) % listeningPracticeData.length];
                openListeningModal(nextItem);
            }
            if (action === "quick-next") {
                if (!listeningQuickQuiz.answered) checkListeningAnswer(activeListeningItem);
                listeningQuickQuiz.index += 1;
                renderListeningQuickQuizItem();
            }
            return;
        }
        const writingModalButton = event.target.closest("[data-writing-modal-action]");
        if (writingModalButton) {
            const action = writingModalButton.dataset.writingModalAction;
            if (action === "toggle-model") toggleModelAnswer();
            if (action === "evaluate") renderWritingEvaluation(evaluateWriting(), activeWritingTask);
            if (action === "save") saveWritingAttempt();
            if (action === "clear") clearWritingAttempt();
            if (action === "challenge-next") {
                const result = evaluateWriting(activeWritingTask, writingTextValue());
                if (result) {
                    writingChallenge.scores.push(result.score);
                    writingChallenge.words += result.wordCount;
                    if (result.wordCount > 0) writingChallenge.completed += 1;
                }
                writingChallenge.index += 1;
                renderWritingChallengeItem();
            }
            return;
        }
        const storyModalButton = event.target.closest("[data-story-modal-action]");
        if (storyModalButton) {
            const action = storyModalButton.dataset.storyModalAction;
            if (action === "listen") speakStory();
            if (action === "slow") speakStorySlow();
            if (action === "stop") stopStorySpeech();
            if (action === "quiz") startStoryComprehension();
            if (action === "tf") startStoryTrueFalse();
            if (action === "order") startEventOrder();
            if (action === "missing") startMissingWords();
            if (action === "vocab") startStoryVocabularyMatch();
            if (action === "mic") startStoryMicPractice();
            if (action === "ending") renderAlternateEnding();
            if (action === "complete") completeStory();
            return;
        }
        const speakingModalButton = event.target.closest("[data-speaking-modal-action]");
        if (speakingModalButton) {
            const action = speakingModalButton.dataset.speakingModalAction;
            if (action === "listen") speakModelAnswer();
            if (action === "slow") speakModelSlow();
            if (action === "stop-speech") stopModelSpeech();
            if (action === "start-mic") startSpeakingRecognition(activeSpeakingMission);
            if (action === "stop-mic") stopSpeakingRecognition();
            if (action === "retry" && activeSpeakingMission) openSpeakingModal(activeSpeakingMission);
            if (action === "save" && activeSpeakingMission) {
                const result = evaluateSpeaking(currentTranscript, activeSpeakingMission.model_answer, activeSpeakingMission);
                saveSpeakingAttempt(activeSpeakingMission, result);
                showSpeakingFeedback("تم حفظ المحاولة.", "good");
            }
            if (action === "challenge-mic") startSpeakingRecognition(activeSpeakingMission, activeSpeakingMission.model_answer, "challenge");
            if (action === "challenge-next") {
                speakingChallenge.index += 1;
                renderSpeakingChallengeItem();
            }
            if (action === "role-listen") speakRolePlayLine();
            if (action === "role-mic") checkRolePlayAnswer();
            if (action === "role-next") {
                rolePlaySession.index += 1;
                renderRolePlayItem();
            }
            return;
        }
        if (event.target.matches("[data-close-reading]") || event.target.classList.contains("reading-modal")) {
            document.getElementById("readingModal").hidden = true;
            return;
        }
        if (event.target.matches("[data-close-listening]") || event.target.classList.contains("listening-modal")) {
            document.getElementById("listeningModal").hidden = true;
            return;
        }
        if (event.target.matches("[data-close-speaking]") || event.target.classList.contains("speaking-modal")) {
            document.getElementById("speakingModal").hidden = true;
            return;
        }
        if (event.target.matches("[data-close-writing]") || event.target.classList.contains("writing-modal")) {
            document.getElementById("writingModal").hidden = true;
            return;
        }
        if (event.target.matches("[data-close-story]") || event.target.classList.contains("story-modal")) {
            document.getElementById("storyModal").hidden = true;
            return;
        }
        if (event.target.matches("[data-close-exam]") || event.target.classList.contains("exam-modal")) {
            saveExamAnswer();
            document.getElementById("examModal").hidden = true;
            return;
        }
        if (event.target.matches("#checkReadingQuiz")) {
            const item = readingPassages.find((passageItem) => passageItem.title_en === document.getElementById("readingModalTitle").textContent);
            if (item) checkReadingQuiz(item);
            return;
        }
        if (event.target.matches("#checkListeningAnswer")) {
            checkListeningAnswer(activeListeningItem);
            return;
        }
        if (event.target.matches("#startListeningQuickQuiz") || event.target.matches("#startListeningQuickQuizAgain")) {
            startListeningQuickQuiz();
            return;
        }
        if (event.target.matches("#startSpeakingChallenge") || event.target.matches("#startSpeakingChallengeAgain")) {
            startSpeakingChallenge();
            return;
        }
        if (event.target.matches("#startRolePlayMini") || event.target.matches("#startRolePlayMiniAgain")) {
            startRolePlayMini();
            return;
        }
        if (event.target.matches("#startWritingChallenge") || event.target.matches("#startWritingChallengeAgain")) {
            startWritingChallenge();
            return;
        }
        if (event.target.matches("#startStoryChallenge") || event.target.matches("#startStoryChallengeAgain")) {
            startStoryChallenge();
            return;
        }
        if (event.target.matches("#buildSentenceHelper")) {
            buildSentenceHelper();
            return;
        }
        if (event.target.matches("#checkStoryComprehension")) {
            checkStoryComprehension();
            return;
        }
        if (event.target.matches("#checkStoryTrueFalse")) {
            checkStoryTrueFalse();
            return;
        }
        if (event.target.matches("#checkEventOrder")) {
            checkEventOrder();
            return;
        }
        if (event.target.matches("#checkMissingWords")) {
            checkMissingWords();
            return;
        }
        if (event.target.matches("#checkStoryVocabularyMatch")) {
            checkStoryVocabularyMatch();
            return;
        }
        if (event.target.matches("#saveAlternateEnding")) {
            saveAlternateEnding();
            return;
        }
        if (event.target.matches("#nextStoryChallenge")) {
            scoreStoryChallengeItem();
            storyChallenge.index += 1;
            renderStoryChallengeItem();
            return;
        }
        if (event.target.matches("#startSpeedTest")) startSpeedTest();
        if (event.target.matches("#finishSpeedTest")) finishSpeedTest();
    });

    document.addEventListener("input", (event) => {
        if (event.target.matches("#writingStudentText")) updateWritingCounters();
        if (event.target.matches("#examWritingAnswer")) saveExamAnswer();
        if (event.target.matches("#certificateStudentName")) saveLevelFourCertificate();
        if (event.target.matches("#sentenceSubject") || event.target.matches("#sentenceVerb") || event.target.matches("#sentenceObject")) buildSentenceHelper();
    });
});
