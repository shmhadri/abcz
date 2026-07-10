(function () {
    "use strict";

    const progressKey = "abcz-conversations-progress-v1";
    const categories = ["School", "Restaurant", "Shopping", "Travel", "Health", "Daily Life", "Challenge"];
    const els = {};
    let activeCategory = "";
    let speechQueue = [];
    let progress = loadConversationProgress();

    function line(speaker, en, ar) {
        return { speaker, en, ar };
    }

    function conversation(item) {
        const lines = item.lines;
        return {
            ...item,
            vocabulary_focus: item.vocabulary_focus || [],
            lines,
            order_activity: lines.map(row => row.en),
            practice_question: item.practice_question || lines[0].en,
            correct_reply: item.correct_reply || lines[1].en,
            wrong_replies: item.wrong_replies || ["I do not know.", "It is under the chair.", "Yesterday was sunny."],
            completion_points: item.completion_points || 10
        };
    }

    const conversationsData = [
        conversation({ id: "at-school", title_en: "At school", title_ar: "في المدرسة", category: "School", level: "Easy", emoji: "🏫", goal_ar: "يتعلم الطالب التحية والسؤال عن الجاهزية للحصة.", vocabulary_focus: ["good morning", "ready", "English class", "open your book"], lines: [line("A", "Good morning. How are you?", "صباح الخير. كيف حالك؟"), line("B", "I am fine, thank you.", "أنا بخير، شكرًا لك."), line("A", "Are you ready for English class?", "هل أنت مستعد لحصة اللغة الإنجليزية؟"), line("B", "Yes, I am ready.", "نعم، أنا مستعد."), line("A", "Great! Open your book, please.", "رائع! افتح كتابك من فضلك."), line("B", "Okay, teacher.", "حسنًا يا معلم.")], correct_reply: "I am fine, thank you.", wrong_replies: ["It is on the desk.", "I want rice.", "Turn left."] }),
        conversation({ id: "classroom", title_en: "In the classroom", title_ar: "داخل الفصل", category: "School", level: "Easy", emoji: "📘", goal_ar: "يتدرب الطالب على طلب الأدوات وفهم تعليمات المعلم.", vocabulary_focus: ["pencil", "notebook", "listen", "write"], lines: [line("A", "Please take out your notebook.", "من فضلك أخرج دفترك."), line("B", "Should I use a pencil?", "هل أستخدم قلم رصاص؟"), line("A", "Yes, write the date first.", "نعم، اكتب التاريخ أولًا."), line("B", "Can you repeat that, please?", "هل يمكنك إعادة ذلك من فضلك؟"), line("A", "Sure. Write the date first.", "بالطبع. اكتب التاريخ أولًا.")], correct_reply: "Can you repeat that, please?", wrong_replies: ["I need a hotel.", "It is cloudy.", "Chicken and rice."] }),
        conversation({ id: "new-friend", title_en: "Meeting a new friend", title_ar: "مقابلة صديق جديد", category: "Daily Life", level: "Easy", emoji: "🤝", goal_ar: "يتعلم الطالب التعارف والسؤال عن الاسم والعمر.", vocabulary_focus: ["name", "age", "nice to meet you"], lines: [line("A", "Hi, my name is Sara.", "مرحبًا، اسمي سارة."), line("B", "Hi Sara, I am Omar.", "مرحبًا سارة، أنا عمر."), line("A", "Nice to meet you.", "سعدت بلقائك."), line("B", "Nice to meet you too.", "سعدت بلقائك أيضًا."), line("A", "How old are you?", "كم عمرك؟"), line("B", "I am eleven years old.", "عمري إحدى عشرة سنة.")], correct_reply: "Hi Sara, I am Omar.", wrong_replies: ["Go straight.", "It costs ten riyals.", "I have a fever."] }),
        conversation({ id: "hobbies", title_en: "Talking about hobbies", title_ar: "الحديث عن الهوايات", category: "Daily Life", level: "Easy", emoji: "🎨", goal_ar: "يتدرب الطالب على الحديث عن الهوايات المفضلة.", vocabulary_focus: ["hobby", "drawing", "reading", "free time"], lines: [line("A", "What is your hobby?", "ما هوايتك؟"), line("B", "I like drawing pictures.", "أحب رسم الصور."), line("A", "That sounds fun.", "يبدو ذلك ممتعًا."), line("B", "What do you like to do?", "ماذا تحب أن تفعل؟"), line("A", "I like reading stories.", "أحب قراءة القصص.")], correct_reply: "I like drawing pictures.", wrong_replies: ["At the airport.", "It is under the table.", "I need medicine."] }),
        conversation({ id: "restaurant", title_en: "At the restaurant", title_ar: "في المطعم", category: "Restaurant", level: "Medium", emoji: "🍽️", goal_ar: "يتعلم الطالب طلب الطعام والشراب بأدب.", vocabulary_focus: ["menu", "order", "chicken", "water"], lines: [line("A", "Hello. Can I see the menu, please?", "مرحبًا. هل يمكنني رؤية القائمة من فضلك؟"), line("B", "Sure. Here you are.", "بالطبع. تفضل."), line("A", "I would like chicken and rice.", "أود دجاجًا وأرزًا."), line("B", "Would you like water?", "هل تريد ماء؟"), line("A", "Yes, please.", "نعم، من فضلك."), line("B", "Your order will be ready soon.", "سيكون طلبك جاهزًا قريبًا.")], correct_reply: "Sure. Here you are.", wrong_replies: ["I am eleven.", "The bus is late.", "Open your book."] }),
        conversation({ id: "market", title_en: "At the market", title_ar: "في السوق", category: "Shopping", level: "Medium", emoji: "🛒", goal_ar: "يتدرب الطالب على السؤال عن السعر والشراء.", vocabulary_focus: ["price", "fresh", "kilo", "buy"], lines: [line("A", "How much are these apples?", "كم سعر هذه التفاحات؟"), line("B", "They are ten riyals a kilo.", "سعرها عشرة ريالات للكيلو."), line("A", "Are they fresh?", "هل هي طازجة؟"), line("B", "Yes, they are very fresh.", "نعم، إنها طازجة جدًا."), line("A", "I will take one kilo.", "سآخذ كيلو واحدًا.")], correct_reply: "They are ten riyals a kilo.", wrong_replies: ["I am ready.", "It is next to the school.", "I have a cough."] }),
        conversation({ id: "airport", title_en: "At the airport", title_ar: "في المطار", category: "Travel", level: "Medium", emoji: "✈️", goal_ar: "يتعلم الطالب جمل السفر في المطار والتذكرة والبوابة.", vocabulary_focus: ["passport", "ticket", "gate", "flight"], lines: [line("A", "May I see your passport, please?", "هل يمكنني رؤية جواز سفرك من فضلك؟"), line("B", "Yes, here it is.", "نعم، ها هو."), line("A", "Your flight is at gate five.", "رحلتك عند البوابة الخامسة."), line("B", "Thank you. Is the gate far?", "شكرًا. هل البوابة بعيدة؟"), line("A", "No, it is near the coffee shop.", "لا، إنها قريبة من المقهى.")], correct_reply: "Yes, here it is.", wrong_replies: ["I like drawing.", "I need a notebook.", "It is spicy."] }),
        conversation({ id: "directions", title_en: "Asking for directions", title_ar: "السؤال عن الاتجاهات", category: "Travel", level: "Medium", emoji: "🧭", goal_ar: "يتدرب الطالب على السؤال عن مكان وفهم الاتجاهات.", vocabulary_focus: ["go straight", "turn left", "next to", "near"], lines: [line("A", "Excuse me. Where is the library?", "عذرًا. أين المكتبة؟"), line("B", "Go straight and turn left.", "اذهب straight ثم انعطف يسارًا."), line("A", "Is it near the school?", "هل هي قريبة من المدرسة؟"), line("B", "Yes, it is next to the school.", "نعم، إنها بجانب المدرسة."), line("A", "Thank you very much.", "شكرًا جزيلًا لك."), line("B", "You are welcome.", "على الرحب والسعة.")], correct_reply: "Go straight and turn left.", wrong_replies: ["I want rice.", "I am sick.", "It leaves at five."] }),
        conversation({ id: "hospital", title_en: "At the hospital", title_ar: "في المستشفى", category: "Health", level: "Medium", emoji: "🏥", goal_ar: "يتعلم الطالب وصف المرض وطلب المساعدة الطبية.", vocabulary_focus: ["doctor", "fever", "medicine", "rest"], lines: [line("A", "Good afternoon. What is the problem?", "مساء الخير. ما المشكلة؟"), line("B", "I have a fever and a headache.", "لدي حمى وصداع."), line("A", "You should rest and drink water.", "ينبغي أن ترتاح وتشرب الماء."), line("B", "Do I need medicine?", "هل أحتاج دواء؟"), line("A", "Yes, take this medicine after lunch.", "نعم، خذ هذا الدواء بعد الغداء.")], correct_reply: "I have a fever and a headache.", wrong_replies: ["I need a ticket.", "It is sunny.", "Medium, please."] }),
        conversation({ id: "phone", title_en: "On the phone", title_ar: "مكالمة هاتفية", category: "Daily Life", level: "Medium", emoji: "☎️", goal_ar: "يتدرب الطالب على بدء مكالمة وترك رسالة.", vocabulary_focus: ["hello", "speak", "message", "call back"], lines: [line("A", "Hello, can I speak to Ahmed?", "مرحبًا، هل يمكنني التحدث إلى أحمد؟"), line("B", "Sorry, he is not here now.", "آسف، هو ليس هنا الآن."), line("A", "Can I leave a message?", "هل يمكنني ترك رسالة؟"), line("B", "Sure. What is your message?", "بالطبع. ما رسالتك؟"), line("A", "Please ask him to call me back.", "من فضلك اطلب منه أن يتصل بي.")], correct_reply: "Sorry, he is not here now.", wrong_replies: ["The shirt is blue.", "I have rice.", "Turn right."] }),
        conversation({ id: "home", title_en: "At home", title_ar: "في المنزل", category: "Daily Life", level: "Easy", emoji: "🏠", goal_ar: "يتعلم الطالب جمل المساعدة والمهام اليومية في المنزل.", vocabulary_focus: ["homework", "help", "clean", "dinner"], lines: [line("A", "Did you finish your homework?", "هل أنهيت واجبك؟"), line("B", "Yes, I finished it.", "نعم، أنهيته."), line("A", "Can you help me set the table?", "هل يمكنك مساعدتي في ترتيب الطاولة؟"), line("B", "Sure, I can help.", "بالطبع، أستطيع المساعدة."), line("A", "Dinner will be ready soon.", "سيكون العشاء جاهزًا قريبًا.")], correct_reply: "Yes, I finished it.", wrong_replies: ["Gate five.", "I need a doctor.", "It is rainy."] }),
        conversation({ id: "library", title_en: "At the library", title_ar: "في المكتبة", category: "School", level: "Medium", emoji: "📚", goal_ar: "يتدرب الطالب على استعارة كتاب والسؤال عن الهدوء.", vocabulary_focus: ["borrow", "book", "quiet", "return"], lines: [line("A", "Can I borrow this book?", "هل يمكنني استعارة هذا الكتاب؟"), line("B", "Yes, you can borrow it for one week.", "نعم، يمكنك استعارته لمدة أسبوع."), line("A", "Where should I return it?", "أين يجب أن أعيده؟"), line("B", "Return it to the front desk.", "أعده إلى مكتب الاستقبال."), line("A", "Thank you. I will be quiet.", "شكرًا. سأكون هادئًا.")], correct_reply: "Yes, you can borrow it for one week.", wrong_replies: ["I want soup.", "It is behind the chair.", "My flight is late."] }),
        conversation({ id: "clothes", title_en: "Buying clothes", title_ar: "شراء الملابس", category: "Shopping", level: "Medium", emoji: "👕", goal_ar: "يتعلم الطالب اختيار المقاس واللون عند شراء الملابس.", vocabulary_focus: ["shirt", "size", "medium", "try on"], lines: [line("A", "I want to buy this shirt.", "أريد شراء هذا القميص."), line("B", "What size do you need?", "ما المقاس الذي تحتاجه؟"), line("A", "Medium, please.", "متوسط، من فضلك."), line("B", "Would you like to try it on?", "هل تريد تجربته؟"), line("A", "Yes, please.", "نعم، من فضلك.")], correct_reply: "What size do you need?", wrong_replies: ["I am ready.", "It is next to the bank.", "Take this medicine."] }),
        conversation({ id: "ordering-food", title_en: "Ordering food", title_ar: "طلب الطعام", category: "Restaurant", level: "Easy", emoji: "🥗", goal_ar: "يتدرب الطالب على طلب وجبة وتأكيد الطلب.", vocabulary_focus: ["order", "sandwich", "juice", "anything else"], lines: [line("A", "What would you like to order?", "ماذا تود أن تطلب؟"), line("B", "I would like a cheese sandwich.", "أود شطيرة جبن."), line("A", "Would you like juice?", "هل تريد عصيرًا؟"), line("B", "Yes, orange juice, please.", "نعم، عصير برتقال من فضلك."), line("A", "Anything else?", "أي شيء آخر؟"), line("B", "No, thank you.", "لا، شكرًا.")], correct_reply: "I would like a cheese sandwich.", wrong_replies: ["I am at school.", "It is cloudy.", "Turn left."] }),
        conversation({ id: "weather", title_en: "Talking about weather", title_ar: "الحديث عن الطقس", category: "Daily Life", level: "Easy", emoji: "☀️", goal_ar: "يتعلم الطالب وصف الطقس اليومي.", vocabulary_focus: ["sunny", "cloudy", "rainy", "warm"], lines: [line("A", "How is the weather today?", "كيف الطقس اليوم؟"), line("B", "It is sunny and warm.", "إنه مشمس ودافئ."), line("A", "Do you want to play outside?", "هل تريد اللعب في الخارج؟"), line("B", "Yes, that sounds great.", "نعم، يبدو ذلك رائعًا."), line("A", "Wear your cap, please.", "ارتدِ قبعتك من فضلك.")], correct_reply: "It is sunny and warm.", wrong_replies: ["I want a ticket.", "I have a fever.", "Medium, please."] }),
        conversation({ id: "daily-routine", title_en: "Talking about daily routine", title_ar: "الروتين اليومي", category: "Daily Life", level: "Medium", emoji: "⏰", goal_ar: "يتدرب الطالب على الحديث عن الأنشطة اليومية.", vocabulary_focus: ["wake up", "breakfast", "school", "homework"], lines: [line("A", "What time do you wake up?", "متى تستيقظ؟"), line("B", "I usually wake up at six.", "عادة أستيقظ الساعة السادسة."), line("A", "What do you do after school?", "ماذا تفعل بعد المدرسة؟"), line("B", "I do my homework and play football.", "أحل واجبي وألعب كرة القدم."), line("A", "That is a good routine.", "هذا روتين جيد.")], correct_reply: "I usually wake up at six.", wrong_replies: ["I need a passport.", "The shirt is small.", "It is under the desk."] }),
        conversation({ id: "hotel", title_en: "At the hotel", title_ar: "في الفندق", category: "Travel", level: "Challenge", emoji: "🏨", goal_ar: "يتعلم الطالب تسجيل الدخول في الفندق وطلب معلومات.", vocabulary_focus: ["reservation", "room", "check in", "breakfast"], lines: [line("A", "Good evening. Do you have a reservation?", "مساء الخير. هل لديك حجز؟"), line("B", "Yes, under Ahmed.", "نعم، باسم أحمد."), line("A", "Your room is on the third floor.", "غرفتك في الطابق الثالث."), line("B", "Is breakfast included?", "هل الإفطار مشمول؟"), line("A", "Yes, breakfast starts at seven.", "نعم، يبدأ الإفطار الساعة السابعة.")], correct_reply: "Yes, under Ahmed.", wrong_replies: ["It is raining.", "I need a pencil.", "I want soup."] }),
        conversation({ id: "bus-station", title_en: "At the bus station", title_ar: "في محطة الحافلات", category: "Travel", level: "Medium", emoji: "🚌", goal_ar: "يتدرب الطالب على السؤال عن وقت الحافلة والتذكرة.", vocabulary_focus: ["bus", "ticket", "leave", "station"], lines: [line("A", "What time does the bus leave?", "متى تغادر الحافلة؟"), line("B", "It leaves at five o'clock.", "تغادر الساعة الخامسة."), line("A", "Where can I buy a ticket?", "أين يمكنني شراء تذكرة؟"), line("B", "You can buy it at the counter.", "يمكنك شراءها من الشباك."), line("A", "Thank you for your help.", "شكرًا على مساعدتك.")], correct_reply: "It leaves at five o'clock.", wrong_replies: ["I like drawing.", "It is spicy.", "Take medicine."] }),
        conversation({ id: "help", title_en: "Asking for help", title_ar: "طلب المساعدة", category: "Daily Life", level: "Easy", emoji: "🙋", goal_ar: "يتعلم الطالب طلب المساعدة بأدب.", vocabulary_focus: ["help", "please", "problem", "understand"], lines: [line("A", "Can you help me, please?", "هل يمكنك مساعدتي من فضلك؟"), line("B", "Of course. What is the problem?", "بالطبع. ما المشكلة؟"), line("A", "I do not understand this question.", "لا أفهم هذا السؤال."), line("B", "Let us read it together.", "دعنا نقرأه معًا."), line("A", "Thank you very much.", "شكرًا جزيلًا لك.")], correct_reply: "Of course. What is the problem?", wrong_replies: ["It leaves at five.", "I want a shirt.", "Sunny and warm."] }),
        conversation({ id: "future-dreams", title_en: "Talking about future dreams", title_ar: "الحديث عن الأحلام المستقبلية", category: "Challenge", level: "Challenge", emoji: "🚀", goal_ar: "يتدرب الطالب على التعبير عن أحلامه وخططه المستقبلية.", vocabulary_focus: ["future", "dream", "doctor", "engineer"], lines: [line("A", "What do you want to be in the future?", "ماذا تريد أن تصبح في المستقبل؟"), line("B", "I want to be an engineer.", "أريد أن أصبح مهندسًا."), line("A", "Why do you like engineering?", "لماذا تحب الهندسة؟"), line("B", "Because I like building new things.", "لأنني أحب بناء أشياء جديدة."), line("A", "That is a great dream.", "هذا حلم رائع.")], correct_reply: "I want to be an engineer.", wrong_replies: ["It is next to school.", "I have a headache.", "No, thank you."] })
    ];

    function escapeHtml(value) {
        return String(value ?? "").replace(/[&<>"']/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
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

    function loadConversationProgress() {
        const initial = window.CONVERSATIONS_INITIAL_PROGRESS || {};
        const fallback = { points: Number(initial.points || 0), actions: Number(initial.actions || 0), completed: [], sectionCompleted: Boolean(initial.completed), fiveBonus: false };
        try {
            return { ...fallback, ...JSON.parse(localStorage.getItem(progressKey) || "{}") };
        } catch {
            return fallback;
        }
    }

    function saveConversationProgress() {
        localStorage.setItem(progressKey, JSON.stringify(progress));
    }

    function csrfToken() {
        return document.cookie.split(";").map(value => value.trim()).find(value => value.startsWith("csrftoken="))?.split("=")[1] || "";
    }

    async function awardConversationPoints(activityType, points, options = {}) {
        progress.points = Math.max(0, Number(progress.points || 0) + points);
        progress.actions = Math.max(0, Number(progress.actions || 0) + 1);
        if (options.completedConversation && !progress.completed.includes(options.completedConversation)) {
            progress.completed.push(options.completedConversation);
        }
        if (progress.completed.length >= 5 && !progress.fiveBonus) {
            progress.fiveBonus = true;
            progress.points += 20;
        }
        if (options.completedSection) progress.sectionCompleted = true;
        saveConversationProgress();
        updateConversationStats();
        // TODO: integrate conversations progress with StudentActivity leaderboard if that model becomes available.
        try {
            const response = await fetch(window.CONVERSATIONS_PROGRESS_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
                body: JSON.stringify({ section: "conversations", activity_type: activityType, points, completed: Boolean(options.completedSection) })
            });
            const data = await response.json();
            if (data.status === "ok") {
                progress.points = data.points;
                progress.actions = data.actions_count;
                progress.sectionCompleted = data.completed || progress.sectionCompleted;
                saveConversationProgress();
                updateConversationStats();
            }
        } catch {
            updateConversationStats();
        }
    }

    function statusFor(points) {
        if (progress.sectionCompleted || points >= 150) return "متقن";
        if (points >= 80) return "ممتاز";
        if (points >= 30) return "جيد";
        return "قيد التدريب";
    }

    function updateConversationStats() {
        const points = Number(progress.points || 0);
        els.points.textContent = points;
        els.actions.textContent = Number(progress.actions || 0);
        els.status.textContent = statusFor(points);
        els.completed.textContent = `${progress.completed.length} / ${conversationsData.length}`;
        els.progressFill.style.width = `${Math.min(100, Math.round((points / 150) * 100))}%`;
    }

    function renderCategoryOptions() {
        els.category.innerHTML = `<option value="">كل التصنيفات</option>` + categories.map(category => `<option value="${category}">${category}</option>`).join("");
    }

    function filterConversations() {
        const query = normalizeText(els.search.value);
        const category = activeCategory || els.category.value;
        const level = els.level.value;
        return conversationsData.filter(item => {
            const haystack = normalizeText(`${item.title_en} ${item.title_ar} ${item.category} ${item.goal_ar} ${item.vocabulary_focus.join(" ")}`);
            return (!query || haystack.includes(query)) && (!category || item.category === category) && (!level || item.level === level);
        });
    }

    function searchConversations() {
        renderConversationCards();
    }

    function renderConversationCards() {
        const rows = filterConversations();
        els.grid.innerHTML = rows.map(item => {
            const completed = progress.completed.includes(item.id);
            return `
                <article class="cv-card" data-conversation="${escapeHtml(item.id)}">
                    <div class="cv-card-top">
                        <div class="cv-emoji">${escapeHtml(item.emoji)}</div>
                        <div>
                            <div class="cv-badges">
                                <span class="cv-badge">${escapeHtml(item.category)}</span>
                                <span class="cv-badge level">${escapeHtml(item.level)}</span>
                                ${completed ? `<span class="cv-badge">مكتملة</span>` : ""}
                            </div>
                            <h2 class="cv-title">${escapeHtml(item.title_en)}</h2>
                            <div class="cv-ar">${escapeHtml(item.title_ar)}</div>
                        </div>
                    </div>
                    <div class="cv-goal">${escapeHtml(item.goal_ar)}</div>
                    <div class="cv-vocab">كلمات مهمة: ${item.vocabulary_focus.map(escapeHtml).join(" - ")}</div>
                    <div class="cv-ar">عدد الجمل: ${item.lines.length}</div>
                    <div class="cv-actions">
                        <button class="cv-action open" type="button" data-action="open" data-id="${escapeHtml(item.id)}">افتح المحادثة</button>
                        <button class="cv-action listen" type="button" data-action="listen" data-id="${escapeHtml(item.id)}">استمع للحوار</button>
                        <button class="cv-action mic" type="button" data-action="mic" data-id="${escapeHtml(item.id)}">اقرأ بالمايك</button>
                        <button class="cv-action order" type="button" data-action="order" data-id="${escapeHtml(item.id)}">رتب الحوار</button>
                        <button class="cv-action reply" type="button" data-action="reply" data-id="${escapeHtml(item.id)}">اختر الرد</button>
                    </div>
                </article>
            `;
        }).join("");
        els.empty.hidden = rows.length > 0;
    }

    function findConversation(id) {
        return conversationsData.find(item => item.id === id);
    }

    function speakText(text, rate = 1) {
        try {
            if (!("speechSynthesis" in window)) {
                openModal("<h2 id='cvModalTitle'>النطق غير مدعوم</h2><p>جرّب Google Chrome لتفعيل النطق.</p>");
                return;
            }
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = "en-US";
            utterance.rate = rate;
            window.speechSynthesis.speak(utterance);
        } catch {
            openModal("<h2 id='cvModalTitle'>تعذر النطق</h2><p>لم يتمكن المتصفح من تشغيل الصوت الآن.</p>");
        }
    }

    function speakSlow(text) {
        speakText(text, 0.68);
    }

    function stopSpeaking() {
        speechQueue = [];
        try { window.speechSynthesis?.cancel(); } catch {}
    }

    function speakDialogue(item) {
        stopSpeaking();
        if (!("speechSynthesis" in window)) {
            openModal("<h2 id='cvModalTitle'>النطق غير مدعوم</h2><p>جرّب Google Chrome لتفعيل النطق.</p>");
            return;
        }
        speechQueue = item.lines.map(row => row.en);
        const speakNext = () => {
            const text = speechQueue.shift();
            if (!text) return;
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = "en-US";
            utterance.rate = 0.9;
            utterance.onend = speakNext;
            window.speechSynthesis.speak(utterance);
        };
        speakNext();
        awardConversationPoints("listen_dialogue", 3);
    }

    function openModal(html) {
        els.modalContent.innerHTML = html;
        els.modal.hidden = false;
    }

    function closeModal() {
        stopSpeaking();
        els.modal.hidden = true;
        els.modalContent.innerHTML = "";
    }

    function dialogueHtml(item) {
        return item.lines.map((row, index) => `
            <div class="cv-line ${row.speaker === "A" ? "speaker-a" : "speaker-b"}">
                <div class="cv-speaker">Speaker ${escapeHtml(row.speaker)}</div>
                <div class="cv-en">${escapeHtml(row.en)}</div>
                <div class="cv-ar-line">${escapeHtml(row.ar)}</div>
                <div class="cv-line-tools">
                    <button class="cv-action listen" type="button" data-modal-speak="${escapeHtml(row.en)}">نطق</button>
                    <button class="cv-action listen" type="button" data-modal-slow="${escapeHtml(row.en)}">قراءة بطيئة</button>
                    <button class="cv-action mic" type="button" data-modal-mic="${escapeHtml(item.id)}" data-line="${index}">مايك</button>
                </div>
            </div>
        `).join("");
    }

    function openConversationModal(item) {
        openModal(`
            <h2 id="cvModalTitle" class="cv-title">${escapeHtml(item.title_en)}</h2>
            <p class="cv-ar">${escapeHtml(item.title_ar)}</p>
            <p class="cv-goal">${escapeHtml(item.goal_ar)}</p>
            <div class="cv-dialogue">${dialogueHtml(item)}</div>
            <div class="cv-actions">
                <button class="cv-action listen" type="button" data-modal-dialogue="${escapeHtml(item.id)}">استمع للحوار كاملًا</button>
                <button class="cv-action order" type="button" data-modal-training="${escapeHtml(item.id)}">ابدأ تدريب المحادثة</button>
                <button class="cv-action reply" type="button" data-modal-stop>إيقاف النطق</button>
            </div>
        `);
        awardConversationPoints("open", 1);
    }

    function similarityScore(original, spoken) {
        const a = normalizeText(original);
        const b = normalizeText(spoken);
        if (!a || !b) return 0;
        const words = a.split(" ");
        const spokenWords = new Set(b.split(" "));
        const hits = words.filter(word => spokenWords.has(word)).length;
        return Math.round((hits / Math.max(words.length, 1)) * 100);
    }

    function startMicPractice(item, lineIndex = 0) {
        const target = item.lines[lineIndex]?.en || item.lines[0].en;
        openModal(`<h2 id="cvModalTitle">تدريب المايك</h2><p class="cv-en">${escapeHtml(target)}</p><div id="cvSpeechResult"></div>`);
        SpeechService.startRecognition({
            targetText: target,
            type: "short_sentence",
            section: "conversations",
            level: item.level || "",
            onStart: () => SpeechService.renderResult("#cvSpeechResult", { expected: target, spoken: SpeechService.messages.listening, score: 0, status: "retry" }),
            onResult: result => {
                SpeechService.renderResult("#cvSpeechResult", result);
                awardConversationPoints("mic", 3, { completedConversation: result.status === "excellent" ? item.id : "" });
                renderConversationCards();
            },
            onError: result => SpeechService.renderResult("#cvSpeechResult", result)
        });
        return;
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            openModal(`<h2 id="cvModalTitle">تدريب المايك</h2><p>الميكروفون غير مدعوم في هذا المتصفح، جرّب Google Chrome.</p><p class="cv-en">${escapeHtml(target)}</p>`);
            return;
        }
        const recognition = new SpeechRecognition();
        recognition.lang = "en-US";
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.onresult = event => {
            const spoken = event.results[0][0].transcript;
            const score = similarityScore(target, spoken);
            const label = score >= 85 ? "ممتاز" : score >= 60 ? "جيد" : "حاول مرة أخرى";
            openModal(`<h2 id="cvModalTitle">نتيجة المايك: ${escapeHtml(label)}</h2><p class="cv-en">${escapeHtml(target)}</p><p>قلت: <strong>${escapeHtml(spoken)}</strong></p><p>نسبة التطابق: <strong>${score}%</strong></p>`);
            awardConversationPoints("mic", 3, { completedConversation: score >= 85 ? item.id : "" });
            renderConversationCards();
        };
        recognition.onerror = () => openModal(`<h2 id="cvModalTitle">تعذر تشغيل المايك</h2><p>اسمح للمتصفح باستخدام الميكروفون ثم جرّب مرة أخرى.</p><p class="cv-en">${escapeHtml(target)}</p>`);
        openModal(`<h2 id="cvModalTitle">استعد للقراءة</h2><p>اقرأ الجملة التالية بصوت واضح.</p><p class="cv-en">${escapeHtml(target)}</p>`);
        recognition.start();
    }

    function dialogueOrderGame(item) {
        const shuffled = shuffle(item.order_activity);
        openModal(`<h2 id="cvModalTitle">Dialogue Order</h2><p>رتب الجمل كما ظهرت في الحوار.</p><div class="cv-vocab">${shuffled.map(escapeHtml).join(" / ")}</div><input id="cvTrainingInput" placeholder="اكتب الجمل بالترتيب"><button class="cv-btn primary" data-check-order="${item.id}">تحقق</button><div id="cvTrainingFeedback"></div>`);
    }

    function chooseReplyGame(item) {
        const choices = shuffle([item.correct_reply, ...item.wrong_replies]).slice(0, 4);
        openModal(`<h2 id="cvModalTitle">Choose the Reply</h2><p class="cv-en">${escapeHtml(item.practice_question)}</p><div class="cv-options">${choices.map(choice => `<button class="cv-option" data-reply="${escapeHtml(choice)}" data-correct="${escapeHtml(item.correct_reply)}" data-id="${escapeHtml(item.id)}">${escapeHtml(choice)}</button>`).join("")}</div><div id="cvTrainingFeedback"></div>`);
    }

    function completeConversationGame(item) {
        openModal(`<h2 id="cvModalTitle">Complete the Conversation</h2><p class="cv-en">${escapeHtml(item.practice_question)}</p><input id="cvTrainingInput" placeholder="اكتب الرد المناسب"><button class="cv-btn primary" data-check-complete="${item.id}">تحقق</button><div id="cvTrainingFeedback"></div>`);
    }

    function listenAndChooseGame(item) {
        const target = item.lines[0];
        const choices = shuffle(item.lines.map(row => row.ar)).slice(0, 4);
        if (!choices.includes(target.ar)) choices[0] = target.ar;
        openModal(`<h2 id="cvModalTitle">Listen and Choose</h2><button class="cv-action listen" data-modal-speak="${escapeHtml(target.en)}">استمع</button><div class="cv-options">${shuffle(choices).map(choice => `<button class="cv-option" data-listen-answer="${escapeHtml(choice)}" data-correct="${escapeHtml(target.ar)}" data-id="${escapeHtml(item.id)}">${escapeHtml(choice)}</button>`).join("")}</div><div id="cvTrainingFeedback"></div>`);
    }

    function rolePlayGame(item) {
        openModal(`<h2 id="cvModalTitle">Role Play</h2><p>اختر دورك. الموقع ينطق الطرف الآخر، وأنت تقرأ دورك بالمايك.</p><button class="cv-action mic" data-role-play="${item.id}" data-role="A">أنا Speaker A</button><button class="cv-action mic" data-role-play="${item.id}" data-role="B">أنا Speaker B</button><div class="cv-dialogue">${dialogueHtml(item)}</div>`);
    }

    function conversationSpeedChallenge() {
        const item = conversationsData[Math.floor(Math.random() * conversationsData.length)];
        const choices = shuffle([item.correct_reply, ...item.wrong_replies]).slice(0, 4);
        els.gamePanel.hidden = false;
        els.gamePanel.innerHTML = `<h2>Conversation Speed Challenge</h2><p>تحدي 60 ثانية: اختر الرد الصحيح بسرعة.</p><p class="cv-en">${escapeHtml(item.practice_question)}</p><div class="cv-options">${choices.map(choice => `<button class="cv-option" data-speed-answer="${escapeHtml(choice)}" data-correct="${escapeHtml(item.correct_reply)}">${escapeHtml(choice)}</button>`).join("")}</div><div id="cvGameFeedback"></div>`;
    }

    function replyMasterGame() {
        const item = conversationsData[Math.floor(Math.random() * conversationsData.length)];
        const choices = shuffle([item.correct_reply, ...item.wrong_replies]).slice(0, 4);
        els.gamePanel.hidden = false;
        els.gamePanel.innerHTML = `<h2>Reply Master</h2><p class="cv-en">${escapeHtml(item.practice_question)}</p><div class="cv-options">${choices.map(choice => `<button class="cv-option" data-game-answer="${escapeHtml(choice)}" data-correct="${escapeHtml(item.correct_reply)}">${escapeHtml(choice)}</button>`).join("")}</div><div id="cvGameFeedback"></div>`;
    }

    function dialogueBuilderGame() {
        const item = conversationsData[Math.floor(Math.random() * conversationsData.length)];
        els.gamePanel.hidden = false;
        els.gamePanel.innerHTML = `<h2>Dialogue Builder</h2><p>اكتب أول جملتين بالترتيب.</p><div class="cv-vocab">${shuffle(item.order_activity).map(escapeHtml).join(" / ")}</div><input id="cvGameInput" placeholder="اكتب الجملتين"><button class="cv-btn primary" data-game-build="${item.id}">تحقق</button><div id="cvGameFeedback"></div>`;
    }

    function rolePlayChallengeGame() {
        const item = conversationsData[Math.floor(Math.random() * conversationsData.length)];
        els.gamePanel.hidden = false;
        els.gamePanel.innerHTML = `<h2>Role Play Challenge</h2><p class="cv-en">${escapeHtml(item.lines[0].en)}</p><button class="cv-action mic" data-panel-mic="${item.id}">اقرأ بالمايك</button><div id="cvGameFeedback"></div>`;
    }

    function conversationMemoryGame() {
        const item = conversationsData[Math.floor(Math.random() * conversationsData.length)];
        const target = item.lines[0];
        const choices = shuffle(item.lines.map(row => row.ar)).slice(0, 4);
        if (!choices.includes(target.ar)) choices[0] = target.ar;
        els.gamePanel.hidden = false;
        els.gamePanel.innerHTML = `<h2>Conversation Memory</h2><p class="cv-en">${escapeHtml(target.en)}</p><div class="cv-options">${shuffle(choices).map(choice => `<button class="cv-option" data-game-answer="${escapeHtml(choice)}" data-correct="${escapeHtml(target.ar)}">${escapeHtml(choice)}</button>`).join("")}</div><div id="cvGameFeedback"></div>`;
    }

    function situationPickerGame() {
        const item = conversationsData[Math.floor(Math.random() * conversationsData.length)];
        const choices = shuffle(conversationsData).slice(0, 4);
        if (!choices.some(row => row.id === item.id)) choices[0] = item;
        els.gamePanel.hidden = false;
        els.gamePanel.innerHTML = `<h2>Situation Picker</h2><p>${escapeHtml(item.goal_ar)}</p><div class="cv-options">${shuffle(choices).map(row => `<button class="cv-option" data-game-answer="${escapeHtml(row.title_en)}" data-correct="${escapeHtml(item.title_en)}">${escapeHtml(row.title_en)}</button>`).join("")}</div><div id="cvGameFeedback"></div>`;
    }

    function fastResponseGame() {
        conversationSpeedChallenge();
    }

    function renderGame(game) {
        if (game === "reply") replyMasterGame();
        if (game === "builder") dialogueBuilderGame();
        if (game === "role") rolePlayChallengeGame();
        if (game === "memory") conversationMemoryGame();
        if (game === "situation") situationPickerGame();
        if (game === "fast") fastResponseGame();
        if (game === "speed") conversationSpeedChallenge();
    }

    function setFeedback(message) {
        const feedback = document.getElementById("cvTrainingFeedback") || document.getElementById("cvGameFeedback");
        if (feedback) feedback.textContent = message;
    }

    function handleTrainingClick(event) {
        const reply = event.target.closest("[data-reply]");
        if (reply) {
            const success = reply.dataset.reply === reply.dataset.correct;
            reply.classList.add(success ? "correct" : "wrong");
            if (success) awardConversationPoints("reply", 5, { completedConversation: reply.dataset.id });
            setFeedback(success ? "إجابة صحيحة +5" : "حاول مرة أخرى.");
            renderConversationCards();
            return;
        }
        const listen = event.target.closest("[data-listen-answer]");
        if (listen) {
            const success = listen.dataset.listenAnswer === listen.dataset.correct;
            listen.classList.add(success ? "correct" : "wrong");
            if (success) awardConversationPoints("reply", 5, { completedConversation: listen.dataset.id });
            setFeedback(success ? "اختيار صحيح +5" : "استمع مرة أخرى.");
            renderConversationCards();
            return;
        }
        const order = event.target.closest("[data-check-order]");
        if (order) {
            const item = findConversation(order.dataset.checkOrder);
            const expected = normalizeText(item.order_activity.join(" "));
            const actual = normalizeText(document.getElementById("cvTrainingInput").value);
            const success = actual.includes(expected.slice(0, 30)) || similarityScore(expected, actual) >= 70;
            if (success) awardConversationPoints("order", 7, { completedConversation: item.id });
            setFeedback(success ? "ترتيب صحيح +7" : `البداية الصحيحة: ${item.order_activity.slice(0, 2).join(" / ")}`);
            renderConversationCards();
            return;
        }
        const complete = event.target.closest("[data-check-complete]");
        if (complete) {
            const item = findConversation(complete.dataset.checkComplete);
            const success = normalizeText(document.getElementById("cvTrainingInput").value) === normalizeText(item.correct_reply);
            if (success) awardConversationPoints("reply", 5, { completedConversation: item.id });
            setFeedback(success ? "إكمال صحيح +5" : `الإجابة: ${item.correct_reply}`);
            renderConversationCards();
            return;
        }
        const role = event.target.closest("[data-role-play]");
        if (role) {
            const item = findConversation(role.dataset.rolePlay);
            const lineIndex = item.lines.findIndex(row => row.speaker === role.dataset.role);
            awardConversationPoints("role_play", 10, { completedConversation: item.id });
            startMicPractice(item, Math.max(0, lineIndex));
        }
    }

    function handleGameClick(event) {
        const answer = event.target.closest("[data-game-answer], [data-speed-answer]");
        if (answer) {
            const userAnswer = answer.dataset.gameAnswer || answer.dataset.speedAnswer;
            const success = userAnswer === answer.dataset.correct;
            answer.classList.add(success ? "correct" : "wrong");
            if (success) awardConversationPoints(answer.dataset.speedAnswer ? "speed" : "game", answer.dataset.speedAnswer ? 10 : 7);
            setFeedback(success ? "ممتاز، نقاط جديدة." : "حاول مرة أخرى.");
            return;
        }
        const build = event.target.closest("[data-game-build]");
        if (build) {
            const item = findConversation(build.dataset.gameBuild);
            const expected = normalizeText(item.order_activity.slice(0, 2).join(" "));
            const actual = normalizeText(document.getElementById("cvGameInput").value);
            const success = similarityScore(expected, actual) >= 65;
            if (success) awardConversationPoints("game", 7, { completedConversation: item.id });
            setFeedback(success ? "بناء صحيح +7" : `الصحيح: ${item.order_activity.slice(0, 2).join(" / ")}`);
            renderConversationCards();
            return;
        }
        const panelMic = event.target.closest("[data-panel-mic]");
        if (panelMic) {
            startMicPractice(findConversation(panelMic.dataset.panelMic), 0);
        }
    }

    function openTraining(item) {
        chooseReplyGame(item);
    }

    function handleCardAction(action, item) {
        if (!item) return;
        if (action === "open") openConversationModal(item);
        if (action === "listen") speakDialogue(item);
        if (action === "mic") startMicPractice(item, 0);
        if (action === "order") dialogueOrderGame(item);
        if (action === "reply") chooseReplyGame(item);
    }

    function handleModalClick(event) {
        const speak = event.target.closest("[data-modal-speak]");
        if (speak) {
            speakText(speak.dataset.modalSpeak);
            awardConversationPoints("listen_sentence", 1);
            return;
        }
        const slow = event.target.closest("[data-modal-slow]");
        if (slow) {
            speakSlow(slow.dataset.modalSlow);
            awardConversationPoints("listen_sentence", 1);
            return;
        }
        const dialogue = event.target.closest("[data-modal-dialogue]");
        if (dialogue) {
            speakDialogue(findConversation(dialogue.dataset.modalDialogue));
            return;
        }
        const mic = event.target.closest("[data-modal-mic]");
        if (mic) {
            startMicPractice(findConversation(mic.dataset.modalMic), Number(mic.dataset.line || 0));
            return;
        }
        const training = event.target.closest("[data-modal-training]");
        if (training) {
            openTraining(findConversation(training.dataset.modalTraining));
            return;
        }
        if (event.target.closest("[data-modal-stop]")) {
            stopSpeaking();
            return;
        }
        handleTrainingClick(event);
    }

    function bindEvents() {
        els.search.addEventListener("input", searchConversations);
        els.category.addEventListener("change", () => {
            activeCategory = "";
            renderConversationCards();
        });
        els.level.addEventListener("change", renderConversationCards);
        document.querySelectorAll("[data-filter-category]").forEach(button => {
            button.addEventListener("click", () => {
                activeCategory = button.dataset.filterCategory;
                els.category.value = activeCategory;
                renderConversationCards();
            });
        });
        document.querySelectorAll("[data-filter-level]").forEach(button => {
            button.addEventListener("click", () => {
                els.level.value = button.dataset.filterLevel;
                renderConversationCards();
            });
        });
        els.grid.addEventListener("click", event => {
            const button = event.target.closest("[data-action]");
            if (!button) return;
            handleCardAction(button.dataset.action, findConversation(button.dataset.id));
        });
        els.modal.addEventListener("click", event => {
            if (event.target === els.modal) closeModal();
            handleModalClick(event);
        });
        document.getElementById("cvModalClose").addEventListener("click", closeModal);
        document.querySelectorAll("[data-game]").forEach(button => {
            button.addEventListener("click", () => renderGame(button.dataset.game));
        });
        els.gamePanel.addEventListener("click", handleGameClick);
        document.getElementById("cvCompleteSection").addEventListener("click", () => {
            awardConversationPoints("complete", 50, { completedSection: true });
        });
    }

    document.addEventListener("DOMContentLoaded", () => {
        els.grid = document.getElementById("cvGrid");
        els.empty = document.getElementById("cvEmpty");
        els.search = document.getElementById("cvSearch");
        els.category = document.getElementById("cvCategory");
        els.level = document.getElementById("cvLevel");
        els.points = document.getElementById("cvPoints");
        els.actions = document.getElementById("cvActions");
        els.status = document.getElementById("cvStatus");
        els.completed = document.getElementById("cvCompleted");
        els.progressFill = document.getElementById("cvProgressFill");
        els.modal = document.getElementById("cvModal");
        els.modalContent = document.getElementById("cvModalContent");
        els.gamePanel = document.getElementById("cvGamePanel");
        renderCategoryOptions();
        updateConversationStats();
        renderConversationCards();
        bindEvents();
    });
})();
