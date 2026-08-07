(function (window) {
    "use strict";

    // Canvas mini-games extracted verbatim from the inline script in
    // templates/letters.html. Method bodies are unchanged; only the surrounding
    // wrapper is new, so gameplay, scoring and win conditions are identical.
    //
    // These two values are the module's only dependencies on the page. They are
    // resolved at install time (not at load time) so this file sees exactly the
    // same objects the application uses, whatever the script order turns out to be.
    let LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");
    let LETTER_DATA = {};

    class LettersCanvasGames {
        initShootingGame(ctx, canvas) {
            const currentLetter = LETTERS[this.currentLetterIndex];
            const app = this;

            // إظهار أزرار التحكم باللمس دائماً
            this.touchControlsEl.style.display = 'flex';
            canvas.style.touchAction = 'none'; // Prevent scrolling

            const cannon = {
                x: canvas.width / 2,
                y: canvas.height - 50,
                width: 60,
                height: 30,
                draw: function() {
                    ctx.save();
                    ctx.translate(this.x, this.y);

                    ctx.fillStyle = '#8b5a2b';
                    ctx.fillRect(-this.width/2, -this.height/2, this.width, this.height);

                    ctx.fillStyle = '#1e293b';
                    ctx.fillRect(-5, -this.height/2 - 10, 10, 10); // Nozzle pointing up

                    ctx.restore();
                },
                update: function() {
                    if (app.touchControls.left && this.x > this.width/2) this.x -= 5;
                    if (app.touchControls.right && this.x < canvas.width - this.width/2) this.x += 5;
                }
            };

            const bullets = [];
            const fishes = [];

            // Increased fish count to 20 for density
            for (let i = 0; i < 20; i++) {
                // Increased probability to 70% for correct letter
                const isCorrect = Math.random() > 0.3;
                const letter = isCorrect ?
                    (Math.random() > 0.5 ? currentLetter : currentLetter.toLowerCase()) :
                    LETTERS[Math.floor(Math.random() * LETTERS.length)];

                fishes.push({
                    x: Math.random() * canvas.width,
                    y: Math.random() * (canvas.height - 200),
                    width: 70, // Increased width
                    height: 35, // Increased height
                    speedX: (Math.random() - 0.5) * 2,
                    speedY: (Math.random() - 0.5) * 1,
                    letter: letter,
                    isCorrect: isCorrect || letter.toLowerCase() === currentLetter.toLowerCase(),
                    color: isCorrect ? '#4cc9f0' : '#ef4444',
                    draw: function() {
                        ctx.fillStyle = this.color;
                        ctx.beginPath();
                        ctx.ellipse(this.x, this.y, this.width/2, this.height/2, 0, 0, Math.PI * 2);
                        ctx.fill();

                        ctx.beginPath();
                        ctx.moveTo(this.x - this.width/2, this.y);
                        ctx.lineTo(this.x - this.width, this.y - this.height/2);
                        ctx.lineTo(this.x - this.width, this.y + this.height/2);
                        ctx.closePath();
                        ctx.fill();

                        ctx.fillStyle = 'white';
                        ctx.beginPath();
                        ctx.arc(this.x + this.width/3, this.y - 3, 3, 0, Math.PI * 2);
                        ctx.fill();

                        ctx.fillStyle = 'white';
                        ctx.font = 'bold 28px Arial'; // Increased font size significantly
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillText(this.letter, this.x + this.width/4, this.y);
                    },
                    update: function() {
                        this.x += this.speedX;
                        this.y += this.speedY;

                        if (this.x < this.width/2 || this.x > canvas.width - this.width/2) {
                            this.speedX = -this.speedX;
                        }
                        if (this.y < 20 || this.y > canvas.height - 100) {
                            this.speedY = -this.speedY;
                        }
                    }
                });
            }

            const shoot = () => {
                const bullet = {
                    x: cannon.x,
                    y: cannon.y - cannon.height/2 - 10,
                    radius: 5,
                    speed: 8,
                    color: '⭐',
                    draw: function() {
                        ctx.fillStyle = '#f59e0b';
                        ctx.font = '24px Arial';
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillText(this.color, this.x, this.y);
                    },
                    update: function() {
                        this.y -= this.speed; // Move straight up

                        for (let i = fishes.length - 1; i >= 0; i--) {
                            const fish = fishes[i];
                            const dx = this.x - fish.x;
                            const dy = this.y - fish.y;
                            const distance = Math.sqrt(dx * dx + dy * dy);

                            if (distance < fish.width/2 + this.radius) {
                                if (fish.isCorrect) {
                                    app.gameStats.successCount++;
                                    app.gameStats.totalAttempts++;
                                    app.gameScoreEl.textContent = parseInt(app.gameScoreEl.textContent) + 10;
                                    app.soundManager.playSound('success');

                                    // Win condition: 15 correct hits
                                    if (app.gameStats.successCount >= 15) {
                                        app.showWinGame();
                                        return;
                                    }
                                } else {
                                    app.gameStats.totalAttempts++;
                                    app.gameScoreEl.textContent = Math.max(0, parseInt(app.gameScoreEl.textContent) - 5);
                                    app.soundManager.playSound('error');
                                }

                                fishes.splice(i, 1);
                                bullets.splice(bullets.indexOf(this), 1);

                                // Respawn logic with high probability for correct letter
                                const isCorrect = Math.random() > 0.3;
                                const letter = isCorrect ?
                                    (Math.random() > 0.5 ? currentLetter : currentLetter.toLowerCase()) :
                                    LETTERS[Math.floor(Math.random() * LETTERS.length)];

                                fishes.push({
                                    x: Math.random() * canvas.width,
                                    y: Math.random() * (canvas.height - 200),
                                    width: 70, // Increased width
                                    height: 35, // Increased height
                                    speedX: (Math.random() - 0.5) * 2,
                                    speedY: (Math.random() - 0.5) * 1,
                                    letter: letter,
                                    isCorrect: isCorrect || letter.toLowerCase() === currentLetter.toLowerCase(),
                                    color: isCorrect ? '#4cc9f0' : '#ef4444',
                                    draw: function() {
                                        ctx.fillStyle = this.color;
                                        ctx.beginPath();
                                        ctx.ellipse(this.x, this.y, this.width/2, this.height/2, 0, 0, Math.PI * 2);
                                        ctx.fill();

                                        ctx.beginPath();
                                        ctx.moveTo(this.x - this.width/2, this.y);
                                        ctx.lineTo(this.x - this.width, this.y - this.height/2);
                                        ctx.lineTo(this.x - this.width, this.y + this.height/2);
                                        ctx.closePath();
                                        ctx.fill();

                                        ctx.fillStyle = 'white';
                                        ctx.beginPath();
                                        ctx.arc(this.x + this.width/3, this.y - 3, 3, 0, Math.PI * 2);
                                        ctx.fill();

                                        ctx.fillStyle = 'white';
                                        ctx.font = 'bold 28px Arial'; // Increased font size
                                        ctx.textAlign = 'center';
                                        ctx.textBaseline = 'middle';
                                        ctx.fillText(this.letter, this.x + this.width/4, this.y);
                                    },
                                    update: function() {
                                        this.x += this.speedX;
                                        this.y += this.speedY;

                                        if (this.x < this.width/2 || this.x > canvas.width - this.width/2) {
                                            this.speedX = -this.speedX;
                                        }
                                        if (this.y < 20 || this.y > canvas.height - 100) {
                                            this.speedY = -this.speedY;
                                        }
                                    }
                                });

                                app.updateGameStats();
                                return;
                            }
                        }

                        return this.x < -10 || this.x > canvas.width + 10 || this.y < -10;
                    }
                };

                bullets.push(bullet);
                app.soundManager.playSound('click');
            };

            // Touch Controls
            canvas.addEventListener('touchmove', (e) => {
                e.preventDefault();
                const rect = canvas.getBoundingClientRect();
                const touch = e.touches[0];
                const touchX = touch.clientX - rect.left;

                cannon.x = touchX;

                if (cannon.x < cannon.width/2) cannon.x = cannon.width/2;
                if (cannon.x > canvas.width - cannon.width/2) cannon.x = canvas.width - cannon.width/2;
            }, { passive: false });

            canvas.addEventListener('touchstart', (e) => {
                e.preventDefault();
                // Fire on tap
                shoot();
            }, { passive: false });

            const gameLoop = () => {
                if (!app.gameRunning) return;

                if (app.isPaused) {
                    this.gameAnimationFrame = requestAnimationFrame(gameLoop);
                    return;
                }

                ctx.clearRect(0, 0, canvas.width, canvas.height);

                // Re-center cannon on resize (only Y)
                cannon.y = canvas.height - 50;

                const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
                gradient.addColorStop(0, '#4cc9f0');
                gradient.addColorStop(1, '#3a0ca3');
                ctx.fillStyle = gradient;
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
                for (let i = 0; i < canvas.width; i += 20) {
                    ctx.beginPath();
                    ctx.arc(i, 50 + Math.sin(Date.now()/1000 + i/50) * 10, 8, 0, Math.PI * 2);
                    ctx.fill();
                }

                cannon.update();
                cannon.draw();

                fishes.forEach(fish => {
                    fish.update();
                    fish.draw();
                });

                for (let i = bullets.length - 1; i >= 0; i--) {
                    const bullet = bullets[i];
                    bullet.draw();
                    if (bullet.update()) {
                        bullets.splice(i, 1);
                    }
                }

                if (app.touchControls.action) {
                    shoot();
                    app.touchControls.action = false;
                }

                this.gameAnimationFrame = requestAnimationFrame(gameLoop);
            };

            gameLoop();

            const keyHandler = (e) => {
                if (e.key === 'ArrowLeft') this.touchControls.left = true;
                if (e.key === 'ArrowRight') this.touchControls.right = true;
                if (e.key === ' ' || e.key === 'Spacebar') {
                    shoot();
                }
            };

            const keyUpHandler = (e) => {
                if (e.key === 'ArrowLeft') this.touchControls.left = false;
                if (e.key === 'ArrowRight') this.touchControls.right = false;
            };

            document.addEventListener('keydown', keyHandler);
            document.addEventListener('keyup', keyUpHandler);

            this.currentKeyHandlers = { keydown: keyHandler, keyup: keyUpHandler };
        }

        initTypingGame(ctx, canvas) {
            const currentLetter = LETTERS[this.currentLetterIndex];
            const app = this;

            // Mobile keyboard support
            const hiddenInput = document.createElement('input');
            hiddenInput.style.position = 'absolute';
            hiddenInput.style.opacity = '0';
            hiddenInput.style.top = '-1000px';
            // Prevent zooming on focus by setting font size
            hiddenInput.style.fontSize = '16px';
            document.body.appendChild(hiddenInput);
            this.hiddenInput = hiddenInput;

            const focusInput = (e) => {
                // Don't prevent default on click, otherwise focus might not work
                hiddenInput.focus();
            };

            canvas.addEventListener('click', focusInput);
            canvas.addEventListener('touchstart', (e) => {
                // e.preventDefault(); // Don't prevent default here, we need focus
                hiddenInput.focus();
            }, { passive: true });

            hiddenInput.addEventListener('input', (e) => {
                if (e.data) {
                    const key = e.data.toLowerCase();
                    // Call keyHandler logic
                    if (this.currentKeyHandler) {
                        this.currentKeyHandler({ key: key });
                    }
                    hiddenInput.value = '';
                }
            });

            const fallingLetters = [];
            const letterSpeed = 0.5; // Slower speed (was 1)
            let currentInput = '';
            let gameActive = true;

            const createLetter = () => {
                const isCorrect = Math.random() > 0.5;
                const letterData = LETTER_DATA[currentLetter];

                let content;
                let isWord = false;

                if (Math.random() > 0.6 && letterData.words.length > 0) {
                    // Spawn a word
                    const wordObj = letterData.words[Math.floor(Math.random() * letterData.words.length)];
                    content = wordObj.word;
                    isWord = true;
                } else {
                    // Spawn a letter
                    content = isCorrect ?
                        (Math.random() > 0.5 ? currentLetter : currentLetter.toLowerCase()) :
                        LETTERS[Math.floor(Math.random() * LETTERS.length)];
                }

                fallingLetters.push({
                    content: content,
                    isWord: isWord,
                    x: Math.random() * (canvas.width - 100) + 50,
                    y: -50,
                    speed: (letterSpeed + Math.random() * 0.5), // Slower variation
                    typed: '',
                    completed: false
                });
            };

            createLetter();

            const keyHandler = (e) => {
                if (!gameActive) return;

                if (e.key.length === 1 && e.key.match(/[a-zA-Z]/)) {
                    const char = e.key.toLowerCase();
                    app.soundManager.playSound('click');

                    // Check all falling items
                    for (let i = fallingLetters.length - 1; i >= 0; i--) {
                        const item = fallingLetters[i];
                        if (item.completed) continue;

                        const target = item.content.toLowerCase();
                        const nextCharIndex = item.typed.length;

                        if (target[nextCharIndex] === char) {
                            item.typed += char;

                            if (item.typed === target) {
                                item.completed = true;
                                app.gameStats.successCount++;
                                app.gameStats.totalAttempts++;
                                app.gameScoreEl.textContent = parseInt(app.gameScoreEl.textContent) + (item.isWord ? 20 : 10);
                                app.soundManager.playSound('success');
                                app.updateGameStats();

                                // Win condition: 10 correct types
                                if (app.gameStats.successCount >= 10) {
                                    app.showWinGame();
                                }
                            }
                            // Only process one correct keystroke per frame to avoid ambiguity if multiple same letters
                            break;
                        }
                    }
                }
            };

            document.addEventListener('keydown', keyHandler);
            this.currentKeyHandler = keyHandler;

            const gameLoop = () => {
                if (!app.gameRunning) return;
                if (!gameActive) return;

                if (app.isPaused) {
                    this.gameAnimationFrame = requestAnimationFrame(gameLoop);
                    return;
                }

                ctx.clearRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = '#0f172a';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = '#f1f5f9';
                ctx.font = 'bold 24px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'top';
                ctx.fillText(`الكتابة السريعة - الحرف ${currentLetter}`, canvas.width/2, 10);

                ctx.fillStyle = '#cbd5e1';
                ctx.font = '16px Arial';
                ctx.fillText('اكتب الكلمات أو الحروف قبل وصولها للأسفل!', canvas.width/2, 40);

                fallingLetters.forEach((item, index) => {
                    item.y += item.speed;

                    // Handle resize
                    if (item.x > canvas.width - 50) item.x = canvas.width - 50;

                    if (item.y > canvas.height - 50 && !item.completed) {
                        app.gameStats.totalAttempts++;
                        fallingLetters.splice(index, 1);
                        app.updateGameStats();
                        app.soundManager.playSound('error');
                    }

                    if (item.y > canvas.height) {
                        fallingLetters.splice(index, 1);
                    }

                    // Draw
                    ctx.font = item.isWord ? 'bold 24px Arial' : 'bold 32px Arial';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';

                    // Base text (faded)
                    ctx.fillStyle = item.completed ? '#22c55e' : '#f472b6';
                    ctx.fillText(item.content, item.x, item.y);

                    // Typed part (highlighted)
                    if (item.typed.length > 0) {
                        const typedPart = item.content.substring(0, item.typed.length);
                        ctx.fillStyle = '#4cc9f0';
                        // Simple overlay for typed part (centered alignment makes exact overlay tricky without measuring)
                        // For simplicity in canvas centered text, we can just redraw the whole thing in a different color if fully typed,
                        // or measure width. Let's try measuring.
                        const totalWidth = ctx.measureText(item.content).width;
                        const typedWidth = ctx.measureText(typedPart).width;
                        const startX = item.x - totalWidth / 2;

                        ctx.textAlign = 'left';
                        ctx.fillText(typedPart, startX, item.y);
                        ctx.textAlign = 'center'; // Reset
                    }
                });

                // Increased spawn rate (0.03 instead of 0.015)
                if (Math.random() < 0.03 && fallingLetters.length < 12) {
                    createLetter();
                }

                this.gameAnimationFrame = requestAnimationFrame(gameLoop);
            };

            gameLoop();
        }

        initMemoryGame(ctx, canvas) {
            const currentLetter = LETTERS[this.currentLetterIndex];
            const app = this;

            const cards = [];
            const padding = 10;
            const cols = 4;
            const rows = 3;

            // Dynamic card size
            let availableWidth = canvas.width - (cols + 1) * padding;
            let cardWidth = Math.min(80, availableWidth / cols);
            let cardHeight = cardWidth * 1.25;

            const cardData = [];
            const letters = [currentLetter, currentLetter.toLowerCase()];

            for (let i = 0; i < 6; i++) {
                const letter = letters[i % 2];
                cardData.push({
                    type: 'letter',
                    value: letter,
                    pairId: i % 2
                });
            }

            for (let i = 0; i < 6; i++) {
                const letter = letters[i % 2];
                cardData.push({
                    type: 'letter',
                    value: letter,
                    pairId: i % 2
                });
            }

            cardData.sort(() => Math.random() - 0.5);

            for (let i = 0; i < rows; i++) {
                for (let j = 0; j < cols; j++) {
                    const index = i * cols + j;
                    if (index >= cardData.length) break;

                    cards.push({
                        col: j, // Store column for resize
                        row: i, // Store row for resize
                        x: j * (cardWidth + padding) + (canvas.width - (cols * (cardWidth + padding) - padding)) / 2,
                        y: i * (cardHeight + padding) + 50,
                        width: cardWidth,
                        height: cardHeight,
                        data: cardData[index],
                        flipped: false,
                        matched: false,
                        draw: function() {
                            ctx.fillStyle = this.flipped || this.matched ? '#ffffff' : '#4361ee';
                            ctx.fillRect(this.x, this.y, this.width, this.height);

                            ctx.strokeStyle = this.matched ? '#4ade80' : '#1e293b';
                            ctx.lineWidth = 2;
                            ctx.strokeRect(this.x, this.y, this.width, this.height);

                            if (this.flipped || this.matched) {
                                ctx.fillStyle = '#1e293b';
                                ctx.font = 'bold 40px Arial';
                                ctx.textAlign = 'center';
                                ctx.textBaseline = 'middle';
                                ctx.fillText(this.data.value, this.x + this.width/2, this.y + this.height/2);

                                ctx.fillStyle = '#475569';
                                ctx.font = '12px Arial';
                                ctx.fillText(
                                    'الحرف',
                                    this.x + this.width/2,
                                    this.y + 15
                                );
                            } else {
                                ctx.fillStyle = '#3a0ca3';
                                ctx.font = 'bold 24px Arial';
                                ctx.textAlign = 'center';
                                ctx.textBaseline = 'middle';
                                ctx.fillText('?', this.x + this.width/2, this.y + this.height/2);
                            }
                        },
                        contains: function(x, y) {
                            return x >= this.x && x <= this.x + this.width &&
                                   y >= this.y && y <= this.y + this.height;
                        }
                    });
                }
            }

            let firstCard = null;
            let secondCard = null;
            let canFlip = true;

            const clickHandler = (e) => {
                if (!canFlip) return;

                const rect = canvas.getBoundingClientRect();
                const mouseX = e.clientX - rect.left;
                const mouseY = e.clientY - rect.top;

                const clickedCard = cards.find(card =>
                    !card.matched && !card.flipped && card.contains(mouseX, mouseY)
                );

                if (!clickedCard) return;

                clickedCard.flipped = true;
                app.soundManager.playSound('click');

                if (!firstCard) {
                    firstCard = clickedCard;
                } else if (!secondCard) {
                    secondCard = clickedCard;
                    canFlip = false;

                    app.gameStats.totalAttempts++;

                    if (firstCard.data.pairId === secondCard.data.pairId &&
                        firstCard.data.value === secondCard.data.value) {
                        firstCard.matched = true;
                        secondCard.matched = true;
                        app.gameStats.successCount++;
                        app.gameScoreEl.textContent = parseInt(app.gameScoreEl.textContent) + 20;
                        app.soundManager.playSound('success');

                        if (cards.every(card => card.matched)) {
                            setTimeout(() => {
                                app.showWinGame();
                            }, 500);
                        }
                    } else {
                        app.soundManager.playSound('error');
                        setTimeout(() => {
                            firstCard.flipped = false;
                            secondCard.flipped = false;
                        }, 1000);
                    }

                    setTimeout(() => {
                        firstCard = null;
                        secondCard = null;
                        canFlip = true;
                        app.updateGameStats();
                    }, 1000);
                }
            };

            canvas.addEventListener('click', clickHandler);

            // Touch support for Memory Game
            canvas.addEventListener('touchstart', (e) => {
                e.preventDefault();
                const touch = e.touches[0];
                // Simulate click
                clickHandler({ clientX: touch.clientX, clientY: touch.clientY });
            }, { passive: false });

            this.currentClickHandler = clickHandler;

            const gameLoop = () => {
                if (!app.gameRunning) return;

                if (app.isPaused) {
                    this.gameAnimationFrame = requestAnimationFrame(gameLoop);
                    return;
                }

                ctx.clearRect(0, 0, canvas.width, canvas.height);

                // Recalculate positions on resize
                let availableWidth = canvas.width - (cols + 1) * padding;
                cardWidth = Math.min(80, availableWidth / cols);
                cardHeight = cardWidth * 1.25;

                const startX = (canvas.width - (cols * (cardWidth + padding) - padding)) / 2;
                cards.forEach(card => {
                    card.width = cardWidth;
                    card.height = cardHeight;
                    card.x = card.col * (cardWidth + padding) + startX;
                    card.y = card.row * (cardHeight + padding) + 50;
                });

                ctx.fillStyle = '#f8fafc';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = '#1e293b';
                ctx.font = 'bold 24px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'top';
                ctx.fillText(`لعبة الذاكرة - الحرف ${currentLetter}`, canvas.width/2, 10);

                cards.forEach(card => card.draw());

                this.gameAnimationFrame = requestAnimationFrame(gameLoop);
            };

            gameLoop();
        }

        initWordSearchGame(ctx, canvas) {
            const currentLetter = LETTERS[this.currentLetterIndex];
            const letterData = LETTER_DATA[currentLetter];
            // Use the words from the letter data, limited to 6 to fit nicely
            const targetWords = letterData.words.slice(0, 6).map((w) => ({
                word: w.word.toLowerCase(),
                translation: w.translation,
                found: false
            }));

            const app = this;

            const gridSize = 10;
            // Adjust cell size to fit grid on the left
            const cellSize = 35;
            const gridOffsetX = 20;
            const gridOffsetY = 60;

            const grid = [];

            // Initialize grid with empty placeholders
            for (let i = 0; i < gridSize; i++) {
                grid[i] = [];
                for (let j = 0; j < gridSize; j++) {
                    grid[i][j] = '.';
                }
            }

            const placedWords = [];
            let foundWordsCount = 0;

            targetWords.forEach(target => {
                let placed = false;
                let attempts = 0;
                const word = target.word;

                while (!placed && attempts < 100) {
                    const direction = Math.floor(Math.random() * 3);
                    const row = Math.floor(Math.random() * gridSize);
                    const col = Math.floor(Math.random() * gridSize);

                    if (this.canPlaceWord(grid, word, row, col, direction)) {
                        this.placeWord(grid, word, row, col, direction);
                        placedWords.push({
                            ...target, // Include translation and initial found state
                            row: row,
                            col: col,
                            direction: direction
                        });
                        placed = true;
                    }
                    attempts++;
                }
            });

            // Fill remaining empty spots with random letters
            for (let i = 0; i < gridSize; i++) {
                for (let j = 0; j < gridSize; j++) {
                    if (grid[i][j] === '.') {
                        grid[i][j] = LETTERS[Math.floor(Math.random() * LETTERS.length)].toLowerCase();
                    }
                }
            }

            const cells = [];
            let selectedCells = [];

            for (let i = 0; i < gridSize; i++) {
                for (let j = 0; j < gridSize; j++) {
                    cells.push({
                        row: i,
                        col: j,
                        x: j * cellSize + gridOffsetX,
                        y: i * cellSize + gridOffsetY,
                        size: cellSize,
                        letter: grid[i][j],
                        selected: false,
                        highlighted: false, // For permanently found words
                        draw: function() {
                            // Background
                            if (this.highlighted) {
                                ctx.fillStyle = '#86efac'; // Green for found
                            } else if (this.selected) {
                                ctx.fillStyle = '#4cc9f0'; // Blue for selecting
                            } else {
                                ctx.fillStyle = '#ffffff';
                            }
                            ctx.fillRect(this.x, this.y, this.size, this.size);

                            ctx.strokeStyle = '#cbd5e1';
                            ctx.lineWidth = 1;
                            ctx.strokeRect(this.x, this.y, this.size, this.size);

                            ctx.fillStyle = '#1e293b';
                            // Dynamic font size based on cell size
                            const fontSize = Math.floor(this.size * 0.6);
                            ctx.font = `bold ${fontSize}px Arial`;
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'middle';
                            ctx.fillText(this.letter, this.x + this.size/2, this.y + this.size/2 + 2);
                        },
                        contains: function(x, y) {
                            return x >= this.x && x <= this.x + this.size &&
                                   y >= this.y && y <= this.y + this.size;
                        }
                    });
                }
            }

            let isDragging = false;
            let startCell = null;

            const mouseDownHandler = (e) => {
                const rect = canvas.getBoundingClientRect();
                const mouseX = e.clientX - rect.left;
                const mouseY = e.clientY - rect.top;

                startCell = cells.find(cell => cell.contains(mouseX, mouseY));
                if (startCell) {
                    isDragging = true;
                    selectedCells = [startCell];
                    startCell.selected = true;
                }
            };

            const mouseMoveHandler = (e) => {
                if (!isDragging || !startCell) return;

                const rect = canvas.getBoundingClientRect();
                const mouseX = e.clientX - rect.left;
                const mouseY = e.clientY - rect.top;

                const currentCell = cells.find(cell => cell.contains(mouseX, mouseY));
                if (currentCell && currentCell !== startCell) {
                    selectedCells = this.getCellsBetween(startCell, currentCell, cells);

                    cells.forEach(cell => {
                        // Only select if not already part of a found word (optional, but good for clarity)
                        cell.selected = selectedCells.includes(cell);
                    });
                }
            };

            const mouseUpHandler = (e) => {
                if (!isDragging || selectedCells.length < 2) {
                    cells.forEach(cell => cell.selected = false);
                    isDragging = false;
                    startCell = null;
                    return;
                }

                const selectedWord = selectedCells.map(cell => cell.letter).join('');

                let foundWord = null;
                for (const placedWord of placedWords) {
                    if (!placedWord.found && selectedWord === placedWord.word) {
                        foundWord = placedWord;
                        break;
                    }
                }

                if (foundWord) {
                    foundWord.found = true;
                    foundWordsCount++;
                    app.gameStats.successCount++;
                    app.gameStats.totalAttempts++;
                    app.gameScoreEl.textContent = parseInt(app.gameScoreEl.textContent) + 15;
                    app.soundManager.playSound('success');

                    // نطق الكلمة عند العثور عليها
                    app.speakText(foundWord.word.toLowerCase());

                    const wordCells = this.getWordCells(foundWord, cells, gridSize, cellSize);
                    wordCells.forEach(cell => {
                        cell.highlighted = true; // Mark as permanently found
                        cell.selected = false;
                    });

                    if (foundWordsCount >= placedWords.length) {
                        setTimeout(() => {
                            app.showWinGame();
                        }, 1000);
                    }
                } else {
                    app.gameStats.totalAttempts++;
                    app.soundManager.playSound('error');
                    cells.forEach(cell => cell.selected = false);
                }

                isDragging = false;
                startCell = null;
                selectedCells = [];
                app.updateGameStats();
            };

            canvas.addEventListener('mousedown', mouseDownHandler);
            canvas.addEventListener('mousemove', mouseMoveHandler);
            canvas.addEventListener('mouseup', mouseUpHandler);

            // Touch support
            canvas.addEventListener('touchstart', (e) => {
                e.preventDefault();
                const touch = e.touches[0];
                mouseDownHandler({ clientX: touch.clientX, clientY: touch.clientY });
            }, { passive: false });

            canvas.addEventListener('touchmove', (e) => {
                e.preventDefault();
                const touch = e.touches[0];
                mouseMoveHandler({ clientX: touch.clientX, clientY: touch.clientY });
            }, { passive: false });

            canvas.addEventListener('touchend', (e) => {
                e.preventDefault();
                const touch = e.changedTouches[0];
                mouseUpHandler({ clientX: touch.clientX, clientY: touch.clientY });
            }, { passive: false });

            this.currentMouseHandlers = {
                mousedown: mouseDownHandler,
                mousemove: mouseMoveHandler,
                mouseup: mouseUpHandler
            };

            const gameLoop = () => {
                if (!app.gameRunning) return;

                if (app.isPaused) {
                    this.gameAnimationFrame = requestAnimationFrame(gameLoop);
                    return;
                }

                ctx.clearRect(0, 0, canvas.width, canvas.height);

                // Responsive Layout Calculation
                const totalWidth = canvas.width;
                const totalHeight = canvas.height;
                const isMobile = totalWidth < 600; // Mobile breakpoint

                let newCellSize, newGridOffsetX, gridOffsetY_Dynamic;

                if (isMobile) {
                    // Mobile Layout: Grid on top, List below
                    // Grid takes full width minus padding
                    const availableGridWidth = totalWidth - 20;
                    // Grid takes about 60% of height
                    const availableGridHeight = totalHeight * 0.6;

                    newCellSize = Math.min(availableGridWidth / gridSize, availableGridHeight / gridSize);
                    newCellSize = Math.min(40, Math.max(20, newCellSize)); // Cap size

                    newGridOffsetX = (totalWidth - (gridSize * newCellSize)) / 2;
                    gridOffsetY_Dynamic = 50; // Space for title
                } else {
                    // Desktop Layout: Side-by-Side
                    const gridWidthRatio = 0.75;
                    const availableGridWidth = (totalWidth * gridWidthRatio) - 10;
                    const availableGridHeight = totalHeight - gridOffsetY - 10;

                    newCellSize = Math.min(availableGridWidth / gridSize, availableGridHeight / gridSize);
                    newCellSize = Math.min(60, Math.max(25, newCellSize));

                    newGridOffsetX = 10;
                    gridOffsetY_Dynamic = gridOffsetY;
                }

                cells.forEach(cell => {
                    cell.size = newCellSize;
                    cell.x = cell.col * newCellSize + newGridOffsetX;
                    cell.y = cell.row * newCellSize + gridOffsetY_Dynamic;
                });

                // Background
                ctx.fillStyle = '#f8fafc';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                // Title
                ctx.fillStyle = '#1e293b';
                ctx.font = `bold ${Math.max(16, totalWidth / 25)}px Arial`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'top';
                ctx.fillText(`لعبة البحث عن الكلمات - الحرف ${currentLetter}`, canvas.width/2, 10);

                // Draw Grid
                cells.forEach(cell => cell.draw());

                // Draw Word List
                let listX, listY;

                if (isMobile) {
                    // List below grid
                    listX = 20;
                    listY = gridOffsetY_Dynamic + (gridSize * newCellSize) + 20;

                    ctx.textAlign = 'right'; // RTL for list
                    ctx.textBaseline = 'top';
                    ctx.fillStyle = '#334155';
                    ctx.font = 'bold 16px Arial';
                    ctx.fillText('الكلمات المطلوبة:', totalWidth - 20, listY);

                    // Draw words in a grid-like flow or columns if possible, or just a list
                    // For simplicity on mobile, let's do 2 columns
                    const colWidth = (totalWidth - 40) / 2;
                    const itemHeight = 25;

                    placedWords.forEach((word, i) => {
                        const col = i % 2;
                        const row = Math.floor(i / 2);
                        const xPos = totalWidth - 20 - (col * colWidth); // RTL flow
                        const yPos = listY + 30 + (row * itemHeight);

                        // Draw logic similar to desktop but adjusted
                        const iconSize = 12;
                        const textX = xPos - iconSize - 5;

                        if (word.found) {
                            ctx.fillStyle = '#22c55e';
                            ctx.fillText('✅', xPos, yPos);
                        } else {
                            ctx.fillStyle = '#d8b4fe';
                            ctx.fillRect(xPos - iconSize, yPos, iconSize, iconSize);
                        }

                        ctx.textAlign = 'right';
                        if (word.found) {
                            ctx.fillStyle = '#94a3b8';
                            ctx.font = 'bold 14px Arial';
                            ctx.fillText(word.word, textX, yPos);
                            const textWidth = ctx.measureText(word.word).width;
                            ctx.fillRect(textX - textWidth, yPos + 8, textWidth, 2);
                        } else {
                            ctx.fillStyle = '#1e293b';
                            ctx.font = 'bold 14px Arial';
                            ctx.fillText(word.word, textX, yPos);
                        }
                    });

                } else {
                    // Desktop List (Right Side)
                    listX = newGridOffsetX + (gridSize * newCellSize) + 15;
                    listY = gridOffsetY_Dynamic;

                    ctx.textAlign = 'left';
                    ctx.textBaseline = 'top';

                    ctx.fillStyle = '#334155';
                    ctx.font = `bold ${Math.max(12, totalWidth / 35)}px Arial`;
                    ctx.fillText('الكلمات المطلوبة:', listX, listY - 30);

                    const itemHeight = Math.max(30, newCellSize * 0.8);

                    placedWords.forEach((word, i) => {
                        const yPos = listY + i * itemHeight;
                        const iconSize = Math.max(12, itemHeight * 0.5);

                        if (word.found) {
                            ctx.fillStyle = '#22c55e';
                            ctx.font = `${iconSize}px Arial`;
                            ctx.fillText('✅', listX, yPos + (itemHeight - iconSize)/2);
                        } else {
                            ctx.fillStyle = '#d8b4fe';
                            ctx.fillRect(listX, yPos + (itemHeight - iconSize)/2, iconSize, iconSize);
                            ctx.fillStyle = 'rgba(0,0,0,0.1)';
                            ctx.fillRect(listX, yPos + (itemHeight - iconSize)/2 + iconSize/2, iconSize, iconSize/2);
                        }

                        const textX = listX + iconSize + 8;
                        const fontSize = Math.max(12, Math.min(20, (totalWidth - listX) / 8));

                        if (word.found) {
                            ctx.fillStyle = '#94a3b8';
                            ctx.font = `bold ${fontSize}px Arial`;
                            ctx.fillText(word.word, textX, yPos + itemHeight/2 - fontSize/2);
                            const textWidth = ctx.measureText(word.word).width;
                            ctx.fillRect(textX, yPos + itemHeight/2, textWidth, 2);
                        } else {
                            ctx.fillStyle = '#1e293b';
                            ctx.font = `bold ${fontSize}px Arial`;
                            ctx.fillText(word.word, textX, yPos + itemHeight/2 - fontSize/2);
                        }
                    });

                    // Progress
                    ctx.fillStyle = '#f72585';
                    ctx.font = `bold ${Math.max(12, totalWidth / 35)}px Arial`;
                    ctx.textAlign = 'center';
                    const listCenter = listX + (totalWidth - listX) / 2;
                    ctx.fillText(`الكلمات: ${foundWordsCount}/${placedWords.length}`, listCenter, listY + placedWords.length * itemHeight + 20);
                }

                this.gameAnimationFrame = requestAnimationFrame(gameLoop);
            };

            gameLoop();
        }

        canPlaceWord(grid, word, row, col, direction) {
            const wordLength = word.length;

            switch(direction) {
                case 0:
                    if (col + wordLength > grid[0].length) return false;
                    break;
                case 1:
                    if (row + wordLength > grid.length) return false;
                    break;
                case 2:
                    if (row + wordLength > grid.length || col + wordLength > grid[0].length) return false;
                    break;
            }

            for (let i = 0; i < wordLength; i++) {
                let r = row, c = col;

                switch(direction) {
                    case 0: c = col + i; break;
                    case 1: r = row + i; break;
                    case 2: r = row + i; c = col + i; break;
                }

                if (grid[r][c] !== '.' && grid[r][c] !== word[i]) {
                    return false;
                }
            }

            return true;
        }

        placeWord(grid, word, row, col, direction) {
            for (let i = 0; i < word.length; i++) {
                let r = row, c = col;

                switch(direction) {
                    case 0: c = col + i; break;
                    case 1: r = row + i; break;
                    case 2: r = row + i; c = col + i; break;
                }

                grid[r][c] = word[i];
            }
        }

        getCellsBetween(startCell, endCell, allCells) {
            const cells = [startCell];

            const rowDiff = endCell.row - startCell.row;
            const colDiff = endCell.col - startCell.col;

            if (rowDiff !== 0 && colDiff !== 0 && Math.abs(rowDiff) !== Math.abs(colDiff)) {
                return cells;
            }

            const rowStep = rowDiff === 0 ? 0 : rowDiff / Math.abs(rowDiff);
            const colStep = colDiff === 0 ? 0 : colDiff / Math.abs(colDiff);

            let currentRow = startCell.row + rowStep;
            let currentCol = startCell.col + colStep;

            while ((rowStep === 0 || (rowStep > 0 ? currentRow <= endCell.row : currentRow >= endCell.row)) &&
                   (colStep === 0 || (colStep > 0 ? currentCol <= endCell.col : currentCol >= endCell.col))) {

                const cell = allCells.find(c => c.row === currentRow && c.col === currentCol);
                if (cell) {
                    cells.push(cell);
                }

                currentRow += rowStep;
                currentCol += colStep;
            }

            return cells;
        }

        getWordCells(placedWord, allCells, gridSize, cellSize) {
            const cells = [];
            const { word, row, col, direction } = placedWord;

            for (let i = 0; i < word.length; i++) {
                let r = row, c = col;

                switch(direction) {
                    case 0: c = col + i; break;
                    case 1: r = row + i; break;
                    case 2: r = row + i; c = col + i; break;
                }

                const cell = allCells.find(cell => cell.row === r && cell.col === c);
                if (cell) {
                    cells.push(cell);
                }
            }

            return cells;
        }

        initDefaultGame(ctx, canvas) {
            const currentLetter = LETTERS[this.currentLetterIndex];

            this.gameTitle.textContent = '🎮 لعبة تعليمية';
            this.gameInstructions.textContent = 'هذه لعبة افتراضية. استمتع!';

            ctx.fillStyle = '#4361ee';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = 'white';
            ctx.font = 'bold 24px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(`لعبة ${this.getGameName(this.currentGame)}`, canvas.width / 2, canvas.height / 2 - 30);
            ctx.fillText(`الحرف ${currentLetter}`, canvas.width / 2, canvas.height / 2 + 30);
        }
    }

    window.installLettersCanvasGames = function installLettersCanvasGames(GameClass) {
        if (!GameClass || !GameClass.prototype) return;

        LETTERS = window.LETTERS || LETTERS;
        LETTER_DATA = window.LETTER_DATA || LETTER_DATA;

        Object.getOwnPropertyNames(LettersCanvasGames.prototype).forEach(name => {
            if (name !== "constructor") {
                GameClass.prototype[name] = LettersCanvasGames.prototype[name];
            }
        });
    };
})(window);
