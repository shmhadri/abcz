(function (window) {
    "use strict";

    const fallbackIcon = "\uD83D\uDD24";
    const speakIcon = "\uD83D\uDD0A";
    const correctMessage = "\u2705 \u0635\u062D! \u0645\u0645\u062A\u0627\u0632";
    const wrongMessage = "\u274C \u062D\u0627\u0648\u0644 \u0645\u0631\u0629 \u062B\u0627\u0646\u064A\u0629";

    const DragWordGameMethods = {
        renderWordWriting(letter, words) {
            if (!this.wordWritingList) return;
            this.wordWritingList.innerHTML = "";
            if (!words || words.length === 0) return;

            const letterProgress = this.ensureLetterRecord(letter);

            words.forEach((wordData, wordIndex) => {
                const item = document.createElement("div");
                item.className = "drag-word-card";
                item.dataset.word = wordData.word;

                const header = document.createElement("div");
                header.className = "drag-word-header";

                const info = document.createElement("div");
                info.className = "word-info";

                const emoji = document.createElement("span");
                emoji.className = "word-emoji";
                emoji.textContent = wordData.emoji || fallbackIcon;

                const translation = document.createElement("span");
                translation.textContent = wordData.translation || wordData.word;

                info.appendChild(emoji);
                info.appendChild(translation);

                const speakBtn = document.createElement("button");
                speakBtn.type = "button";
                speakBtn.className = "icon-btn speak-btn";
                speakBtn.title = "\u0646\u0637\u0642 \u0627\u0644\u0643\u0644\u0645\u0629";
                speakBtn.textContent = speakIcon;
                speakBtn.addEventListener("click", () => this.soundManager.speak(wordData.word));

                header.appendChild(info);
                header.appendChild(speakBtn);

                const slots = document.createElement("div");
                slots.className = "drag-word-target";

                const letters = String(wordData.word || "").trim().toLowerCase().split("");
                letters.forEach((_, slotIndex) => {
                    slots.appendChild(this.createWordSlot(slotIndex));
                });

                const scrambled = document.createElement("div");
                scrambled.className = "scrambled-word-letters";

                this.shuffleWordLetters(letters).forEach((char, letterIndex) => {
                    scrambled.appendChild(this.createDragWordLetter(char, wordIndex, letterIndex));
                });

                const feedback = document.createElement("div");
                feedback.className = "drag-word-feedback";

                item.appendChild(header);
                item.appendChild(slots);
                item.appendChild(scrambled);
                item.appendChild(feedback);

                if (letterProgress.exercises.words[wordData.word]) {
                    this.markDragWordComplete(item, wordData.word, true);
                }

                this.wordWritingList.appendChild(item);
            });
        },

        shuffleWordLetters(letters) {
            const shuffled = [...letters];
            for (let i = shuffled.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
            }
            return shuffled;
        },

        createWordSlot(index) {
            const slot = document.createElement("button");
            slot.type = "button";
            slot.className = "drag-word-slot";
            slot.dataset.index = index;
            slot.dataset.letter = "";

            slot.addEventListener("dragover", (event) => {
                event.preventDefault();
                slot.classList.add("drag-over");
            });
            slot.addEventListener("dragleave", () => slot.classList.remove("drag-over"));
            slot.addEventListener("drop", (event) => this.handleDragWordDrop(event, slot));
            slot.addEventListener("click", () => this.handleWordSlotClick(slot));

            return slot;
        },

        createDragWordLetter(char, wordIndex, letterIndex) {
            const button = document.createElement("button");
            button.type = "button";
            button.className = "drag-word-letter";
            button.textContent = char;
            button.draggable = true;
            button.dataset.letter = char;
            button.dataset.id = `drag-${wordIndex}-${letterIndex}-${Date.now()}-${Math.random().toString(36).slice(2)}`;

            button.addEventListener("dragstart", (event) => {
                event.dataTransfer.setData("text/plain", JSON.stringify({
                    id: button.dataset.id,
                    letter: char
                }));
            });
            button.addEventListener("click", () => this.handleDragWordLetterClick(button));

            return button;
        },

        handleDragWordLetterClick(button) {
            const card = button.closest(".drag-word-card");
            if (!card || card.classList.contains("completed")) return;

            if (button.classList.contains("used")) {
                this.clearSlotForDragWordLetter(button);
                return;
            }

            card.querySelectorAll(".drag-word-letter.selected").forEach(el => el.classList.remove("selected"));
            button.classList.add("selected");
        },

        clearSlotForDragWordLetter(button) {
            const card = button.closest(".drag-word-card");
            if (!card) return;

            const slot = Array.from(card.querySelectorAll(".drag-word-slot"))
                .find(item => item.dataset.sourceId === button.dataset.id);
            if (slot) {
                this.clearDragWordSlot(slot);
            }
        },

        handleWordSlotClick(slot) {
            const card = slot.closest(".drag-word-card");
            if (!card || card.classList.contains("completed")) return;

            if (slot.classList.contains("filled")) {
                this.clearDragWordSlot(slot);
                return;
            }

            const selected = card.querySelector(".drag-word-letter.selected:not(.used)");
            if (selected) {
                this.placeDragLetterInSlot(slot, selected.dataset.letter, selected);
                selected.classList.remove("selected");
            }
        },

        handleDragWordDrop(event, slot) {
            event.preventDefault();
            slot.classList.remove("drag-over");

            let data = null;
            try {
                data = JSON.parse(event.dataTransfer.getData("text/plain"));
            } catch (error) {
                return;
            }

            const card = slot.closest(".drag-word-card");
            const letterButton = card?.querySelector(`[data-id="${data.id}"]`);
            if (!letterButton || letterButton.classList.contains("used")) return;

            if (slot.classList.contains("filled")) {
                this.clearDragWordSlot(slot);
            }
            this.placeDragLetterInSlot(slot, data.letter, letterButton);
        },

        placeDragLetterInSlot(slot, letter, sourceButton) {
            slot.textContent = letter;
            slot.dataset.letter = letter;
            slot.dataset.sourceId = sourceButton.dataset.id;
            slot.classList.add("filled");
            sourceButton.classList.add("used");
            sourceButton.classList.remove("selected");
            sourceButton.setAttribute("aria-pressed", "true");
            sourceButton.title = "\u0627\u0636\u063a\u0637 \u0644\u0625\u0631\u062c\u0627\u0639 \u0627\u0644\u062d\u0631\u0641";
            this.checkDragWordItem(slot.closest(".drag-word-card"));
        },

        clearDragWordSlot(slot) {
            const sourceId = slot.dataset.sourceId;
            const card = slot.closest(".drag-word-card");
            if (sourceId) {
                const sourceButton = card?.querySelector(`[data-id="${sourceId}"]`);
                if (sourceButton) {
                    sourceButton.classList.remove("used");
                    sourceButton.setAttribute("aria-pressed", "false");
                }
            }
            slot.textContent = "";
            slot.dataset.letter = "";
            slot.dataset.sourceId = "";
            slot.classList.remove("filled");

            const feedback = slot.closest(".drag-word-card")?.querySelector(".drag-word-feedback");
            if (feedback) {
                feedback.textContent = "";
                feedback.className = "drag-word-feedback";
            }
        },

        checkDragWordItem(card) {
            if (!card || card.classList.contains("completed")) return;

            const expected = card.dataset.word;
            const slots = Array.from(card.querySelectorAll(".drag-word-slot"));
            if (!slots.every(slot => slot.dataset.letter)) return;

            const answer = slots.map(slot => slot.dataset.letter).join("").toLowerCase();
            const feedback = card.querySelector(".drag-word-feedback");

            if (answer === expected) {
                this.markDragWordComplete(card, expected);
            } else {
                if (feedback) {
                    feedback.textContent = "\u274c \u062d\u0627\u0648\u0644 \u062a\u0628\u062f\u064a\u0644 \u062d\u0631\u0641 \u0623\u0648 \u0627\u0636\u063a\u0637 \u0639\u0644\u0649 \u0627\u0644\u062e\u0627\u0646\u0629 \u0644\u0625\u0631\u062c\u0627\u0639\u0647";
                    feedback.className = "drag-word-feedback wrong";
                }
                this.soundManager.playSound("error");
            }
        },

        resetDragWordItem(card) {
            if (!card || card.classList.contains("completed")) return;
            card.querySelectorAll(".drag-word-slot").forEach(slot => {
                slot.textContent = "";
                slot.dataset.letter = "";
                slot.dataset.sourceId = "";
                slot.classList.remove("filled", "drag-over");
            });
            card.querySelectorAll(".drag-word-letter").forEach(letter => {
                letter.classList.remove("used", "selected");
                letter.setAttribute("aria-pressed", "false");
            });
            const feedback = card.querySelector(".drag-word-feedback");
            if (feedback) {
                feedback.textContent = "";
                feedback.className = "drag-word-feedback";
            }
        },

        markDragWordComplete(card, expected, isLoading = false) {
            const letter = this.progress.currentLetter;
            const letterProgress = this.ensureLetterRecord(letter);
            const word = String(expected || "").trim().toLowerCase();
            if (!word) return;

            letterProgress.exercises.words[word] = word;
            card.classList.add("completed");

            const slots = Array.from(card.querySelectorAll(".drag-word-slot"));
            word.toLowerCase().split("").forEach((char, index) => {
                if (slots[index]) {
                    slots[index].textContent = char;
                    slots[index].dataset.letter = char;
                    slots[index].classList.add("filled");
                }
            });

            card.querySelectorAll(".drag-word-letter").forEach(button => button.classList.add("used"));

            const feedback = card.querySelector(".drag-word-feedback");
            if (feedback) {
                feedback.textContent = correctMessage;
                feedback.className = "drag-word-feedback correct";
            }

            if (!isLoading) {
                this.updateAndCommitScores();
                this.soundManager.playSound("success");
                this.soundManager.speak(word);
            }
        },

        calculateCurrentWordsScore() {
            const letter = this.progress.currentLetter;
            if (!letter) return 0;
            const letterProgress = this.ensureLetterRecord(letter);
            return Object.keys(letterProgress.exercises.words || {}).length;
        }
    };

    window.installDragWordGame = function installDragWordGame(GameClass) {
        if (!GameClass || !GameClass.prototype) return;
        Object.assign(GameClass.prototype, DragWordGameMethods);
    };

    window.startDragWordGame = function startDragWordGame(instance, letter, words) {
        if (instance && typeof instance.renderWordWriting === "function") {
            instance.renderWordWriting(letter, words);
        }
    };

    window.loadNextDragWord = window.startDragWordGame;
})(window);
