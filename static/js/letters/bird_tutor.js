(function (window, document) {
    "use strict";

    const STATES = ["idle", "talking", "happy", "wrong", "thinking"];
    const STATE_FILES = {
        idle: "/static/animations/bird/bird_idle.json",
        talking: "/static/animations/bird/bird_talk.json",
        happy: "/static/animations/bird/bird_happy.json",
        wrong: "/static/animations/bird/bird_wrong.json",
        thinking: "/static/animations/bird/bird_thinking.json"
    };
    const FALLBACK_EMOJI = "\uD83E\uDD9C";
    const REVIEW_STORAGE_KEY = "birdTutorReviewItems";
    const XP_STORAGE_KEY = "birdTutorXp";
    const QUESTION_TYPES = [
        "starts_with_letter",
        "choose_word_for_letter",
        "listen_and_choose",
        "find_missing_letter"
    ];
    const BIRD_MESSAGES = {
        opening: [
            "هيا يا بطل، اضغط اسألني لنتمرن معًا.",
            "أنا جاهز أساعدك خطوة بخطوة.",
            "لنراجع الحروف والكلمات بطريقة ممتعة."
        ],
        encouragement: [
            "ممتاز يا بطل!",
            "رائع! تفكيرك يتحسن.",
            "أحسنت، هذه إجابة ذكية."
        ],
        gentleWrong: [
            "قريب جدًا، ركز على أول صوت في الكلمة.",
            "محاولة جميلة، لنفكر بهدوء.",
            "لا بأس، التلميح سيساعدك."
        ],
        review: [
            "لنراجع كلمة أخطأت فيها سابقًا.",
            "وقت المراجعة القصيرة.",
            "هيا نثبت الكلمة في الذاكرة."
        ],
        celebration: [
            "أحسنت! أنت تتحسن.",
            "نجمة جديدة لك!",
            "رائع، المراجعة صنعت فرقًا."
        ]
    };

    function shuffle(items) {
        return items
            .map(item => ({ item, sort: Math.random() }))
            .sort((a, b) => a.sort - b.sort)
            .map(entry => entry.item);
    }

    function uniqueWords(words) {
        const seen = new Set();
        return words.filter(word => {
            const key = String(word || "").trim().toLowerCase();
            if (!key || seen.has(key)) return false;
            seen.add(key);
            return true;
        });
    }

    function pick(items, fallback = "") {
        if (!Array.isArray(items) || items.length === 0) {
            return fallback;
        }
        return items[Math.floor(Math.random() * items.length)];
    }

    function cleanWord(value) {
        return String(value || "").trim().toLowerCase();
    }

    function normalizeAnswer(value) {
        return String(value || "").trim().toLowerCase();
    }

    function getLetters() {
        return window.LETTERS || "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");
    }

    function getCookie(name) {
        const cookieValue = `; ${document.cookie || ""}`;
        const parts = cookieValue.split(`; ${name}=`);
        if (parts.length === 2) {
            return parts.pop().split(";").shift();
        }
        return "";
    }

    function isAuthenticatedForBirdTutor() {
        return Boolean(window.PHONICS_USER_ID || window.phonicsUserId || window.currentUserId);
    }

    function postBirdTutorJson(url, payload) {
        if (!isAuthenticatedForBirdTutor()) {
            return Promise.reject(new Error("bird_tutor_not_authenticated"));
        }

        return fetch(url, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify(payload)
        }).then(response => {
            if (!response.ok) {
                throw new Error(`bird_tutor_request_failed_${response.status}`);
            }
            return response.json();
        });
    }

    function getBirdTutorJson(url) {
        if (!isAuthenticatedForBirdTutor()) {
            return Promise.reject(new Error("bird_tutor_not_authenticated"));
        }

        return fetch(url, {
            method: "GET",
            credentials: "same-origin",
            headers: {
                "Accept": "application/json"
            }
        }).then(response => {
            if (!response.ok) {
                throw new Error(`bird_tutor_request_failed_${response.status}`);
            }
            return response.json();
        });
    }

    function installBirdTutor(AppClass) {
        if (!AppClass || !AppClass.prototype || AppClass.prototype.__birdTutorInstalled) {
            return;
        }

        AppClass.prototype.__birdTutorInstalled = true;

        const originalInit = AppClass.prototype.init;
        AppClass.prototype.init = function () {
            originalInit.call(this);
            this.initBirdTutor();
        };

        AppClass.prototype.initBirdTutor = function () {
            this.birdTutor = document.getElementById("birdTutor");
            this.birdLottieEl = document.getElementById("birdLottie");
            this.birdFallbackEl = document.getElementById("birdFallback");
            this.birdBubbleEl = document.getElementById("birdBubble");
            this.birdActionsEl = document.getElementById("birdActions");
            this.birdAskBtn = document.getElementById("birdAskBtn");
            this.birdRepeatBtn = document.getElementById("birdRepeatBtn");
            this.birdReviewBtn = document.getElementById("birdReviewBtn");
            this.birdStatsEl = document.getElementById("birdStats");
            this.birdHintEl = document.getElementById("birdHint");

            if (!this.birdTutor || !this.birdBubbleEl || !this.birdActionsEl) {
                return;
            }

            this.birdAnimation = null;
            this.birdAnimationCache = {};
            this.birdCurrentState = "";
            this.birdTypingTimer = null;
            this.birdLastQuestion = null;
            this.birdWrongAttempts = 0;
            this.birdLottieStatus = "fallback";
            this.birdQuestionCounter = 0;
            this.birdXp = this.loadBirdXp();
            this.birdReviewItems = this.loadBirdReviewItems();

            if (this.birdAskBtn && !this.birdAskBtn.dataset.bound) {
                this.birdAskBtn.addEventListener("click", () => {
                    const question = this.buildQuestionForCurrentLetter();
                    this.renderQuestion(question);
                });
                this.birdAskBtn.dataset.bound = "true";
            }

            if (this.birdRepeatBtn && !this.birdRepeatBtn.dataset.bound) {
                this.birdRepeatBtn.addEventListener("click", () => this.repeatQuestion());
                this.birdRepeatBtn.dataset.bound = "true";
            }

            this.typeMessage("هيا يا بطل، اضغط اسألني لنبدأ!");
            if (this.birdReviewBtn && !this.birdReviewBtn.dataset.bound) {
                this.birdReviewBtn.addEventListener("click", () => this.startBirdReview());
                this.birdReviewBtn.dataset.bound = "true";
            }

            this.typeMessage(pick(BIRD_MESSAGES.opening));
            this.setBirdState("idle");
            this.updateBirdStats();

            window.addEventListener("load", () => {
                if (this.birdLottieStatus !== "lottie") {
                    this.setBirdState(this.birdCurrentState || "idle");
                }
            }, { once: true });
        };

        AppClass.prototype.setBirdState = function (state) {
            const nextState = STATES.includes(state) ? state : "idle";
            this.birdCurrentState = nextState;

            if (!this.birdTutor || !this.birdLottieEl || !this.birdFallbackEl) {
                return;
            }

            this.birdTutor.dataset.state = nextState;
            this.birdFallbackEl.textContent = FALLBACK_EMOJI;

            if (!window.lottie || typeof window.lottie.loadAnimation !== "function") {
                this.showBirdFallback("lottie-web unavailable");
                return;
            }

            const availableFiles = window.BIRD_LOTTIE_FILES || {};
            const path = availableFiles[nextState] || "";
            if (!path) {
                this.showBirdFallback("missing state path");
                return;
            }

            this.loadBirdAnimation(path)
                .then(animationData => {
                    if (this.birdCurrentState !== nextState) {
                        return;
                    }

                    if (!animationData || !window.lottie) {
                        this.showBirdFallback("missing animation data");
                        return;
                    }

                    if (this.birdAnimation) {
                        this.birdAnimation.destroy();
                        this.birdAnimation = null;
                    }

                    this.birdLottieEl.replaceChildren();
                    this.birdAnimation = window.lottie.loadAnimation({
                        container: this.birdLottieEl,
                        renderer: "svg",
                        loop: true,
                        autoplay: true,
                        animationData
                    });
                    this.birdLottieEl.hidden = false;
                    this.birdFallbackEl.hidden = true;
                    this.birdLottieStatus = "lottie";
                    this.birdTutor.dataset.lottieStatus = "lottie";
                })
                .catch(() => {
                    this.showBirdFallback("animation unavailable");
                });
        };

        AppClass.prototype.loadBirdAnimation = function (path) {
            if (this.birdAnimationCache[path]) {
                return this.birdAnimationCache[path];
            }

            this.birdAnimationCache[path] = fetch(path, { cache: "force-cache" })
                .then(response => {
                    if (!response.ok) {
                        throw new Error("missing_lottie_file");
                    }
                    return response.json();
                })
                .catch(error => {
                    delete this.birdAnimationCache[path];
                    throw error;
                });

            return this.birdAnimationCache[path];
        };

        AppClass.prototype.showBirdFallback = function (reason) {
            if (this.birdAnimation) {
                this.birdAnimation.destroy();
                this.birdAnimation = null;
            }

            if (this.birdLottieEl) {
                this.birdLottieEl.replaceChildren();
                this.birdLottieEl.hidden = true;
            }

            if (this.birdFallbackEl) {
                this.birdFallbackEl.hidden = false;
                this.birdFallbackEl.textContent = FALLBACK_EMOJI;
            }

            if (this.birdTutor) {
                this.birdTutor.dataset.lottieStatus = "fallback";
                this.birdTutor.dataset.lottieReason = reason || "fallback";
            }

            this.birdLottieStatus = "fallback";
        };

        AppClass.prototype.typeMessage = function (text) {
            const message = String(text || "");
            if (!this.birdBubbleEl) {
                return;
            }

            if (this.birdTypingTimer) {
                clearInterval(this.birdTypingTimer);
                this.birdTypingTimer = null;
            }

            this.birdBubbleEl.textContent = "";
            let index = 0;
            this.birdTypingTimer = setInterval(() => {
                this.birdBubbleEl.textContent = message.slice(0, index + 1);
                index += 1;
                if (index >= message.length) {
                    clearInterval(this.birdTypingTimer);
                    this.birdTypingTimer = null;
                }
            }, 28);
        };

        AppClass.prototype.speakText = function (text) {
            const message = String(text || "").trim();
            if (!message || !("speechSynthesis" in window) || !window.SpeechSynthesisUtterance) {
                return;
            }

            try {
                window.speechSynthesis.cancel();
                const utterance = new window.SpeechSynthesisUtterance(message);
                utterance.lang = "en-GB";
                utterance.rate = 0.9;
                utterance.onstart = () => this.setBirdState("talking");
                utterance.onend = () => this.setBirdState("idle");
                utterance.onerror = () => this.setBirdState("idle");
                window.speechSynthesis.speak(utterance);
            } catch (error) {
                this.setBirdState("idle");
            }
        };

        AppClass.prototype.buildQuestionForCurrentLetter = function () {
            this.setBirdState("thinking");

            const letters = window.LETTERS || "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");
            const letter = letters[this.currentLetterIndex] || this.progress?.currentLetter || "A";
            const letterData = window.LETTER_DATA?.[letter] || { words: [] };
            const letterWords = uniqueWords((letterData.words || []).map(item => item.word));
            const correct = shuffle(letterWords)[0] || letter.toLowerCase();

            const distractors = [];
            letters.forEach(otherLetter => {
                if (otherLetter === letter) return;
                const words = window.LETTER_DATA?.[otherLetter]?.words || [];
                words.forEach(item => {
                    const word = String(item.word || "").trim().toLowerCase();
                    if (word && word !== correct) {
                        distractors.push(word);
                    }
                });
            });

            const choices = uniqueWords([correct, ...shuffle(distractors)]).slice(0, 4);
            if (!choices.includes(correct)) {
                choices[0] = correct;
            }

            return {
                letter,
                prompt: `What word starts with ${letter}?`,
                correct,
                choices: shuffle(choices)
            };
        };

        AppClass.prototype.renderQuestion = function (question) {
            if (!question || !this.birdActionsEl) {
                return;
            }

            this.birdLastQuestion = question;
            this.birdWrongAttempts = 0;
            this.birdActionsEl.replaceChildren();
            this.typeMessage(question.prompt);
            this.speakText(question.prompt);

            question.choices.forEach(choice => {
                const button = document.createElement("button");
                button.type = "button";
                button.className = "bird-choice-btn";
                button.textContent = choice;
                button.addEventListener("click", () => this.handleAnswer(choice));
                this.birdActionsEl.appendChild(button);
            });
        };

        AppClass.prototype.handleAnswer = function (choice) {
            if (!this.birdLastQuestion) {
                return;
            }

            const selected = String(choice || "").trim().toLowerCase();
            const correct = String(this.birdLastQuestion.correct || "").trim().toLowerCase();

            if (selected === correct) {
                this.setBirdState("happy");
                this.birdActionsEl.replaceChildren();
                this.typeMessage("ممتاز يا بطل! \u2B50");
                this.speakText("Excellent!");
                return;
            }

            this.birdWrongAttempts += 1;
            this.setBirdState("wrong");

            if (this.birdWrongAttempts >= 2) {
                this.birdActionsEl.replaceChildren();
                this.typeMessage(`الإجابة الصحيحة هي ${correct}. سنراجعها لاحقًا.`);
                this.speakText(correct);
                return;
            }

            this.typeMessage("قريب جدًا، جرّب مرة ثانية");
            this.speakText("Try again.");
        };

        AppClass.prototype.repeatQuestion = function () {
            if (this.birdLastQuestion) {
                this.typeMessage(this.birdLastQuestion.prompt);
                this.speakText(this.birdLastQuestion.prompt);
                return;
            }

            this.typeMessage("اضغط اسألني أولًا لنبدأ!");
        };
        AppClass.prototype.loadBirdXp = function () {
            try {
                return Math.max(0, Number(localStorage.getItem(XP_STORAGE_KEY) || 0));
            } catch (error) {
                return 0;
            }
        };

        AppClass.prototype.saveBirdXp = function () {
            try {
                localStorage.setItem(XP_STORAGE_KEY, String(this.birdXp || 0));
            } catch (error) {
                // Local progress only; ignore storage failures.
            }
        };

        AppClass.prototype.loadBirdReviewItems = function () {
            try {
                const parsed = JSON.parse(localStorage.getItem(REVIEW_STORAGE_KEY) || "[]");
                return Array.isArray(parsed) ? parsed.filter(item => item && item.word && item.letter) : [];
            } catch (error) {
                return [];
            }
        };

        AppClass.prototype.saveBirdReviewItems = function () {
            try {
                localStorage.setItem(REVIEW_STORAGE_KEY, JSON.stringify(this.birdReviewItems || []));
            } catch (error) {
                // Local review only; ignore storage failures.
            }
        };

        AppClass.prototype.getActiveBirdReviewItems = function () {
            return (this.birdReviewItems || []).filter(item => !item.mastered);
        };

        AppClass.prototype.updateBirdStats = function () {
            const reviewCount = this.getActiveBirdReviewItems().length;

            if (this.birdStatsEl) {
                this.birdStatsEl.replaceChildren();

                const xpBadge = document.createElement("span");
                xpBadge.className = "bird-stat-badge";
                xpBadge.textContent = `⭐ Bird XP: ${this.birdXp || 0}`;

                const reviewBadge = document.createElement("span");
                reviewBadge.className = "bird-stat-badge bird-stat-review";
                reviewBadge.textContent = `مراجعة: ${reviewCount}`;

                this.birdStatsEl.append(xpBadge, reviewBadge);
            }

            if (this.birdReviewBtn) {
                this.birdReviewBtn.hidden = reviewCount === 0;
                this.birdReviewBtn.disabled = reviewCount === 0;
            }
        };

        AppClass.prototype.setBirdHint = function (text, tone = "info") {
            if (!this.birdHintEl) {
                return;
            }

            const message = String(text || "").trim();
            this.birdHintEl.textContent = message;
            this.birdHintEl.hidden = !message;
            this.birdHintEl.dataset.tone = tone;
        };

        AppClass.prototype.addBirdXp = function (amount) {
            this.birdXp = Math.max(0, (this.birdXp || 0) + Number(amount || 0));
            this.saveBirdXp();
            this.updateBirdStats();
        };

        AppClass.prototype.applyServerProgress = function (progress) {
            if (!progress || typeof progress.xp !== "number") {
                return;
            }

            this.birdXp = Math.max(0, progress.xp);
            this.saveBirdXp();
            this.updateBirdStats();
        };

        AppClass.prototype.syncBirdProgress = function (question, isCorrect, xpDelta) {
            return postBirdTutorJson("/api/bird-tutor/progress/", {
                xp_delta: Math.max(0, Number(xpDelta || 0)),
                question_type: question?.type || "",
                is_correct: Boolean(isCorrect),
                letter: question?.letter || "",
                word: question?.targetWord || question?.correct || ""
            }).then(data => {
                this.applyServerProgress(data.progress);
                return data;
            });
        };

        AppClass.prototype.syncBirdReviewItem = function (question, isCorrect) {
            return postBirdTutorJson("/api/bird-tutor/review/", {
                letter: question?.letter || "",
                word: question?.targetWord || question?.correct || "",
                question_type: question?.type || "",
                is_correct: Boolean(isCorrect)
            });
        };

        AppClass.prototype.mapServerReviewItem = function (item) {
            return {
                id: item.id ? `server:${item.id}` : `${item.letter}:${item.word}`,
                serverId: item.id || null,
                letter: item.letter,
                word: item.word,
                lastType: item.question_type || "starts_with_letter",
                misses: item.mistakes_count || 0,
                successes: item.success_count || 0,
                mastered: Boolean(item.mastered),
                source: "server"
            };
        };

        AppClass.prototype.fetchBirdReviewItems = function () {
            return getBirdTutorJson("/api/bird-tutor/review/")
                .then(data => {
                    if (!Array.isArray(data.items)) {
                        return this.getActiveBirdReviewItems();
                    }

                    this.birdReviewItems = data.items.map(item => this.mapServerReviewItem(item));
                    this.saveBirdReviewItems();
                    this.updateBirdStats();
                    return this.getActiveBirdReviewItems();
                })
                .catch(() => this.getActiveBirdReviewItems());
        };

        AppClass.prototype.getWordRecordsForLetter = function (letter) {
            const data = window.LETTER_DATA?.[letter] || { words: [] };
            return (data.words || [])
                .map(item => ({
                    word: cleanWord(item.word),
                    translation: String(item.translation || "").trim(),
                    emoji: String(item.emoji || "").trim()
                }))
                .filter(item => item.word);
        };

        AppClass.prototype.getDistractorWords = function (letter, correctWord, limit = 3) {
            const distractors = [];
            getLetters().forEach(otherLetter => {
                if (otherLetter === letter) return;
                this.getWordRecordsForLetter(otherLetter).forEach(item => {
                    if (item.word !== correctWord) {
                        distractors.push(item.word);
                    }
                });
            });

            return uniqueWords(shuffle(distractors)).slice(0, limit);
        };

        AppClass.prototype.makeWordChoices = function (letter, correctWord) {
            const choices = uniqueWords([
                correctWord,
                ...this.getDistractorWords(letter, correctWord, 6)
            ]).slice(0, 4);

            if (!choices.includes(correctWord)) {
                choices[0] = correctWord;
            }

            return shuffle(choices);
        };

        AppClass.prototype.makeLetterChoices = function (letter) {
            const otherLetters = getLetters().filter(item => item !== letter);
            return shuffle(uniqueWords([letter, ...shuffle(otherLetters).slice(0, 3)])).map(item => item.toUpperCase());
        };

        AppClass.prototype.buildQuestionForCurrentLetter = function () {
            this.setBirdState("thinking");
            this.setBirdHint("");

            const letters = getLetters();
            const letter = letters[this.currentLetterIndex] || this.progress?.currentLetter || "A";
            const records = this.getWordRecordsForLetter(letter);
            const record = pick(records, { word: letter.toLowerCase(), translation: "", emoji: "" });
            const type = QUESTION_TYPES[this.birdQuestionCounter % QUESTION_TYPES.length];
            this.birdQuestionCounter += 1;

            return this.createBirdQuestion({ type, letter, record, isReview: false });
        };

        AppClass.prototype.createBirdQuestion = function ({ type, letter, record, isReview = false, reviewId = "" }) {
            const word = cleanWord(record?.word) || cleanWord(letter);
            const upperLetter = String(letter || "").toUpperCase();
            const displayWord = `${record?.emoji ? `${record.emoji} ` : ""}${word}`;
            const base = {
                type,
                letter: upperLetter,
                targetWord: word,
                isReview,
                reviewId,
                correctExplanation: `ممتاز يا بطل! ${word} تبدأ بحرف ${upperLetter} وصوت /${upperLetter.toLowerCase()}/.`,
                wrongHint: `استمع إلى بداية الكلمة. نحن نبحث عن كلمة تبدأ بحرف ${upperLetter}.`,
                finalExplanation: `الإجابة الصحيحة هي ${word} لأنها تبدأ بحرف ${upperLetter}.`,
                speakPrompt: `Listen carefully. ${word}.`
            };

            if (type === "listen_and_choose") {
                return {
                    ...base,
                    prompt: "استمع جيدًا، أي كلمة سمعت؟",
                    correct: word,
                    choices: this.makeWordChoices(upperLetter, word),
                    wrongHint: "استمع للكلمة مرة أخرى، ثم اختر نفس الكلمة من الأزرار.",
                    correctExplanation: `رائع! سمعت كلمة ${word} واخترتها بشكل صحيح.`,
                    finalExplanation: `الكلمة التي سمعتها هي ${word}. سنراجعها مرة أخرى لاحقًا.`
                };
            }

            if (type === "find_missing_letter") {
                const missingWord = word.length > 1 ? `_${word.slice(1)}` : "_";
                return {
                    ...base,
                    prompt: `ما الحرف الناقص في ${missingWord}؟`,
                    correct: upperLetter,
                    choices: this.makeLetterChoices(upperLetter),
                    wrongHint: `انظر إلى الكلمة ${word}. ما أول حرف تسمعه؟`,
                    correctExplanation: `صحيح! ${word} تبدأ بحرف ${upperLetter}، لذلك الحرف الناقص هو ${upperLetter}.`,
                    finalExplanation: `الإجابة الصحيحة هي ${upperLetter} لأن ${word} تبدأ بهذا الحرف.`,
                    speakPrompt: `What is the missing first letter in ${word}?`
                };
            }

            if (type === "choose_word_for_letter") {
                return {
                    ...base,
                    prompt: `اختر الكلمة التي تناسب حرف ${upperLetter}.`,
                    correct: word,
                    choices: this.makeWordChoices(upperLetter, word),
                    wrongHint: `ابحث عن الكلمة التي يبدأ صوتها الأول بحرف ${upperLetter}.`,
                    correctExplanation: `أحسنت! ${displayWord} هي كلمة مناسبة لحرف ${upperLetter}.`,
                    speakPrompt: `Choose the word for letter ${upperLetter}.`
                };
            }

            return {
                ...base,
                prompt: `أي كلمة تبدأ بحرف ${upperLetter}؟`,
                correct: word,
                choices: this.makeWordChoices(upperLetter, word),
                speakPrompt: `What word starts with ${upperLetter}?`
            };
        };

        AppClass.prototype.renderQuestion = function (question) {
            if (!question || !this.birdActionsEl) {
                return;
            }

            this.birdLastQuestion = question;
            this.birdWrongAttempts = 0;
            this.birdActionsEl.replaceChildren();
            this.setBirdHint("");
            this.typeMessage(question.prompt);
            this.speakText(question.speakPrompt || question.prompt);

            (question.choices || []).forEach(choice => {
                const button = document.createElement("button");
                button.type = "button";
                button.className = "bird-choice-btn";
                button.textContent = choice;
                button.addEventListener("click", () => this.handleAnswer(choice));
                this.birdActionsEl.appendChild(button);
            });
        };

        AppClass.prototype.handleAnswer = function (choice) {
            if (!this.birdLastQuestion) {
                return;
            }

            const question = this.birdLastQuestion;
            const selected = normalizeAnswer(choice);
            const correct = normalizeAnswer(question.correct);

            if (selected === correct) {
                this.handleCorrectBirdAnswer(question);
                return;
            }

            this.handleWrongBirdAnswer(question);
        };

        AppClass.prototype.handleCorrectBirdAnswer = function (question) {
            const xpDelta = question.isReview ? 8 : 5;
            this.setBirdState("happy");
            this.birdActionsEl.replaceChildren();
            this.typeMessage(`${pick(BIRD_MESSAGES.encouragement)} ${question.correctExplanation}`);
            this.setBirdHint(question.correctExplanation, "success");
            this.speakText(question.correctExplanation);
            this.addBirdXp(xpDelta);
            this.syncBirdProgress(question, true, xpDelta).catch(() => {
                // Local XP is already saved as fallback.
            });

            if (question.isReview) {
                this.markReviewSuccess(question.reviewId);
            }
        };

        AppClass.prototype.handleWrongBirdAnswer = function (question) {
            this.birdWrongAttempts += 1;
            this.setBirdState("wrong");

            if (this.birdWrongAttempts >= 2) {
                this.birdActionsEl.replaceChildren();
                this.typeMessage(question.finalExplanation);
                this.setBirdHint(question.finalExplanation, "review");
                this.speakText(question.targetWord || question.correct);
                this.addBirdReviewItem(question);
                this.syncBirdProgress(question, false, 0).catch(() => {
                    // Local review remains available as fallback.
                });
                this.syncBirdReviewItem(question, false).catch(() => {
                    // addBirdReviewItem already persisted local fallback.
                });
                return;
            }

            const hint = `${pick(BIRD_MESSAGES.gentleWrong)} ${question.wrongHint}`;
            this.typeMessage(hint);
            this.setBirdHint(question.wrongHint, "hint");
            this.speakText("Try again.");
        };

        AppClass.prototype.addBirdReviewItem = function (question) {
            if (!question || !question.targetWord || question.isReview) {
                return;
            }

            const id = `${question.letter}:${question.targetWord}`;
            const existing = (this.birdReviewItems || []).find(item => item.id === id);

            if (existing) {
                existing.mastered = false;
                existing.misses = (existing.misses || 0) + 1;
                existing.lastType = question.type;
            } else {
                this.birdReviewItems.push({
                    id,
                    letter: question.letter,
                    word: question.targetWord,
                    lastType: question.type,
                    misses: 1,
                    successes: 0,
                    mastered: false
                });
            }

            this.saveBirdReviewItems();
            this.updateBirdStats();
        };

        AppClass.prototype.startBirdReview = function () {
            this.fetchBirdReviewItems().then(reviewItems => {
            if (reviewItems.length === 0) {
                this.typeMessage("لا توجد كلمات للمراجعة الآن. اسألني سؤالًا جديدًا.");
                this.setBirdHint("", "info");
                this.updateBirdStats();
                return;
            }

            const item = pick(reviewItems);
            const question = this.createBirdQuestion({
                type: "starts_with_letter",
                letter: item.letter,
                record: { word: item.word },
                isReview: true,
                reviewId: item.id
            });

            question.prompt = `${pick(BIRD_MESSAGES.review)} أي كلمة تبدأ بحرف ${item.letter}؟`;
            question.correctExplanation = `أحسنت! أنت تتحسن. ${item.word} تبدأ بحرف ${item.letter}.`;
            question.finalExplanation = `لا بأس. الكلمة هي ${item.word} لأنها تبدأ بحرف ${item.letter}. سنحاول مرة أخرى.`;
            this.renderQuestion(question);
            });
        };

        AppClass.prototype.markReviewSuccess = function (reviewId) {
            const item = (this.birdReviewItems || []).find(entry => entry.id === reviewId);
            if (!item) {
                return;
            }

            item.successes = (item.successes || 0) + 1;
            if (item.successes >= 2) {
                item.mastered = true;
                this.typeMessage(`${pick(BIRD_MESSAGES.celebration)} تم إتقان ${item.word}.`);
            }

            this.saveBirdReviewItems();
            this.updateBirdStats();
            this.syncBirdReviewItem({
                letter: item.letter,
                targetWord: item.word,
                correct: item.word,
                type: item.lastType || "starts_with_letter"
            }, true).then(data => {
                if (data && data.item) {
                    const serverItem = this.mapServerReviewItem(data.item);
                    Object.assign(item, serverItem);
                    this.saveBirdReviewItems();
                    this.updateBirdStats();
                }
            }).catch(() => {
                // Local success/mastered state remains as fallback.
            });
        };

        AppClass.prototype.repeatQuestion = function () {
            if (this.birdLastQuestion) {
                this.typeMessage(this.birdLastQuestion.prompt);
                this.speakText(this.birdLastQuestion.speakPrompt || this.birdLastQuestion.prompt);
                return;
            }

            this.typeMessage("اضغط اسألني أولًا لنبدأ!");
        };
    }

    window.installBirdTutor = installBirdTutor;
})(window, document);
