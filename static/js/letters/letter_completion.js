(function (window) {
    "use strict";

    function bindActivation(element, handler) {
        if (!element || typeof handler !== "function") return;

        let lastTouchAt = 0;

        element.addEventListener("touchend", (event) => {
            if (event.cancelable) event.preventDefault();
            lastTouchAt = Date.now();
            handler(event);
        }, { passive: false });

        element.addEventListener("click", (event) => {
            if (Date.now() - lastTouchAt < 500) return;
            handler(event);
        });
    }

    function getLetterWords(letter) {
        const data = window.LETTER_DATA && window.LETTER_DATA[letter];
        const words = Array.isArray(data && data.words) ? data.words : [];
        return words.map((item) => {
            if (typeof item === "string") return item;
            return item && item.word ? item.word : "";
        }).filter(Boolean);
    }

    window.installLetterCompletionScreen = function installLetterCompletionScreen(PhonicsGameLab) {
        if (!PhonicsGameLab || !PhonicsGameLab.prototype) return;

        PhonicsGameLab.prototype.initLetterCompletionScreen = function initLetterCompletionScreen() {
            this.letterCompletionModal = document.getElementById("letterCompletionModal");
            this.completionLetterEl = document.getElementById("completionLetter");
            this.completionScoreEl = document.getElementById("completionScore");
            this.completionWordsEl = document.getElementById("completionWords");
            this.completionBirdMessageEl = document.getElementById("completionBirdMessage");
            this.completionNextLetterBtn = document.getElementById("completionNextLetter");
            this.completionOptionalGamesBtn = document.getElementById("completionOptionalGames");
            this.completionParentReportBtn = document.getElementById("completionParentReport");
            this.completionDismissBtn = document.getElementById("completionDismiss");
            this.letterCompletionCloseBtn = document.getElementById("letterCompletionClose");
            this.letterCompletionState = null;

            if (!this.letterCompletionModal) return;

            if (this.completionParentReportBtn && window.LEVEL_ONE_DISABLED_FEATURES?.parentReport) {
                this.completionParentReportBtn.hidden = true;
                this.completionParentReportBtn.setAttribute("aria-hidden", "true");
                this.completionParentReportBtn.tabIndex = -1;
            }

            bindActivation(this.completionNextLetterBtn, () => this.goToCompletionNextLetter());
            bindActivation(this.completionOptionalGamesBtn, () => this.openCompletionOptionalGames());
            bindActivation(this.completionParentReportBtn, () => this.openCompletionParentReport());
            bindActivation(this.completionDismissBtn, () => this.hideLetterCompletion());
            bindActivation(this.letterCompletionCloseBtn, () => this.hideLetterCompletion());

            this.letterCompletionModal.addEventListener("click", (event) => {
                if (event.target === this.letterCompletionModal) {
                    this.hideLetterCompletion();
                }
            });

            document.addEventListener("keydown", (event) => {
                if (event.key === "Escape" && this.isLetterCompletionOpen()) {
                    this.hideLetterCompletion();
                }
            });
        };

        PhonicsGameLab.prototype.showLetterCompletion = function showLetterCompletion(letter, entry) {
            if (!this.letterCompletionModal) {
                if (typeof this.showParentReport === "function") {
                    this.showParentReport(letter, entry);
                }
                return;
            }

            const safeLetter = String(letter || "").toUpperCase();
            const score = entry && typeof entry.score === "number" ? entry.score : this.getCurrentLetterTotalScore();
            const words = getLetterWords(safeLetter);

            this.letterCompletionState = {
                letter: safeLetter,
                entry: entry || null,
                nextIndex: this.currentLetterIndex + 1
            };

            if (this.completionLetterEl) this.completionLetterEl.textContent = safeLetter;
            if (this.completionScoreEl) this.completionScoreEl.textContent = String(score);
            if (this.completionBirdMessageEl) {
                this.completionBirdMessageEl.textContent = "🦜 رائع! أنت جاهز للحرف التالي.";
            }

            if (this.completionBirdMessageEl) {
                this.completionBirdMessageEl.textContent = "رائع! أنت جاهز للحرف التالي.";
            }

            if (this.completionWordsEl) {
                this.completionWordsEl.replaceChildren();
                words.forEach((word) => {
                    const chip = document.createElement("span");
                    chip.className = "letter-completion-word";
                    chip.textContent = word;
                    this.completionWordsEl.appendChild(chip);
                });
            }

            this.letterCompletionModal.style.display = "flex";
            this.letterCompletionModal.classList.add("is-open");

            window.setTimeout(() => {
                if (this.completionNextLetterBtn) {
                    this.completionNextLetterBtn.focus({ preventScroll: true });
                }
            }, 80);
        };

        PhonicsGameLab.prototype.hideLetterCompletion = function hideLetterCompletion() {
            if (!this.letterCompletionModal) return;
            this.letterCompletionModal.classList.remove("is-open");
            this.letterCompletionModal.style.display = "none";
        };

        PhonicsGameLab.prototype.isLetterCompletionOpen = function isLetterCompletionOpen() {
            return !!(
                this.letterCompletionModal &&
                this.letterCompletionModal.style.display !== "none" &&
                this.letterCompletionModal.classList.contains("is-open")
            );
        };

        PhonicsGameLab.prototype.goToCompletionNextLetter = function goToCompletionNextLetter() {
            const state = this.letterCompletionState || {};
            const nextIndex = typeof state.nextIndex === "number" ? state.nextIndex : this.currentLetterIndex + 1;

            this.hideLetterCompletion();

            if (nextIndex < window.LETTERS.length) {
                const nextLetter = window.LETTERS[nextIndex];
                if (!this.isLetterAvailableForPlan(nextLetter)) {
                    this.showLetterPaywall(nextLetter);
                    return;
                }

                this.loadLetter(nextIndex);
                return;
            }

            this.showCertificate();
        };

        PhonicsGameLab.prototype.openCompletionOptionalGames = function openCompletionOptionalGames() {
            this.hideLetterCompletion();
            if (typeof this.showGameSelection === "function") {
                this.showGameSelection();
            }
        };

        PhonicsGameLab.prototype.openCompletionParentReport = function openCompletionParentReport() {
            if (window.LEVEL_ONE_DISABLED_FEATURES?.parentReport) {
                this.hideLetterCompletion();
                if (typeof this.showToast === "function") {
                    this.showToast("تقرير ولي الأمر غير متاح في هذه الباقة.", 3000, "info");
                }
                return;
            }
            const state = this.letterCompletionState || {};
            this.hideLetterCompletion();
            if (typeof this.showParentReport === "function" && state.letter) {
                this.showParentReport(state.letter, state.entry);
            }
        };
    };
})(window);
