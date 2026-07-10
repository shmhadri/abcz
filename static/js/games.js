const vocabularyGameData = [
    { prompt: "classroom", answer: "فصل دراسي", options: ["فصل دراسي", "مطار", "قلق"], emoji: "CLS", letters: "classroom" },
    { prompt: "dictionary", answer: "قاموس", options: ["حاسوب", "قاموس", "سوق"], emoji: "DIC", letters: "dictionary" },
    { prompt: "computer", answer: "حاسوب", options: ["مدرسة", "حاسوب", "مسؤولية"], emoji: "CPU", letters: "computer" },
    { prompt: "airport", answer: "مطار", options: ["مطار", "مطعم", "كتاب"], emoji: "AIR", letters: "airport" },
    { prompt: "worried", answer: "قلق", options: ["سعيد", "قلق", "سريع"], emoji: "WRD", letters: "worried" },
    { prompt: "responsibility", answer: "مسؤولية", options: ["مسؤولية", "سفر", "طاولة"], emoji: "RSP", letters: "responsibility" },
];

const grammarGameData = [
    { prompt: "She ___ happy.", answer: "is", options: ["am", "is", "are"], fixed: "She is happy." },
    { prompt: "They ___ students.", answer: "are", options: ["is", "are", "am"], fixed: "They are students." },
    { prompt: "I ___ swim.", answer: "can", options: ["can", "is", "are"], fixed: "I can swim." },
    { prompt: "He ___ books.", answer: "reads", options: ["read", "reads", "reading"], fixed: "He reads books." },
    { prompt: "Where ___ you live?", answer: "do", options: ["do", "is", "are"], fixed: "Where do you live?" },
    { prompt: "She are happy.", answer: "She is happy.", options: ["She is happy.", "She am happy.", "She are happy."], fixed: "She is happy." },
];

const sentenceGameData = [
    { prompt: "Good morning.", answer: "صباح الخير.", options: ["صباح الخير.", "تصبح على خير.", "شكرا."], words: ["Good", "morning."], trueFalse: true },
    { prompt: "How are you today?", answer: "كيف حالك اليوم؟", options: ["أين كتابك؟", "كيف حالك اليوم؟", "أنا سعيد."], words: ["How", "are", "you", "today?"], trueFalse: true },
    { prompt: "Can you help me, please?", answer: "هل يمكنك مساعدتي من فضلك؟", options: ["هل يمكنك مساعدتي من فضلك؟", "أحب القراءة.", "افتح الباب."], words: ["Can", "you", "help", "me,", "please?"], trueFalse: true },
    { prompt: "Never give up.", answer: "لا تستسلم أبدا.", options: ["لا تستسلم أبدا.", "اجلس هنا.", "أنا أقرأ."], words: ["Never", "give", "up."], trueFalse: false },
];

const conversationGameData = [
    { prompt: "A: Nice to meet you. B: ___", answer: "Nice to meet you too.", options: ["Nice to meet you too.", "It is red.", "Open the book."], order: ["Good morning.", "How are you?", "I am fine."] },
    { prompt: "A: Thank you. B: ___", answer: "You are welcome.", options: ["You are welcome.", "I am seven.", "It is big."], order: ["May I have water?", "Sure.", "Thank you."] },
    { prompt: "A: How are you? B: ___", answer: "I am fine.", options: ["I am fine.", "It is a pen.", "Blue."], order: ["Hello.", "How are you?", "I am fine."] },
];

const gamesData = [
    { id: "flashcards", title: "Flashcards", ar: "بطاقات تعليمية", category: "Vocabulary", skill: "Vocabulary", level: "Easy", time: "5 دقائق", questions: 6, icon: "FC", description: "اقلب البطاقة وشاهد الترجمة والمثال.", mode: "flashcards" },
    { id: "word-match", title: "Word Match", ar: "مطابقة الكلمات", category: "Vocabulary", skill: "Vocabulary", level: "Easy", time: "8 دقائق", questions: 6, icon: "WM", description: "طابق الكلمة الإنجليزية مع معناها العربي.", mode: "choice" },
    { id: "emoji-choice", title: "Picture / Emoji Choice", ar: "اختر الكلمة من الصورة", category: "Vocabulary", skill: "Vocabulary", level: "Easy", time: "6 دقائق", questions: 6, icon: "PC", description: "يظهر رمز أو صورة مبسطة، والطالب يختار الكلمة المناسبة.", mode: "emoji" },
    { id: "listen-choose", title: "Listen and Choose", ar: "استمع واختر", category: "Vocabulary", skill: "Listening", level: "Medium", time: "8 دقائق", questions: 6, icon: "LC", description: "استمع للكلمة أو الجملة ثم اختر المعنى الصحيح.", mode: "listen", supportsListen: true },
    { id: "fill-blank", title: "Fill in the Blank", ar: "أكمل الفراغ", category: "Grammar", skill: "Grammar", level: "Medium", time: "8 دقائق", questions: 6, icon: "FB", description: "أكمل الكلمة أو القاعدة الناقصة.", mode: "choice" },
    { id: "memory-game", title: "Memory Game", ar: "لعبة الذاكرة", category: "Vocabulary", skill: "Vocabulary", level: "Medium", time: "10 دقائق", questions: 6, icon: "MG", description: "طابق الكلمة مع ترجمتها من بطاقات مخفية.", mode: "memory" },
    { id: "word-builder", title: "Word Builder", ar: "بناء الكلمة", category: "Vocabulary", skill: "Reading", level: "Medium", time: "8 دقائق", questions: 5, icon: "WB", description: "رتب الحروف لتكوين الكلمة الصحيحة.", mode: "builder" },
    { id: "sentence-builder", title: "Sentence Builder", ar: "ترتيب الجملة", category: "Sentences", skill: "Reading", level: "Medium", time: "10 دقائق", questions: 4, icon: "SB", description: "رتب الكلمات لتكوين جملة صحيحة.", mode: "sentenceBuilder" },
    { id: "grammar-fix", title: "Grammar Fix", ar: "صحح الخطأ", category: "Grammar", skill: "Grammar", level: "Challenge", time: "10 دقائق", questions: 5, icon: "GF", description: "اكتشف الخطأ في الجملة وصححه.", mode: "grammarFix" },
    { id: "tense-race", title: "Tense Race", ar: "سباق الأزمنة", category: "Grammar", skill: "Grammar", level: "Challenge", time: "6 دقائق", questions: 6, icon: "TR", description: "اختر الزمن الصحيح بسرعة.", mode: "race", timed: true },
    { id: "pronoun-match", title: "Pronoun Match", ar: "مطابقة الضمائر", category: "Grammar", skill: "Grammar", level: "Medium", time: "7 دقائق", questions: 5, icon: "PM", description: "طابق الضمير مع استخدامه الصحيح.", mode: "choice" },
    { id: "question-builder", title: "Question Builder", ar: "بناء السؤال", category: "Grammar", skill: "Grammar", level: "Medium", time: "8 دقائق", questions: 5, icon: "QB", description: "رتب الكلمات لبناء سؤال صحيح.", mode: "questionBuilder" },
    { id: "translation-match", title: "Translation Match", ar: "مطابقة الترجمة", category: "Sentences", skill: "Reading", level: "Easy", time: "8 دقائق", questions: 5, icon: "TM", description: "طابق الجملة الإنجليزية مع الترجمة العربية.", mode: "translation" },
    { id: "true-false-race", title: "True or False Race", ar: "سباق صح أو خطأ", category: "Sentences", skill: "Reading", level: "Challenge", time: "6 دقائق", questions: 5, icon: "TF", description: "قرر بسرعة هل الترجمة صحيحة أم خاطئة.", mode: "trueFalse", timed: true },
    { id: "reply-master", title: "Reply Master", ar: "اختيار الرد المناسب", category: "Conversations", skill: "Conversation", level: "Medium", time: "8 دقائق", questions: 4, icon: "RM", description: "اختر أفضل رد في موقف محادثة.", mode: "reply", supportsListen: true },
    { id: "dialogue-builder", title: "Dialogue Builder", ar: "بناء الحوار", category: "Conversations", skill: "Conversation", level: "Challenge", time: "10 دقائق", questions: 4, icon: "DB", description: "رتب جمل الحوار بالترتيب الصحيح.", mode: "dialogue" },
    { id: "speak-challenge", title: "Speak Challenge", ar: "تحدي النطق", category: "Speaking", skill: "Speaking", level: "Challenge", time: "6 دقائق", questions: 4, icon: "SC", description: "اقرأ الكلمة أو الجملة بالمايك واحصل على تقييم.", mode: "speak", supportsMic: true, supportsListen: true },
    { id: "one-minute", title: "One Minute Challenge", ar: "تحدي الدقيقة", category: "Speed", skill: "Reading", level: "Challenge", time: "60 ثانية", questions: 10, icon: "OM", description: "أجب عن أكبر عدد من الأسئلة خلال 60 ثانية.", mode: "oneMinute", timed: true },
];

let gamesState = {
    points: 0,
    actions: 0,
    completed: false,
    completedGames: [],
    bestScore: 0,
    bestGameName: "-",
    lastPlayedGame: "-",
    todayBestScore: 0,
    daily: {},
};
let activeGame = null;
let activeQuestions = [];
let activeIndex = 0;
let roundScore = 0;
let currentAnswer = "";
let mistakes = [];
let timerId = null;
let secondsLeft = 0;

function csrfToken() {
    return document.cookie.split(";").map((value) => value.trim()).find((value) => value.startsWith("csrftoken="))?.split("=")[1] || "";
}

function normalizeText(value) {
    return String(value || "").toLowerCase().replace(/[^\w\s?.,']/g, "").replace(/\s+/g, " ").trim();
}

function similarityScore(source, target) {
    const a = normalizeText(source);
    const b = normalizeText(target);
    if (!a || !b) return 0;
    if (a === b) return 100;
    const words = b.split(" ");
    const hits = words.filter((word) => a.includes(word)).length;
    return Math.round((hits / Math.max(words.length, 1)) * 100);
}

function speakText(text, rate = 0.9) {
    try {
        if (!("speechSynthesis" in window)) {
            showFeedback("النطق غير مدعوم في هذا المتصفح.", "wrong");
            return;
        }
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = "en-US";
        utterance.rate = rate;
        window.speechSynthesis.speak(utterance);
    } catch {
        showFeedback("تعذر تشغيل النطق الآن.", "wrong");
    }
}

function loadGamesProgress() {
    try {
        const local = JSON.parse(localStorage.getItem("gamesCenterProgress") || "{}");
        gamesState = {
            points: Number(local.points ?? document.body.dataset.initialPoints ?? 0),
            actions: Number(local.actions ?? document.body.dataset.initialActions ?? 0),
            completed: local.completed ?? document.body.dataset.initialCompleted === "true",
            completedGames: Array.isArray(local.completedGames) ? local.completedGames : [],
            bestScore: Number(local.bestScore || 0),
            bestGameName: local.bestGameName || "-",
            lastPlayedGame: local.lastPlayedGame || "-",
            todayBestScore: Number(local.todayBestScore || 0),
            daily: local.daily || {},
            fiveBonusAwarded: Boolean(local.fiveBonusAwarded),
        };
    } catch {
        gamesState.points = Number(document.body.dataset.initialPoints || 0);
        gamesState.actions = Number(document.body.dataset.initialActions || 0);
    }
}

function saveGamesProgress() {
    localStorage.setItem("gamesCenterProgress", JSON.stringify(gamesState));
}

async function awardGamePoints(activityType, points, completed = false, gameId = "") {
    let pointsToAward = points;
    gamesState.actions += 1;
    if (completed && gameId && !gamesState.completedGames.includes(gameId)) {
        gamesState.completedGames.push(gameId);
    }
    if (gamesState.completedGames.length >= 5 && !gamesState.fiveBonusAwarded) {
        pointsToAward += 20;
        gamesState.fiveBonusAwarded = true;
    }
    if (gamesState.points + pointsToAward >= 150 && !gamesState.completed) {
        gamesState.completed = true;
        pointsToAward += 50;
        completed = true;
    }
    gamesState.points += pointsToAward;
    saveGamesProgress();
    updateGamesStats();

    try {
        const response = await fetch(window.GAMES_PROGRESS_URL || "/api/english-foundation/progress/", {
            method: "POST",
            headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
            body: JSON.stringify({ section: "games", activity_type: activityType, points: pointsToAward, completed }),
        });
        const data = await response.json();
        if (data.status === "ok") {
            gamesState.points = data.points;
            gamesState.actions = data.actions_count;
            gamesState.completed = data.completed;
            saveGamesProgress();
            updateGamesStats();
        }
    } catch {
        // TODO: integrate games progress with StudentActivity leaderboard.
    }
}

function statusFromPoints(points) {
    if (points >= 150) return "متقن";
    if (points >= 80) return "ممتاز";
    if (points >= 30) return "جيد";
    return "قيد التدريب";
}

function updateGamesStats() {
    document.getElementById("gamesPoints").textContent = gamesState.points;
    document.getElementById("gamesActions").textContent = gamesState.actions;
    document.getElementById("gamesStatus").textContent = statusFromPoints(gamesState.points);
    document.getElementById("gamesCompleted").textContent = gamesState.completedGames.length;
    document.getElementById("gamesBestScore").textContent = gamesState.bestScore;
    document.getElementById("gamesProgressBar").style.width = `${Math.min(100, Math.round((gamesState.points / 150) * 100))}%`;
    document.getElementById("todayBestScore").textContent = gamesState.todayBestScore;
    document.getElementById("bestGameName").textContent = gamesState.bestGameName;
    document.getElementById("boardCompleted").textContent = gamesState.completedGames.length;
    document.getElementById("lastPlayedGame").textContent = gamesState.lastPlayedGame;
}

function cardActions(game) {
    const extra = [
        game.supportsListen ? `<button class="listen-action" type="button" data-action="listen" data-id="${game.id}">استماع</button>` : "",
        game.supportsMic ? `<button class="mic-action" type="button" data-action="mic" data-id="${game.id}">مايك</button>` : "",
    ].join("");
    return `
        <button class="start-action" type="button" data-action="start" data-id="${game.id}">ابدأ اللعبة</button>
        <button type="button" data-action="level" data-id="${game.id}">اختيار المستوى</button>
        <button type="button" data-action="explain" data-id="${game.id}">شرح اللعبة</button>
        <button type="button" data-action="result" data-id="${game.id}">عرض النتيجة</button>
        ${extra}
    `;
}

function gameCard(game) {
    return `
        <article class="game-card" data-id="${game.id}" data-category="${game.category}" data-skill="${game.skill}" data-level="${game.level}">
            <div class="game-icon" aria-hidden="true">${game.icon}</div>
            <h2>${game.title}</h2>
            <p class="arabic-title">${game.ar}</p>
            <p class="game-description">${game.description}</p>
            <div class="meta-grid">
                <div class="meta"><span>التصنيف</span><strong>${game.category}</strong></div>
                <div class="meta"><span>المستوى</span><strong>${game.level}</strong></div>
                <div class="meta"><span>الوقت</span><strong>${game.time}</strong></div>
                <div class="meta"><span>عدد الأسئلة</span><strong>${game.questions}</strong></div>
                <div class="meta"><span>المهارة</span><strong>${game.skill}</strong></div>
                <div class="meta"><span>أفضل نتيجة</span><strong>${localStorage.getItem(`gameBest:${game.id}`) || 0}</strong></div>
            </div>
            <div class="game-actions">${cardActions(game)}</div>
        </article>
    `;
}

function renderGameCards(items = gamesData) {
    document.getElementById("gamesGrid").innerHTML = items.map(gameCard).join("");
    document.getElementById("emptyGames").hidden = items.length > 0;
}

function searchGames() {
    const query = document.getElementById("gameSearch").value.trim().toLowerCase();
    const category = document.getElementById("categoryFilter").value;
    const skill = document.getElementById("skillFilter").value;
    const level = document.getElementById("levelFilter").value;
    const filtered = gamesData.filter((game) => {
        const text = `${game.title} ${game.ar} ${game.category} ${game.skill}`.toLowerCase();
        return (!query || text.includes(query))
            && (category === "all" || game.category === category)
            && (skill === "all" || game.skill === skill)
            && (level === "all" || game.level === level);
    });
    renderGameCards(filtered);
}

function filterGames(category) {
    document.getElementById("categoryFilter").value = category;
    document.querySelectorAll("[data-filter-category]").forEach((button) => {
        button.classList.toggle("active", button.dataset.filterCategory === category);
    });
    searchGames();
}

function dailyChallenge() {
    const today = new Date().toISOString().slice(0, 10);
    if (gamesState.daily.date !== today) {
        gamesState.daily = {
            date: today,
            ids: ["word-match", "grammar-fix", "speak-challenge"],
            completed: [],
            bonusAwarded: false,
        };
        saveGamesProgress();
    }
    document.getElementById("dailyChallengeGames").innerHTML = gamesState.daily.ids.map((id) => {
        const game = gamesData.find((item) => item.id === id);
        const done = gamesState.daily.completed.includes(id) ? "مكتملة" : "جاهزة";
        return `<div class="daily-game"><span>${game.title}</span><span>${done}</span></div>`;
    }).join("");
}

function dataForGame(game) {
    if (["flashcards", "word-match", "emoji-choice", "listen-choose", "memory-game", "word-builder"].includes(game.id)) return vocabularyGameData;
    if (["sentence-builder", "translation-match", "true-false-race"].includes(game.id)) return sentenceGameData;
    if (["reply-master", "dialogue-builder"].includes(game.id)) return conversationGameData;
    return grammarGameData;
}

function buildQuestion(game, item) {
    if (game.mode === "emoji") return { prompt: item.emoji, answer: item.prompt, options: vocabularyGameData.map((entry) => entry.prompt).slice(0, 3) };
    if (game.mode === "builder") return { prompt: `رتب الحروف: ${item.letters.split("").sort().join(" / ")}`, answer: item.prompt, input: true };
    if (game.mode === "sentenceBuilder") return { prompt: `رتب: ${item.words.slice().reverse().join(" / ")}`, answer: item.prompt, input: true };
    if (game.mode === "questionBuilder") return { prompt: "رتب السؤال: live / you / do / Where ?", answer: "Where do you live?", input: true };
    if (game.mode === "grammarFix") return { prompt: item.prompt, answer: item.fixed, options: item.options };
    if (game.mode === "dialogue") return { prompt: `رتب الحوار: ${item.order.slice().reverse().join(" / ")}`, answer: item.order.join(" "), input: true };
    if (game.mode === "trueFalse") return { prompt: `${item.prompt} = ${item.answer}`, answer: item.trueFalse ? "True" : "False", options: ["True", "False"] };
    if (game.mode === "listen") return { prompt: "اضغط استماع ثم اختر المعنى", speak: item.prompt, answer: item.answer, options: item.options };
    if (game.mode === "speak") return { prompt: item.prompt, answer: item.prompt, mic: true };
    if (game.mode === "flashcards") return { prompt: item.prompt, answer: item.answer, options: ["إظهار الإجابة"], flashcard: true };
    if (game.mode === "oneMinute") return { prompt: item.prompt, answer: item.answer, options: item.options };
    return { prompt: item.prompt, answer: item.answer, options: item.options };
}

function openGameModal(id) {
    activeGame = gamesData.find((game) => game.id === id);
    if (!activeGame) return;
    document.getElementById("modalGameTitle").textContent = activeGame.title;
    document.getElementById("modalGameCategory").textContent = `${activeGame.category} / ${activeGame.skill}`;
    document.getElementById("modalGameInstructions").textContent = activeGame.description;
    document.getElementById("modalLevel").value = activeGame.level;
    document.getElementById("gameModal").hidden = false;
    document.getElementById("questionArea").innerHTML = "";
    document.getElementById("answerArea").innerHTML = "";
    showFeedback("اختر المستوى ثم اضغط بدء.", "neutral");
    awardGamePoints("open", 1, false, id);
}

function startGame() {
    if (!activeGame) return;
    const data = dataForGame(activeGame);
    activeQuestions = data.slice(0, activeGame.questions).map((item) => buildQuestion(activeGame, item));
    activeIndex = 0;
    roundScore = 0;
    mistakes = [];
    if (activeGame.id === "one-minute") {
        secondsLeft = 60;
        startTimer();
    } else if (activeGame.timed) {
        secondsLeft = 30;
        startTimer();
    } else {
        stopTimer();
    }
    renderActiveQuestion();
}

function startTimer() {
    stopTimer();
    document.getElementById("roundTimer").textContent = secondsLeft;
    timerId = window.setInterval(() => {
        secondsLeft -= 1;
        document.getElementById("roundTimer").textContent = secondsLeft;
        if (secondsLeft <= 0) finishGame();
    }, 1000);
}

function stopTimer() {
    if (timerId) window.clearInterval(timerId);
    timerId = null;
    document.getElementById("roundTimer").textContent = "0";
}

function renderActiveQuestion() {
    const question = activeQuestions[activeIndex];
    if (!question) {
        finishGame();
        return;
    }
    currentAnswer = "";
    document.getElementById("roundScore").textContent = roundScore;
    document.getElementById("roundProgress").textContent = `${activeIndex + 1} / ${activeQuestions.length}`;
    document.getElementById("questionArea").innerHTML = `<div class="question-card">${question.prompt}</div>`;
    if (question.speak) {
        document.getElementById("questionArea").innerHTML += `<button type="button" data-modal-action="listen-current">استماع</button>`;
    }
    if (question.mic) {
        document.getElementById("answerArea").innerHTML = `<button class="mic-action" type="button" data-modal-action="mic-current">مايك</button><input class="text-answer" id="textAnswer" placeholder="أو اكتب ما قرأت">`;
    } else if (question.input) {
        document.getElementById("answerArea").innerHTML = `<input class="text-answer" id="textAnswer" placeholder="اكتب الإجابة">`;
    } else {
        document.getElementById("answerArea").innerHTML = `<div class="option-grid">${question.options.map((option) => `<button type="button" data-option="${option}">${option}</button>`).join("")}</div>`;
    }
    showFeedback("", "neutral", true);
}

function selectedAnswer() {
    const input = document.getElementById("textAnswer");
    return input ? input.value : currentAnswer;
}

function checkAnswer() {
    const question = activeQuestions[activeIndex];
    if (!question) return;
    const answer = selectedAnswer();
    const correct = normalizeText(answer) === normalizeText(question.answer);
    if (correct) {
        roundScore += 10;
        awardGamePoints("exercise", 2, false, activeGame.id);
        showFeedback("إجابة صحيحة.", "correct");
    } else {
        mistakes.push({ prompt: question.prompt, answer: question.answer, selected: answer || "-" });
        showFeedback(`حاول مرة أخرى. الإجابة: ${question.answer}`, "wrong");
    }
    document.getElementById("roundScore").textContent = roundScore;
}

function nextQuestion() {
    activeIndex += 1;
    renderActiveQuestion();
}

function finishGame() {
    stopTimer();
    if (!activeGame) return;
    const perfect = mistakes.length === 0 && activeQuestions.length > 0;
    let earned = 7 + (perfect ? 10 : 0) + (activeGame.id === "one-minute" ? 10 : 0);
    gamesState.lastPlayedGame = activeGame.title;
    if (roundScore > gamesState.bestScore) {
        gamesState.bestScore = roundScore;
        gamesState.bestGameName = activeGame.title;
    }
    gamesState.todayBestScore = Math.max(gamesState.todayBestScore, roundScore);
    localStorage.setItem(`gameBest:${activeGame.id}`, String(Math.max(Number(localStorage.getItem(`gameBest:${activeGame.id}`) || 0), roundScore)));
    earned += markDailyComplete(activeGame.id);
    awardGamePoints("game", earned, true, activeGame.id);
    showFeedback(`النتيجة: ${roundScore}. الأخطاء: ${mistakes.length}. النقاط المكتسبة: ${earned}.`, perfect ? "correct" : "neutral");
    updateGamesStats();
}

function markDailyComplete(gameId) {
    dailyChallenge();
    let bonus = 0;
    if (gamesState.daily.ids.includes(gameId) && !gamesState.daily.completed.includes(gameId)) {
        gamesState.daily.completed.push(gameId);
    }
    if (gamesState.daily.completed.length >= 3 && !gamesState.daily.bonusAwarded) {
        gamesState.daily.bonusAwarded = true;
        bonus = 20;
    }
    saveGamesProgress();
    dailyChallenge();
    return bonus;
}

function reviewMistakes() {
    if (!mistakes.length) {
        showFeedback("لا توجد أخطاء للمراجعة.", "correct");
        return;
    }
    document.getElementById("questionArea").innerHTML = mistakes.map((item) => `<div class="question-card">${item.prompt}<br>إجابتك: ${item.selected}<br>الصحيح: ${item.answer}</div>`).join("");
    document.getElementById("answerArea").innerHTML = "";
}

function showFeedback(message, state = "neutral", hide = false) {
    const box = document.getElementById("gameFeedback");
    box.hidden = hide || !message;
    box.className = `feedback-box ${state}`;
    box.textContent = message;
}

function startMicPractice() {
    const speechQuestion = activeQuestions[activeIndex];
    showFeedback(`${SpeechService.messages.listening} ${speechQuestion.answer}`, "neutral");
    SpeechService.startRecognition({
        targetText: speechQuestion.answer,
        type: speechQuestion.answer.split(/\s+/).length > 1 ? "short_sentence" : "word",
        section: "games",
        level: activeGame?.id || "",
        onResult: (result) => {
            document.getElementById("textAnswer").value = result.spokenText || result.spoken || "";
            awardGamePoints("mic", 3, result.status === "excellent", activeGame.id);
            showFeedback(`${SpeechService.statusLabel(result.status)}: ${result.score}%`, result.status === "excellent" ? "correct" : result.status === "good" ? "neutral" : "wrong");
        },
        onError: (result) => showFeedback(result.message || SpeechService.messages.unknown, "wrong")
    });
    return;
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) {
        showFeedback("الميكروفون غير مدعوم في هذا المتصفح، جرب Google Chrome.", "wrong");
        return;
    }
    const question = activeQuestions[activeIndex];
    const recognition = new Recognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        const score = similarityScore(transcript, question.answer);
        document.getElementById("textAnswer").value = transcript;
        awardGamePoints("mic", 3, false, activeGame.id);
        if (score >= 85) showFeedback(`ممتاز: ${score}%`, "correct");
        else if (score >= 60) showFeedback(`جيد: ${score}%`, "neutral");
        else showFeedback(`حاول مرة أخرى: ${score}%`, "wrong");
    };
    recognition.onerror = () => showFeedback("تعذر تشغيل المايك الآن. اسمح للمتصفح باستخدام الميكروفون ثم حاول مرة أخرى.", "wrong");
    recognition.start();
}

function flashcardsGame() { openGameModal("flashcards"); }
function wordMatchGame() { openGameModal("word-match"); }
function emojiChoiceGame() { openGameModal("emoji-choice"); }
function listenAndChooseGame() { openGameModal("listen-choose"); }
function fillBlankGame() { openGameModal("fill-blank"); }
function memoryGame() { openGameModal("memory-game"); }
function wordBuilderGame() { openGameModal("word-builder"); }
function sentenceBuilderGame() { openGameModal("sentence-builder"); }
function grammarFixGame() { openGameModal("grammar-fix"); }
function tenseRaceGame() { openGameModal("tense-race"); }
function pronounMatchGame() { openGameModal("pronoun-match"); }
function questionBuilderGame() { openGameModal("question-builder"); }
function translationMatchGame() { openGameModal("translation-match"); }
function trueFalseRaceGame() { openGameModal("true-false-race"); }
function replyMasterGame() { openGameModal("reply-master"); }
function dialogueBuilderGame() { openGameModal("dialogue-builder"); }
function speakChallengeGame() { openGameModal("speak-challenge"); }
function oneMinuteChallenge() { openGameModal("one-minute"); }

document.addEventListener("DOMContentLoaded", () => {
    loadGamesProgress();
    renderGameCards();
    dailyChallenge();
    updateGamesStats();
    document.querySelector('[data-filter-category="all"]')?.classList.add("active");

    document.getElementById("gameSearch").addEventListener("input", searchGames);
    document.getElementById("categoryFilter").addEventListener("change", (event) => filterGames(event.target.value));
    document.getElementById("skillFilter").addEventListener("change", searchGames);
    document.getElementById("levelFilter").addEventListener("change", searchGames);
    document.getElementById("beginGame").addEventListener("click", startGame);
    document.getElementById("checkGameAnswer").addEventListener("click", checkAnswer);
    document.getElementById("nextGameQuestion").addEventListener("click", nextQuestion);
    document.getElementById("finishGameRound").addEventListener("click", finishGame);
    document.getElementById("reviewMistakesBtn").addEventListener("click", reviewMistakes);
    document.getElementById("explainGame").addEventListener("click", () => activeGame && showFeedback(activeGame.description, "neutral"));
    document.getElementById("startDailyChallenge").addEventListener("click", () => openGameModal(gamesState.daily.ids[0]));

    document.addEventListener("click", (event) => {
        const categoryButton = event.target.closest("[data-filter-category]");
        if (categoryButton) {
            filterGames(categoryButton.dataset.filterCategory);
            return;
        }
        const levelButton = event.target.closest("[data-level-chip]");
        if (levelButton) {
            document.getElementById("levelFilter").value = levelButton.dataset.levelChip;
            searchGames();
            return;
        }
        const actionButton = event.target.closest("[data-action]");
        if (actionButton) {
            const game = gamesData.find((item) => item.id === actionButton.dataset.id);
            if (!game) return;
            if (actionButton.dataset.action === "start" || actionButton.dataset.action === "level") openGameModal(game.id);
            if (actionButton.dataset.action === "explain") {
                openGameModal(game.id);
                showFeedback(game.description, "neutral");
            }
            if (actionButton.dataset.action === "result") alert(`أفضل نتيجة: ${localStorage.getItem(`gameBest:${game.id}`) || 0}`);
            if (actionButton.dataset.action === "listen") speakText((dataForGame(game)[0] || {}).prompt || game.title);
            if (actionButton.dataset.action === "mic") {
                openGameModal(game.id);
                startGame();
                startMicPractice();
            }
        }
        const option = event.target.closest("[data-option]");
        if (option) {
            currentAnswer = option.dataset.option;
            document.querySelectorAll("[data-option]").forEach((button) => button.classList.remove("selected"));
            option.classList.add("selected");
        }
        if (event.target.closest("[data-modal-action='listen-current']")) {
            const question = activeQuestions[activeIndex];
            speakText(question.speak || question.answer || question.prompt);
        }
        if (event.target.closest("[data-modal-action='mic-current']")) startMicPractice();
        if (event.target.matches("[data-close-modal]") || event.target.classList.contains("game-modal")) {
            stopTimer();
            document.getElementById("gameModal").hidden = true;
        }
    });
});
