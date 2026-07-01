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
            this.setBirdState("idle");

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
    }

    window.installBirdTutor = installBirdTutor;
})(window, document);
