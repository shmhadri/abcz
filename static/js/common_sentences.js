(function () {
    "use strict";

    const progressKey = "abcz-common-sentences-progress-v1";
    const themeKey = "abcz-common-sentences-theme";
    const categories = ["Polite Expressions", "Daily Life", "School", "Classroom Commands", "Questions", "Feelings", "Shopping", "Travel", "Health", "Speaking Practice"];
    const emojiByCategory = {
        "Polite Expressions": "🤝",
        "Daily Life": "🏠",
        School: "🏫",
        "Classroom Commands": "📘",
        Questions: "❓",
        Feelings: "😊",
        Shopping: "🛒",
        Travel: "✈️",
        Health: "🏥",
        "Speaking Practice": "🎙️"
    };

    const rawSentences = [
        ["Good morning.", "صباح الخير.", "Polite Expressions", "Easy"],
        ["Good afternoon.", "مساء الخير.", "Polite Expressions", "Easy"],
        ["Good evening.", "مساء الخير.", "Polite Expressions", "Easy"],
        ["How are you today?", "كيف حالك اليوم؟", "Daily Life", "Easy"],
        ["I am fine, thank you.", "أنا بخير، شكرًا لك.", "Daily Life", "Easy"],
        ["Nice to meet you.", "سعيد بلقائك.", "Polite Expressions", "Easy"],
        ["What is your name?", "ما اسمك؟", "Questions", "Easy"],
        ["My name is Ahmed.", "اسمي أحمد.", "Daily Life", "Easy"],
        ["Where do you live?", "أين تسكن؟", "Questions", "Easy"],
        ["I live in Saudi Arabia.", "أعيش في السعودية.", "Daily Life", "Easy"],
        ["Please open your book.", "من فضلك افتح كتابك.", "Classroom Commands", "Easy"],
        ["Please close your book.", "من فضلك أغلق كتابك.", "Classroom Commands", "Easy"],
        ["Listen carefully.", "استمع جيدًا.", "Classroom Commands", "Easy"],
        ["Repeat after me.", "كرر بعدي.", "Classroom Commands", "Easy"],
        ["Raise your hand.", "ارفع يدك.", "Classroom Commands", "Easy"],
        ["May I ask a question?", "هل يمكنني أن أسأل سؤالًا؟", "School", "Medium"],
        ["Can you help me, please?", "هل يمكنك مساعدتي من فضلك؟", "Polite Expressions", "Easy"],
        ["I do not understand.", "أنا لا أفهم.", "School", "Easy"],
        ["Can you say that again?", "هل يمكنك قول ذلك مرة أخرى؟", "Speaking Practice", "Medium"],
        ["Can you speak slowly?", "هل يمكنك التحدث ببطء؟", "Speaking Practice", "Medium"],
        ["I finished my homework.", "أنهيت واجبي المنزلي.", "School", "Easy"],
        ["I forgot my notebook.", "نسيت دفتري.", "School", "Easy"],
        ["The lesson is easy.", "الدرس سهل.", "School", "Easy"],
        ["The test is difficult.", "الاختبار صعب.", "School", "Easy"],
        ["I like English.", "أحب اللغة الإنجليزية.", "School", "Easy"],
        ["I want to improve my reading.", "أريد أن أحسن قراءتي.", "Speaking Practice", "Medium"],
        ["I am happy today.", "أنا سعيد اليوم.", "Feelings", "Easy"],
        ["I feel tired.", "أشعر بالتعب.", "Feelings", "Easy"],
        ["I am excited.", "أنا متحمس.", "Feelings", "Easy"],
        ["I am worried about the exam.", "أنا قلق بشأن الاختبار.", "Feelings", "Medium"],
        ["Do not worry.", "لا تقلق.", "Feelings", "Easy"],
        ["Everything will be okay.", "كل شيء سيكون بخير.", "Feelings", "Medium"],
        ["How much is this?", "بكم هذا؟", "Shopping", "Easy"],
        ["It is too expensive.", "إنه غالي جدًا.", "Shopping", "Easy"],
        ["Do you have a cheaper one?", "هل لديك واحد أرخص؟", "Shopping", "Medium"],
        ["I would like to buy this.", "أود شراء هذا.", "Shopping", "Medium"],
        ["Can I pay by card?", "هل يمكنني الدفع بالبطاقة؟", "Shopping", "Medium"],
        ["Where is the airport?", "أين المطار؟", "Travel", "Easy"],
        ["I need a taxi.", "أحتاج سيارة أجرة.", "Travel", "Easy"],
        ["I have a ticket.", "لدي تذكرة.", "Travel", "Easy"],
        ["Where is my seat?", "أين مقعدي؟", "Travel", "Easy"],
        ["I lost my bag.", "فقدت حقيبتي.", "Travel", "Medium"],
        ["I need help.", "أحتاج مساعدة.", "Travel", "Easy"],
        ["I have a headache.", "لدي صداع.", "Health", "Easy"],
        ["I feel sick.", "أشعر بالمرض.", "Health", "Easy"],
        ["I need a doctor.", "أحتاج طبيبًا.", "Health", "Easy"],
        ["Take this medicine.", "خذ هذا الدواء.", "Health", "Easy"],
        ["Drink more water.", "اشرب ماءً أكثر.", "Health", "Easy"],
        ["You should rest.", "يجب أن ترتاح.", "Health", "Easy"],
        ["What time is it?", "كم الساعة؟", "Questions", "Easy"],
        ["What is your favorite sport?", "ما رياضتك المفضلة؟", "Questions", "Easy"],
        ["Why are you late?", "لماذا أنت متأخر؟", "Questions", "Medium"],
        ["How do you spell your name?", "كيف تتهجى اسمك؟", "Questions", "Medium"],
        ["I like playing football.", "أحب لعب كرة القدم.", "Daily Life", "Easy"],
        ["I usually wake up early.", "عادة أستيقظ مبكرًا.", "Daily Life", "Medium"],
        ["I go to school by bus.", "أذهب إلى المدرسة بالحافلة.", "Daily Life", "Easy"],
        ["My favorite subject is English.", "مادتي المفضلة هي الإنجليزية.", "School", "Easy"],
        ["I am proud of myself.", "أنا فخور بنفسي.", "Feelings", "Medium"],
        ["Practice makes progress.", "التدريب يصنع التقدم.", "Speaking Practice", "Challenge"],
        ["Never give up.", "لا تستسلم أبدًا.", "Speaking Practice", "Easy"]
    ];

    function slugify(value) {
        return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
    }

    function buildMissingWord(sentence) {
        const words = sentence.replace(/[?.!]/g, "").split(/\s+/).filter(Boolean);
        const index = Math.min(words.length - 1, Math.max(0, Math.floor(words.length / 2)));
        const answer = words[index];
        const blank = sentence.replace(new RegExp(`\\b${escapeRegExp(answer)}\\b`, "i"), "____");
        return { blank, answer, orderWords: words };
    }

    const commonSentencesData = rawSentences.map((row, index) => {
        const [sentence, arabic, category, level] = row;
        const missing = buildMissingWord(sentence);
        const wrongReplies = rawSentences.filter((_, i) => i !== index).slice(index + 1, index + 4).map(item => item[1]);
        while (wrongReplies.length < 3) wrongReplies.push(rawSentences[wrongReplies.length][1]);
        return {
            id: slugify(sentence),
            sentence,
            arabic,
            category,
            level,
            emoji: emojiByCategory[category] || "🗣️",
            explanation_ar: `تستخدم هذه الجملة في مواقف ${category} للتواصل بسرعة ووضوح.`,
            example_context_ar: `مثال موقف: قل "${arabic}" عندما تحتاج إلى هذه العبارة في المدرسة أو الحياة اليومية.`,
            missing_word: missing.answer,
            blank_sentence: missing.blank,
            true_false_translation: arabic,
            correct_reply: arabic,
            wrong_replies: wrongReplies,
            order_words: missing.orderWords
        };
    });

    const els = {};
    let activeCategory = "";
    let readingStartedAt = 0;
    let readingSample = [];
    let minuteScore = 0;
    let progress = loadCommonSentenceProgress();

    function escapeRegExp(value) {
        return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    }

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
        const button = document.getElementById("csThemeToggle");
        if (button) {
            button.setAttribute("aria-pressed", String(nextTheme === "dark"));
            button.textContent = nextTheme === "dark" ? "الوضع الفاتح" : "الوضع الداكن";
        }
        try { localStorage.setItem(themeKey, nextTheme); } catch {}
    }

    function loadCommonSentenceProgress() {
        const initial = window.COMMON_SENTENCES_INITIAL_PROGRESS || {};
        const fallback = {
            points: Number(initial.points || 0),
            actions: Number(initial.actions || 0),
            mastered: [],
            review: [],
            completed: Boolean(initial.completed),
            tenBonus: false
        };
        try {
            return { ...fallback, ...JSON.parse(localStorage.getItem(progressKey) || "{}") };
        } catch {
            return fallback;
        }
    }

    function saveCommonSentenceProgress() {
        localStorage.setItem(progressKey, JSON.stringify(progress));
    }

    function csrfToken() {
        return document.cookie.split(";").map(v => v.trim()).find(v => v.startsWith("csrftoken="))?.split("=")[1] || "";
    }

    async function awardCommonSentencePoints(activityType, points, options = {}) {
        progress.points = Math.max(0, Number(progress.points || 0) + points);
        progress.actions = Math.max(0, Number(progress.actions || 0) + 1);
        if (options.masteredSentence && !progress.mastered.includes(options.masteredSentence)) {
            progress.mastered.push(options.masteredSentence);
            progress.review = progress.review.filter(id => id !== options.masteredSentence);
        }
        if (options.reviewSentence && !progress.review.includes(options.reviewSentence) && !progress.mastered.includes(options.reviewSentence)) {
            progress.review.push(options.reviewSentence);
        }
        if (progress.mastered.length >= 10 && !progress.tenBonus) {
            progress.tenBonus = true;
            progress.points += 20;
        }
        if (options.completed) progress.completed = true;
        saveCommonSentenceProgress();
        updateCommonSentenceStats();
        // TODO: integrate common sentences progress with StudentActivity leaderboard.
        try {
            const response = await fetch(window.COMMON_SENTENCES_PROGRESS_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
                body: JSON.stringify({ section: "common_sentences", activity_type: activityType, points, completed: Boolean(options.completed) })
            });
            const data = await response.json();
            if (data.status === "ok") {
                progress.points = data.points;
                progress.actions = data.actions_count;
                progress.completed = data.completed || progress.completed;
                saveCommonSentenceProgress();
                updateCommonSentenceStats();
            }
        } catch {
            updateCommonSentenceStats();
        }
    }

    function statusFor(points) {
        if (progress.completed || points >= 150) return "متقن";
        if (points >= 80) return "ممتاز";
        if (points >= 30) return "جيد";
        return "قيد التدريب";
    }

    function updateCommonSentenceStats() {
        const points = Number(progress.points || 0);
        els.points.textContent = points;
        els.actions.textContent = Number(progress.actions || 0);
        els.status.textContent = statusFor(points);
        els.mastered.textContent = `${progress.mastered.length} / ${commonSentencesData.length}`;
        els.progressFill.style.width = `${Math.min(100, Math.round((points / 150) * 100))}%`;
    }

    function renderCategoryOptions() {
        els.category.innerHTML = `<option value="">كل التصنيفات</option>` + categories.map(category => `<option value="${category}">${category}</option>`).join("");
    }

    function filterSentences() {
        const query = normalizeText(els.search.value);
        const category = activeCategory || els.category.value;
        const level = els.level.value;
        return commonSentencesData.filter(item => {
            const haystack = normalizeText(`${item.sentence} ${item.arabic} ${item.category} ${item.explanation_ar}`);
            return (!query || haystack.includes(query)) && (!category || item.category === category) && (!level || item.level === level);
        });
    }

    function searchSentences() {
        renderSentenceCards();
    }

    function renderSentenceCards() {
        const rows = filterSentences();
        els.grid.innerHTML = rows.map(item => {
            const mastered = progress.mastered.includes(item.id);
            return `
                <article class="cs-card" data-sentence="${escapeHtml(item.id)}">
                    <div class="cs-card-top">
                        <div class="cs-emoji">${escapeHtml(item.emoji)}</div>
                        <div>
                            <div class="cs-badges">
                                <span class="cs-badge">${escapeHtml(item.category)}</span>
                                <span class="cs-badge level">${escapeHtml(item.level)}</span>
                                ${mastered ? `<span class="cs-badge">متقنة</span>` : ""}
                            </div>
                            <h2 class="cs-sentence">${escapeHtml(item.sentence)}</h2>
                        </div>
                    </div>
                    <div class="cs-ar">${escapeHtml(item.arabic)}</div>
                    <div class="cs-explain">${escapeHtml(item.explanation_ar)}</div>
                    <div class="cs-context">${escapeHtml(item.example_context_ar)}</div>
                    <div class="cs-actions">
                        <button class="cs-action open" type="button" data-action="open" data-id="${escapeHtml(item.id)}">ابدأ</button>
                        <button class="cs-action listen" type="button" data-action="listen" data-id="${escapeHtml(item.id)}">استماع</button>
                        <button class="cs-action slow" type="button" data-action="slow" data-id="${escapeHtml(item.id)}">قراءة بطيئة</button>
                        <button class="cs-action train" type="button" data-action="training" data-id="${escapeHtml(item.id)}">حل تدريب</button>
                        <button class="cs-action mic" type="button" data-action="mic" data-id="${escapeHtml(item.id)}">مايك</button>
                        <button class="cs-action review" type="button" data-action="review" data-id="${escapeHtml(item.id)}">أضف للمراجعة</button>
                    </div>
                </article>
            `;
        }).join("");
        els.empty.hidden = rows.length > 0;
    }

    function findSentence(id) {
        return commonSentencesData.find(item => item.id === id);
    }

    function speakText(text, rate = 0.9) {
        try {
            if (!("speechSynthesis" in window)) {
                openModal("<h2 id='csModalTitle'>النطق غير مدعوم</h2><p>جرّب Google Chrome لتفعيل النطق.</p>");
                return;
            }
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = "en-US";
            utterance.rate = rate;
            window.speechSynthesis.speak(utterance);
        } catch {
            openModal("<h2 id='csModalTitle'>تعذر تشغيل النطق</h2><p>حاول مرة أخرى.</p>");
        }
    }

    function speakSlow(text) {
        speakText(text, 0.65);
    }

    function stopSpeaking() {
        try { window.speechSynthesis?.cancel(); } catch {}
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

    function openSentenceModal(item) {
        openModal(`
            <h2 id="csModalTitle" class="cs-sentence">${escapeHtml(item.sentence)}</h2>
            <p class="cs-ar">${escapeHtml(item.arabic)}</p>
            <p class="cs-explain">${escapeHtml(item.explanation_ar)}</p>
            <p class="cs-context">${escapeHtml(item.example_context_ar)}</p>
            <div class="cs-actions">
                <button class="cs-action listen" type="button" data-modal-speak="${escapeHtml(item.sentence)}">نطق عادي</button>
                <button class="cs-action slow" type="button" data-modal-slow="${escapeHtml(item.sentence)}">نطق بطيء</button>
                <button class="cs-action train" type="button" data-modal-training="${escapeHtml(item.id)}">سؤال سريع</button>
                <button class="cs-action review" type="button" data-modal-master="${escapeHtml(item.id)}">حفظ كمتقنة</button>
                <button class="cs-action review" type="button" data-modal-stop>إيقاف النطق</button>
            </div>
            <h3>ما الترجمة الصحيحة لهذه الجملة؟</h3>
            ${translationOptions(item)}
            <div id="csTrainingFeedback"></div>
        `);
        awardCommonSentencePoints("open", 1);
    }

    function translationOptions(item) {
        const choices = shuffle([item.arabic, ...item.wrong_replies]).slice(0, 4);
        return `<div class="cs-options">${choices.map(choice => `<button class="cs-option" data-answer="${escapeHtml(choice)}" data-correct="${escapeHtml(item.arabic)}" data-id="${escapeHtml(item.id)}">${escapeHtml(choice)}</button>`).join("")}</div>`;
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

    function startMicPractice(item) {
        openModal(`<h2 id="csModalTitle">تدريب المايك</h2><p class="cs-sentence">${escapeHtml(item.sentence)}</p><div id="csSpeechResult"></div>`);
        SpeechService.startRecognition({
            targetText: item.sentence,
            type: "short_sentence",
            section: "common_sentences",
            level: item.level || "",
            onStart: () => SpeechService.renderResult("#csSpeechResult", { expected: item.sentence, spoken: SpeechService.messages.listening, score: 0, status: "retry" }),
            onResult: result => {
                SpeechService.renderResult("#csSpeechResult", result);
                awardCommonSentencePoints("mic", 3, { masteredSentence: result.status === "excellent" ? item.id : "", reviewSentence: result.status === "retry" ? item.id : "" });
                renderSentenceCards();
            },
            onError: result => SpeechService.renderResult("#csSpeechResult", result)
        });
        return;
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            openModal(`<h2 id="csModalTitle">تدريب المايك</h2><p>الميكروفون غير مدعوم في هذا المتصفح، جرّب Google Chrome.</p><p class="cs-sentence">${escapeHtml(item.sentence)}</p>`);
            return;
        }
        const recognition = new SpeechRecognition();
        recognition.lang = "en-US";
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.onresult = event => {
            const spoken = event.results[0][0].transcript;
            const score = similarityScore(item.sentence, spoken);
            const label = score >= 85 ? "ممتاز" : score >= 60 ? "جيد" : "حاول مرة أخرى";
            openModal(`<h2 id="csModalTitle">نتيجة المايك: ${escapeHtml(label)}</h2><p class="cs-sentence">${escapeHtml(item.sentence)}</p><p>قلت: <strong>${escapeHtml(spoken)}</strong></p><p>نسبة التطابق: <strong>${score}%</strong></p>`);
            awardCommonSentencePoints("mic", 3, { masteredSentence: score >= 85 ? item.id : "", reviewSentence: score < 60 ? item.id : "" });
            renderSentenceCards();
        };
        recognition.onerror = () => openModal(`<h2 id="csModalTitle">تعذر تشغيل المايك</h2><p>اسمح للمتصفح باستخدام الميكروفون ثم جرّب مرة أخرى.</p><p class="cs-sentence">${escapeHtml(item.sentence)}</p>`);
        openModal(`<h2 id="csModalTitle">استعد للقراءة</h2><p>اقرأ الجملة بصوت واضح.</p><p class="cs-sentence">${escapeHtml(item.sentence)}</p>`);
        recognition.start();
    }

    function trueFalseGame(item = randomSentence()) {
        const useCorrect = Math.random() > 0.35;
        const displayed = useCorrect ? item.arabic : randomSentence(item.id).arabic;
        openModal(`<h2 id="csModalTitle">True or False</h2><p class="cs-sentence">${escapeHtml(item.sentence)}</p><p class="cs-ar">${escapeHtml(displayed)}</p><button class="cs-btn" data-tf="true" data-correct="${useCorrect}" data-id="${item.id}">صح</button><button class="cs-btn" data-tf="false" data-correct="${useCorrect}" data-id="${item.id}">خطأ</button><div id="csTrainingFeedback"></div>`);
    }

    function chooseTranslationGame(item = randomSentence()) {
        openModal(`<h2 id="csModalTitle">Choose Translation</h2><p class="cs-sentence">${escapeHtml(item.sentence)}</p>${translationOptions(item)}<div id="csTrainingFeedback"></div>`);
    }

    function fillBlankGame(item = randomSentence()) {
        openModal(`<h2 id="csModalTitle">Fill in the Blank</h2><p class="cs-sentence">${escapeHtml(item.blank_sentence)}</p><input id="csTrainingInput" placeholder="اكتب الكلمة الناقصة"><button class="cs-btn primary" data-check-blank="${item.id}">تحقق</button><div id="csTrainingFeedback"></div>`);
    }

    function sentenceOrderGame(item = randomSentence()) {
        openModal(`<h2 id="csModalTitle">Sentence Order</h2><p class="cs-context">${shuffle(item.order_words).join(" / ")}</p><input id="csTrainingInput" placeholder="اكتب الجملة بالترتيب"><button class="cs-btn primary" data-check-order="${item.id}">تحقق</button><div id="csTrainingFeedback"></div>`);
    }

    function listenAndChooseGame(item = randomSentence()) {
        openModal(`<h2 id="csModalTitle">Listen and Choose</h2><button class="cs-action listen" data-modal-speak="${escapeHtml(item.sentence)}">استمع</button>${translationOptions(item)}<div id="csTrainingFeedback"></div>`);
    }

    function quickMeaningGame(item = randomSentence()) {
        const choices = shuffle([item.sentence, ...shuffle(commonSentencesData.filter(row => row.id !== item.id)).slice(0, 3).map(row => row.sentence)]);
        openModal(`<h2 id="csModalTitle">Quick Meaning</h2><p class="cs-ar">${escapeHtml(item.arabic)}</p><div class="cs-options">${choices.map(choice => `<button class="cs-option" data-quick="${escapeHtml(choice)}" data-correct="${escapeHtml(item.sentence)}" data-id="${item.id}">${escapeHtml(choice)}</button>`).join("")}</div><div id="csTrainingFeedback"></div>`);
    }

    function readingSpeedTest() {
        readingSample = shuffle(commonSentencesData).slice(0, 5);
        readingStartedAt = Date.now();
        els.panel.hidden = false;
        els.panel.innerHTML = `<h2>اختبار سرعة القراءة</h2><p>اقرأ الجمل الخمس ثم اضغط أنهيت القراءة.</p><div class="cs-reading-list">${readingSample.map(item => `<div>${escapeHtml(item.sentence)}</div>`).join("")}</div><button class="cs-btn primary" id="csFinishReading">أنهيت القراءة</button><div id="csReadingResult"></div>`;
    }

    function finishReadingTest() {
        const seconds = Math.max(1, Math.round((Date.now() - readingStartedAt) / 1000));
        const words = readingSample.reduce((sum, item) => sum + item.sentence.split(/\s+/).length, 0);
        const wpm = Math.round((words / seconds) * 60);
        const rating = wpm < 50 ? "يحتاج تدريب" : wpm <= 90 ? "جيد" : "ممتاز";
        document.getElementById("csReadingResult").textContent = `الوقت: ${seconds} ثانية | الكلمات: ${words} | WPM: ${wpm} | التقييم: ${rating}`;
        awardCommonSentencePoints("reading_speed", 10);
    }

    function micReadingTest() {
        const sample = shuffle(commonSentencesData).slice(0, 3);
        openModal(`<h2 id="csModalTitle">اختبار بالمايك</h2><p>اقرأ الجمل التالية بالمايك.</p><div class="cs-reading-list">${sample.map(item => `<div>${escapeHtml(item.sentence)}</div>`).join("")}</div><button class="cs-action mic" data-mic-reading="${sample.map(item => item.id).join(",")}">ابدأ المايك</button>`);
    }

    function minuteChallenge() {
        const item = randomSentence();
        minuteScore = 0;
        els.panel.hidden = false;
        els.panel.dataset.minuteStarted = String(Date.now());
        els.panel.innerHTML = `<h2>Minute Challenge</h2><p>60 ثانية: اختر الترجمة الصحيحة.</p><p>Score: <strong id="csMinuteScore">0</strong></p><p class="cs-sentence">${escapeHtml(item.sentence)}</p>${translationOptions(item).replaceAll("data-answer", "data-minute-answer")}<div id="csGameFeedback"></div>`;
    }

    function sentenceFlashcards() {
        const item = randomSentence();
        els.panel.hidden = false;
        els.panel.innerHTML = `<h2>Sentence Flashcards</h2><p class="cs-sentence">${escapeHtml(item.sentence)}</p><button class="cs-btn primary" data-show-card="${item.id}">إظهار الترجمة</button><div id="csGameFeedback"></div>`;
    }

    function translationMatch() {
        choosePanelGame("Translation Match");
    }

    function sentenceBuilder() {
        const item = randomSentence();
        els.panel.hidden = false;
        els.panel.innerHTML = `<h2>Sentence Builder</h2><p class="cs-context">${shuffle(item.order_words).join(" / ")}</p><input id="csPanelInput" placeholder="رتب الجملة"><button class="cs-btn primary" data-panel-order="${item.id}">تحقق</button><div id="csGameFeedback"></div>`;
    }

    function listenRace() {
        const item = randomSentence();
        els.panel.hidden = false;
        els.panel.innerHTML = `<h2>Listen Race</h2><button class="cs-action listen" data-panel-speak="${escapeHtml(item.sentence)}">استمع</button>${translationOptions(item).replaceAll("data-answer", "data-panel-answer")}<div id="csGameFeedback"></div>`;
    }

    function trueFalseRace() {
        const item = randomSentence();
        const correct = Math.random() > 0.35;
        const displayed = correct ? item.arabic : randomSentence(item.id).arabic;
        els.panel.hidden = false;
        els.panel.innerHTML = `<h2>True or False Race</h2><p class="cs-sentence">${escapeHtml(item.sentence)}</p><p>${escapeHtml(displayed)}</p><button class="cs-btn" data-panel-tf="true" data-correct="${correct}">صح</button><button class="cs-btn" data-panel-tf="false" data-correct="${correct}">خطأ</button><div id="csGameFeedback"></div>`;
    }

    function speakChallenge() {
        const item = randomSentence();
        els.panel.hidden = false;
        els.panel.innerHTML = `<h2>Speak Challenge</h2><p class="cs-sentence">${escapeHtml(item.sentence)}</p><button class="cs-action mic" data-panel-mic="${item.id}">ابدأ المايك</button><div id="csGameFeedback"></div>`;
    }

    function dailySentenceReview() {
        const sample = shuffle(commonSentencesData).slice(0, 5);
        els.panel.hidden = false;
        els.panel.innerHTML = `<h2>Daily Sentence Review</h2><div class="cs-reading-list">${sample.map(item => `<div>${escapeHtml(item.sentence)}<br>${escapeHtml(item.arabic)}</div>`).join("")}</div>`;
        awardCommonSentencePoints("review", 1);
    }

    function choosePanelGame(title) {
        const item = randomSentence();
        els.panel.hidden = false;
        els.panel.innerHTML = `<h2>${title}</h2><p class="cs-sentence">${escapeHtml(item.sentence)}</p>${translationOptions(item).replaceAll("data-answer", "data-panel-answer")}<div id="csGameFeedback"></div>`;
    }

    function randomSentence(excludeId = "") {
        const pool = commonSentencesData.filter(item => item.id !== excludeId);
        return pool[Math.floor(Math.random() * pool.length)];
    }

    function exact(value, expected) {
        return normalizeText(value) === normalizeText(expected);
    }

    function feedback(message) {
        const target = document.getElementById("csTrainingFeedback") || document.getElementById("csGameFeedback");
        if (target) target.textContent = message;
    }

    function handleAnswerClick(event) {
        const answer = event.target.closest("[data-answer]");
        if (answer) {
            const success = answer.dataset.answer === answer.dataset.correct;
            answer.classList.add(success ? "correct" : "wrong");
            if (success) awardCommonSentencePoints("exercise", 5, { masteredSentence: answer.dataset.id });
            feedback(success ? "إجابة صحيحة +5" : "حاول مرة أخرى.");
            renderSentenceCards();
            return true;
        }
        const quick = event.target.closest("[data-quick]");
        if (quick) {
            const success = quick.dataset.quick === quick.dataset.correct;
            quick.classList.add(success ? "correct" : "wrong");
            if (success) awardCommonSentencePoints("exercise", 5, { masteredSentence: quick.dataset.id });
            feedback(success ? "ممتاز +5" : "راجع الجملة.");
            renderSentenceCards();
            return true;
        }
        return false;
    }

    function handleModalClick(event) {
        if (handleAnswerClick(event)) return;
        const speak = event.target.closest("[data-modal-speak]");
        if (speak) {
            speakText(speak.dataset.modalSpeak);
            awardCommonSentencePoints("listen", 1);
            return;
        }
        const slow = event.target.closest("[data-modal-slow]");
        if (slow) {
            speakSlow(slow.dataset.modalSlow);
            awardCommonSentencePoints("slow", 1);
            return;
        }
        if (event.target.closest("[data-modal-stop]")) {
            stopSpeaking();
            return;
        }
        const training = event.target.closest("[data-modal-training]");
        if (training) {
            chooseTranslationGame(findSentence(training.dataset.modalTraining));
            return;
        }
        const master = event.target.closest("[data-modal-master]");
        if (master) {
            awardCommonSentencePoints("master", 5, { masteredSentence: master.dataset.modalMaster });
            feedback("تم حفظها كجملة متقنة.");
            renderSentenceCards();
            return;
        }
        const tf = event.target.closest("[data-tf]");
        if (tf) {
            const success = String(tf.dataset.correct) === tf.dataset.tf;
            tf.classList.add(success ? "correct" : "wrong");
            if (success) awardCommonSentencePoints("exercise", 5, { masteredSentence: tf.dataset.id });
            feedback(success ? "صحيح +5" : "حاول مرة أخرى.");
            renderSentenceCards();
            return;
        }
        const blank = event.target.closest("[data-check-blank]");
        if (blank) {
            const item = findSentence(blank.dataset.checkBlank);
            const success = exact(document.getElementById("csTrainingInput").value, item.missing_word);
            if (success) awardCommonSentencePoints("exercise", 5, { masteredSentence: item.id });
            feedback(success ? "ممتاز +5" : `الإجابة: ${item.missing_word}`);
            renderSentenceCards();
            return;
        }
        const order = event.target.closest("[data-check-order]");
        if (order) {
            const item = findSentence(order.dataset.checkOrder);
            const success = similarityScore(item.sentence, document.getElementById("csTrainingInput").value) >= 80;
            if (success) awardCommonSentencePoints("exercise", 5, { masteredSentence: item.id });
            feedback(success ? "ترتيب صحيح +5" : `الصحيح: ${item.sentence}`);
            renderSentenceCards();
            return;
        }
        const micReading = event.target.closest("[data-mic-reading]");
        if (micReading) {
            const item = findSentence(micReading.dataset.micReading.split(",")[0]);
            startMicPractice(item);
        }
    }

    function handlePanelClick(event) {
        const finishReading = event.target.closest("#csFinishReading");
        if (finishReading) {
            finishReadingTest();
            return;
        }
        const showCard = event.target.closest("[data-show-card]");
        if (showCard) {
            const item = findSentence(showCard.dataset.showCard);
            document.getElementById("csGameFeedback").textContent = item.arabic;
            return;
        }
        const panelAnswer = event.target.closest("[data-panel-answer], [data-minute-answer]");
        if (panelAnswer) {
            const value = panelAnswer.dataset.panelAnswer || panelAnswer.dataset.minuteAnswer;
            const success = value === panelAnswer.dataset.correct;
            panelAnswer.classList.add(success ? "correct" : "wrong");
            if (success) {
                minuteScore += panelAnswer.dataset.minuteAnswer ? 1 : 0;
                const scoreNode = document.getElementById("csMinuteScore");
                if (scoreNode) scoreNode.textContent = minuteScore;
                awardCommonSentencePoints(panelAnswer.dataset.minuteAnswer ? "minute_challenge" : "game", panelAnswer.dataset.minuteAnswer ? 10 : 5);
            }
            feedback(success ? "إجابة صحيحة." : "حاول مرة أخرى.");
            return;
        }
        const panelTf = event.target.closest("[data-panel-tf]");
        if (panelTf) {
            const success = String(panelTf.dataset.correct) === panelTf.dataset.panelTf;
            panelTf.classList.add(success ? "correct" : "wrong");
            if (success) awardCommonSentencePoints("game", 5);
            feedback(success ? "صحيح." : "راجع الترجمة.");
            return;
        }
        const panelOrder = event.target.closest("[data-panel-order]");
        if (panelOrder) {
            const item = findSentence(panelOrder.dataset.panelOrder);
            const success = similarityScore(item.sentence, document.getElementById("csPanelInput").value) >= 80;
            if (success) awardCommonSentencePoints("game", 5, { masteredSentence: item.id });
            feedback(success ? "ترتيب صحيح." : `الصحيح: ${item.sentence}`);
            renderSentenceCards();
            return;
        }
        const panelSpeak = event.target.closest("[data-panel-speak]");
        if (panelSpeak) {
            speakText(panelSpeak.dataset.panelSpeak);
            awardCommonSentencePoints("listen", 1);
            return;
        }
        const panelMic = event.target.closest("[data-panel-mic]");
        if (panelMic) startMicPractice(findSentence(panelMic.dataset.panelMic));
    }

    function startPractice(kind) {
        const item = randomSentence();
        if (kind === "trueFalse") trueFalseGame(item);
        if (kind === "choose") chooseTranslationGame(item);
        if (kind === "blank") fillBlankGame(item);
        if (kind === "order") sentenceOrderGame(item);
        if (kind === "listen") listenAndChooseGame(item);
        if (kind === "speak") startMicPractice(item);
        if (kind === "meaning") quickMeaningGame(item);
    }

    function startGame(kind) {
        if (kind === "flashcards") sentenceFlashcards();
        if (kind === "match") translationMatch();
        if (kind === "builder") sentenceBuilder();
        if (kind === "listenRace") listenRace();
        if (kind === "tfRace") trueFalseRace();
        if (kind === "speakChallenge") speakChallenge();
        if (kind === "review") dailySentenceReview();
    }

    function handleCardAction(action, item) {
        if (action === "open") openSentenceModal(item);
        if (action === "listen") {
            speakText(item.sentence);
            awardCommonSentencePoints("listen", 1);
        }
        if (action === "slow") {
            speakSlow(item.sentence);
            awardCommonSentencePoints("slow", 1);
        }
        if (action === "training") chooseTranslationGame(item);
        if (action === "mic") startMicPractice(item);
        if (action === "review") {
            if (!progress.review.includes(item.id)) progress.review.push(item.id);
            saveCommonSentenceProgress();
            updateCommonSentenceStats();
        }
    }

    function bindEvents() {
        document.getElementById("csThemeToggle").addEventListener("click", () => {
            applyTheme(document.body.dataset.theme === "dark" ? "light" : "dark");
        });
        els.search.addEventListener("input", searchSentences);
        els.category.addEventListener("change", () => {
            activeCategory = "";
            renderSentenceCards();
        });
        els.level.addEventListener("change", renderSentenceCards);
        document.querySelectorAll("[data-filter-category]").forEach(button => {
            button.addEventListener("click", () => {
                activeCategory = button.dataset.filterCategory;
                els.category.value = activeCategory;
                renderSentenceCards();
            });
        });
        document.querySelectorAll("[data-filter-level]").forEach(button => {
            button.addEventListener("click", () => {
                els.level.value = button.dataset.filterLevel;
                renderSentenceCards();
            });
        });
        document.querySelectorAll("[data-practice]").forEach(button => {
            button.addEventListener("click", () => startPractice(button.dataset.practice));
        });
        document.querySelectorAll("[data-game]").forEach(button => {
            button.addEventListener("click", () => startGame(button.dataset.game));
        });
        document.getElementById("csReadingStart").addEventListener("click", readingSpeedTest);
        document.getElementById("csMicReadingStart").addEventListener("click", micReadingTest);
        document.getElementById("csMinuteChallenge").addEventListener("click", minuteChallenge);
        document.getElementById("csCompleteSection").addEventListener("click", () => awardCommonSentencePoints("complete", 50, { completed: true }));
        els.grid.addEventListener("click", event => {
            const button = event.target.closest("[data-action]");
            if (!button) return;
            handleCardAction(button.dataset.action, findSentence(button.dataset.id));
        });
        els.modal.addEventListener("click", event => {
            if (event.target === els.modal) closeModal();
            handleModalClick(event);
        });
        els.panel.addEventListener("click", handlePanelClick);
        document.getElementById("csModalClose").addEventListener("click", closeModal);
    }

    document.addEventListener("DOMContentLoaded", () => {
        applyTheme(preferredTheme());
        els.grid = document.getElementById("csGrid");
        els.empty = document.getElementById("csEmpty");
        els.search = document.getElementById("csSearch");
        els.category = document.getElementById("csCategory");
        els.level = document.getElementById("csLevel");
        els.points = document.getElementById("csPoints");
        els.actions = document.getElementById("csActions");
        els.status = document.getElementById("csStatus");
        els.mastered = document.getElementById("csMastered");
        els.progressFill = document.getElementById("csProgressFill");
        els.modal = document.getElementById("csModal");
        els.modalContent = document.getElementById("csModalContent");
        els.panel = document.getElementById("csPanel");
        renderCategoryOptions();
        updateCommonSentenceStats();
        renderSentenceCards();
        bindEvents();
    });
})();
