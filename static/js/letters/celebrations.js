(function (window) {
    "use strict";

    // Celebration effects and win screens, extracted verbatim from the inline
    // script in templates/letters.html. Method bodies are unchanged, so the
    // balloons, confetti, win messages and modal wording are all identical.
    let LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

    class LettersCelebrations {
        launchBalloonsCelebration() {
            // Prevent multiple celebrations
            if (this.isCelebrating) return;
            this.isCelebrating = true;

            const container = document.body;
            const celebrationElements = [];

            // Create fewer balloons for better performance
            for (let i = 0; i < 15; i++) {
                const balloon = document.createElement('div');
                balloon.className = 'celebrate-balloon';
                balloon.textContent = '🎈';
                balloon.style.left = Math.random() * 100 + 'vw';
                balloon.style.animationDuration = (Math.random() * 1.5 + 2) + 's';
                balloon.style.fontSize = (Math.random() * 15 + 25) + 'px';
                container.appendChild(balloon);
                celebrationElements.push(balloon);
            }

            // Clean up celebration elements
            this.gameTimeouts.push(setTimeout(() => {
                celebrationElements.forEach(element => {
                    if (element.parentNode) {
                        element.parentNode.removeChild(element);
                    }
                });
                this.isCelebrating = false;
            }, 4000));

            this.createConfetti();
        }

        createConfetti() {
            // Prevent multiple confetti
            if (this.isConfettiActive) return;
            this.isConfettiActive = true;

            const colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff'];
            const confettiElements = [];

            // Reduce confetti count for better performance
            for (let i = 0; i < 50; i++) {
                const confetti = document.createElement('div');
                confetti.className = 'confetti';
                confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
                confetti.style.left = Math.random() * 100 + 'vw';
                confetti.style.animationDuration = (Math.random() * 2 + 1.5) + 's';
                confetti.style.opacity = Math.random();
                document.body.appendChild(confetti);
                confettiElements.push(confetti);
            }

            // Clean up confetti elements
            this.gameTimeouts.push(setTimeout(() => {
                confettiElements.forEach(element => {
                    if (element.parentNode) {
                        element.parentNode.removeChild(element);
                    }
                });
                this.isConfettiActive = false;
            }, 4000));
        }

        // ============ إدارة الفوز والخسارة ============

        handleGameWin(gameName, letter = null) {
            const targetLetter = letter || LETTERS[this.currentLetterIndex];
            this.markGameCompleted(targetLetter, gameName);

            // Show motivational message
            this.showGameWinMessage(gameName);

            // Clean up and show win modal
            this.cleanupGameResources();
            this.gameModal.style.display = 'none';
            this.winModal.style.display = 'flex';
        }

        handleGameLose(gameName) {
            this.cleanupGameResources();
            this.gameModal.style.display = 'none';
            this.showToast('حاول مرة أخرى! أنت تتعلم وتتحسن 💪', 3000);
        }

        showGameWinMessage(gameName) {
            const messages = {
                'match': [
                    'أحسنت! أنت بطل الحروف 💪',
                    'رائع! دماغك يلمع ذكاء ✨',
                    'ممتاز! ذاكرتك قوية جداً! 🧠',
                    'عمل مدهش! أنت تتقن المطابقة! 🌟'
                ],
                'balloons': [
                    'عظيم! سرعتك مذهلة! ⚡',
                    'برافو! انتباهك رائع! 🎯',
                    'هائل! تركيزك مدهش! 🎆',
                    'أنت سريع جداً! استمر هكذا! 🚀'
                ],

                'memory': [
                    'عبقري! ذاكرتك قوية جداً! 🧠',
                    'رائع! تذكر بشكل ممتاز! ✨',
                    'ما شاء الله! ذاكرة حديدية! 💎',
                    'أنت ذكي جداً! 🎓'
                ],
                'wordsearch': [
                    'أحسنت! عيناك كالصقر! 🦅',
                    'رائع! وجدت كل الكلمات! 🔍',
                    'ممتاز! قوة ملاحظة عالية! 👀'
                ]
            };

            const gameMessages = messages[gameName] || ['أحسنت! استمر في التقدم! 🎉', 'عمل رائع! 🌟', 'أنت مبدع! ✨'];
            const randomMessage = gameMessages[Math.floor(Math.random() * gameMessages.length)];

            this.showToast(randomMessage, 4000, 'success');
        }

        showWinGame() {
            // Prevent multiple calls
            if (this.isGameEnding) return;
            this.isGameEnding = true;

            // Stop the game immediately
            this.gameRunning = false;

            const currentLetter = LETTERS[this.currentLetterIndex];
            this.markGameCompleted(currentLetter, this.currentGame);

            // Clean up game resources first
            this.cleanupGameResources();

            // Launch celebration
            this.launchBalloonsCelebration();
            this.soundManager.playSound('applause');

            // Prepare Victory Screen Content
            const gameNames = {
                'match': 'لعبة المطابقة',
                'balloons': 'لعبة البالونات',
                'memory': 'لعبة الذاكرة',


                'shooting': 'اصطياد الحرف',
                'search': 'لعبة البحث',
                'typing': 'الكتابة السريعة'
            };

            const motivationalMessages = [
                "أنت بطل حقيقي! 🌟",
                "أداء مذهل! استمر في التألق! ✨",
                "رائع! أنت تتقدم بسرعة! 🚀",
                "ممتاز! ذكاؤك يبهرنا! 💡",
                "عمل رائع! المستقبل بانتظارك! 🎓",
                "أنت نجم ساطع في سماء العلم! ⭐",
                "إنجاز رائع! نحن فخورون بك! 🏆",
                "ذكاء خارق! استمر في الإبداع! 🧠"
            ];
            const randomMsg = motivationalMessages[Math.floor(Math.random() * motivationalMessages.length)];

            // Check remaining games
            this.updateLetterExerciseProgress(currentLetter);
            const missingGames = this.getMissingRequiredGames(currentLetter);

            let nextStepsHtml = '';
            if (missingGames.length > 0) {
                const missingNames = missingGames.map(g => `<li>${gameNames[g] || g}</li>`).join('');
                nextStepsHtml = `
                    <div style="margin-top: 20px; background: #f0f9ff; padding: 15px; border-radius: 10px; border: 2px solid #bae6fd;">
                        <h4 style="color: #0284c7; margin-bottom: 10px;">الألعاب المتبقية لإكمال الحرف:</h4>
                        <ul style="list-style: none; padding: 0; color: #0369a1; font-weight: bold;">
                            ${missingNames}
                        </ul>
                    </div>
                `;
            } else {
                nextStepsHtml = `
                    <div style="margin-top: 20px; background: #dcfce7; padding: 15px; border-radius: 10px; border: 2px solid #86efac;">
                        <h4 style="color: #15803d; margin: 0;">🎉 مبروك! لقد أكملت جميع ألعاب هذا الحرف!</h4>
                    </div>
                `;
            }

            // Update Modal Content
            const modalContent = this.gameModal.querySelector('.game-modal-content');
            modalContent.innerHTML = `
                <div style="text-align: center; padding: 20px;">
                    <div style="font-size: 60px; margin-bottom: 10px;">🏆</div>
                    <h2 style="color: #f59e0b; font-size: 28px; margin-bottom: 10px;">${randomMsg}</h2>
                    <p style="color: #64748b; font-size: 18px;">لقد فزت في ${gameNames[this.currentGame] || 'اللعبة'}!</p>

                    ${nextStepsHtml}

                    <button id="backToGamesBtn" style="
                        margin-top: 25px;
                        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
                        color: white;
                        border: none;
                        padding: 12px 30px;
                        font-size: 18px;
                        border-radius: 50px;
                        cursor: pointer;
                        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4);
                        transition: transform 0.2s;
                    ">العودة للألعاب 🎮</button>
                </div>
            `;

            // Add event listener to the new button
            document.getElementById('backToGamesBtn').addEventListener('click', () => {
                this.gameModal.style.display = 'none';
                this.showGames(); // Return to games list
            });

            // Reset game ending flag
            setTimeout(() => {
                this.isGameEnding = false;
            }, 1000);
        }

        showWinModal() {
            const score = parseInt(this.gameScoreEl.textContent);
            const timeLeft = this.gameTimeLeft;
            const accuracy = this.gameStats.accuracy;

            this.finalScoreEl.textContent = score;
            this.finalTimeEl.textContent = timeLeft;
            this.finalAccuracyEl.textContent = `${accuracy}%`;

            const winMessages = [
                "سلمت يابطل! 🔥 أنت نجم المستقبل!",
                "مذهل! مهاراتك لا تصدق! ✨",
                "إتقان رائع! أنت بطل الحروف! 🏆",
                "أداء متميز! تستحق كل التقدير! ⭐",
                "براعة فائقة! أنت متعلم ممتاز! 💫"
            ];

            const fireworkEmojis = ["🎆", "🎇", "✨", "🌟", "💥", "🔥", "⭐", "⚡"];

            this.winTitle.textContent = winMessages[Math.floor(Math.random() * winMessages.length)];
            this.winSubtitle.textContent = `حققت ${score} نقطة بدقة ${accuracy}%`;
            this.winAnimation.textContent = fireworkEmojis[Math.floor(Math.random() * fireworkEmojis.length)] +
                                           fireworkEmojis[Math.floor(Math.random() * fireworkEmojis.length)] +
                                           fireworkEmojis[Math.floor(Math.random() * fireworkEmojis.length)];

            this.winModal.style.display = 'flex';
            this.soundManager.playSound('fireworks');
        }
    }

    window.installLettersCelebrations = function installLettersCelebrations(GameClass) {
        if (!GameClass || !GameClass.prototype) return;

        LETTERS = window.LETTERS || LETTERS;

        Object.getOwnPropertyNames(LettersCelebrations.prototype).forEach(name => {
            if (name !== "constructor") {
                GameClass.prototype[name] = LettersCelebrations.prototype[name];
            }
        });
    };
})(window);
