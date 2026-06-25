(function (window) {
    "use strict";

    const MatchGameMethods = {
            initMatchGame(ctx, canvas) {
                const currentLetter = LETTERS[this.currentLetterIndex];
                const letterData = LETTER_DATA[currentLetter];
                const app = this;
                
                const letters = [];
                const words = [];
                const matches = [];
                
                // Responsive layout calculation
                const isMobile = canvas.width < 600;
                const letterWidth = isMobile ? 40 : Math.min(50, canvas.width * 0.15);
                const wordWidth = isMobile ? canvas.width * 0.5 : Math.min(150, canvas.width * 0.45);
                
                const letterX = isMobile ? 10 : canvas.width * 0.1;
                const wordX = isMobile ? canvas.width - wordWidth - 10 : canvas.width * 0.5;
                
                for (let i = 0; i < 6; i++) {
                    letters.push({
                        id: i,
                        letter: i % 2 === 0 ? currentLetter : currentLetter.toLowerCase(),
                        x: letterX,
                        y: 100 + i * (isMobile ? 50 : 60),
                        width: letterWidth,
                        height: isMobile ? 40 : 50,
                        dragging: false,
                        matched: false,
                        draw: function() {
                            ctx.fillStyle = this.matched ? '#4ade80' : '#4361ee';
                            ctx.fillRect(this.x, this.y, this.width, this.height);
                            
                            ctx.fillStyle = 'white';
                            ctx.font = isMobile ? 'bold 24px Arial' : 'bold 30px Arial';
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'middle';
                            ctx.fillText(this.letter, this.x + this.width/2, this.y + this.height/2);
                        },
                        contains: function(x, y) {
                            return x >= this.x && x <= this.x + this.width &&
                                   y >= this.y && y <= this.y + this.height;
                        }
                    });
                }
                
                letterData.words.forEach((wordData, i) => {
                    if (i < 6) {
                        words.push({
                            id: i,
                            word: wordData.word,
                            translation: wordData.translation,
                            x: wordX,
                            y: 100 + i * (isMobile ? 50 : 60),
                            width: wordWidth,
                            height: isMobile ? 40 : 50,
                            matched: false,
                            draw: function() {
                                ctx.fillStyle = this.matched ? '#4ade80' : '#f59e0b';
                                ctx.fillRect(this.x, this.y, this.width, this.height);
                                
                                ctx.fillStyle = 'white';
                                ctx.font = isMobile ? 'bold 16px Arial' : 'bold 18px Arial';
                                ctx.textAlign = 'center';
                                ctx.textBaseline = 'middle';
                                
                                const lines = this.wrapText(ctx, this.word, this.width - 10);
                                lines.forEach((line, idx) => {
                                    ctx.fillText(
                                        line,
                                        this.x + this.width/2,
                                        this.y + this.height/2 + (idx - (lines.length-1)/2) * (isMobile ? 16 : 20)
                                    );
                                });
                                
                                // Hide translation on very small screens if matched to save space, or keep it small
                                if (!isMobile || !this.matched) {
                                    ctx.fillStyle = '#cbd5e1';
                                    ctx.font = isMobile ? '10px Arial' : '12px Arial';
                                    ctx.fillText(this.translation, this.x + this.width/2, this.y + this.height + (isMobile ? 10 : 15));
                                }
                            },
                            wrapText: function(ctx, text, maxWidth) {
                                const words = text.split(' ');
                                const lines = [];
                                let currentLine = words[0];
                                
                                for (let i = 1; i < words.length; i++) {
                                    const word = words[i];
                                    const width = ctx.measureText(currentLine + " " + word).width;
                                    if (width < maxWidth) {
                                        currentLine += " " + word;
                                    } else {
                                        lines.push(currentLine);
                                        currentLine = word;
                                    }
                                }
                                lines.push(currentLine);
                                return lines;
                            },
                            contains: function(x, y) {
                                return x >= this.x && x <= this.x + this.width &&
                                       y >= this.y && y <= this.y + this.height;
                            }
                        });
                    }
                });
                
                let draggedLetter = null;
                let offsetX = 0, offsetY = 0;
                
                const mouseDownHandler = (e) => {
                    const rect = canvas.getBoundingClientRect();
                    const mouseX = e.clientX - rect.left;
                    const mouseY = e.clientY - rect.top;
                    
                    for (const letter of letters) {
                        if (!letter.matched && letter.contains(mouseX, mouseY)) {
                            draggedLetter = letter;
                            draggedLetter.dragging = true;
                            offsetX = mouseX - letter.x;
                            offsetY = mouseY - letter.y;
                            break;
                        }
                    }
                };
                
                const mouseMoveHandler = (e) => {
                    if (!draggedLetter) return;
                    
                    const rect = canvas.getBoundingClientRect();
                    const mouseX = e.clientX - rect.left;
                    const mouseY = e.clientY - rect.top;
                    
                    draggedLetter.x = mouseX - offsetX;
                    draggedLetter.y = mouseY - offsetY;
                };
                
                const mouseUpHandler = (e) => {
                    if (!draggedLetter) return;
                    
                    const rect = canvas.getBoundingClientRect();
                    const mouseX = e.clientX - rect.left;
                    const mouseY = e.clientY - rect.top;
                    
                    let matchedWord = null;
                    for (const word of words) {
                        if (!word.matched && word.contains(mouseX, mouseY)) {
                            if (word.word.startsWith(draggedLetter.letter.toUpperCase()) || 
                                word.word.toLowerCase().startsWith(draggedLetter.letter.toLowerCase())) {
                                matchedWord = word;
                                break;
                            }
                        }
                    }
                    
                    if (matchedWord) {
                        draggedLetter.matched = true;
                        matchedWord.matched = true;
                        
                        draggedLetter.x = matchedWord.x - 60;
                        draggedLetter.y = matchedWord.y;
                        
                        matches.push({
                            fromX: draggedLetter.x + draggedLetter.width,
                            fromY: draggedLetter.y + draggedLetter.height/2,
                            toX: matchedWord.x,
                            toY: matchedWord.y + matchedWord.height/2
                        });
                        
                        app.gameStats.successCount++;
                        app.gameStats.totalAttempts++;
                        app.gameScoreEl.textContent = parseInt(app.gameScoreEl.textContent) + 10;
                        app.soundManager.playSound('success');
                        
                        // نطق الكلمة عند المطابقة
                        app.speakText(matchedWord.word.toLowerCase());
                        
                        // التحقق من الفوز: إذا تم مطابقة 5 كلمات أو أكثر
                        const matchedCount = letters.filter(l => l.matched).length;
                        if (matchedCount >= 5) {
                            setTimeout(() => {
                                app.showWinGame();
                            }, 1000);
                        }
                    } else {
                        const originalIndex = letters.findIndex(l => l.id === draggedLetter.id);
                        draggedLetter.x = 100;
                        draggedLetter.y = 100 + originalIndex * 60;
                        app.soundManager.playSound('error');
                    }
                    
                    draggedLetter.dragging = false;
                    draggedLetter = null;
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
                    
                    // Responsive update
                    const letterX = canvas.width * 0.1;
                    const letterWidth = Math.min(50, canvas.width * 0.15);
                    const wordX = canvas.width * 0.5;
                    const wordWidth = Math.min(150, canvas.width * 0.45);
                    
                    letters.forEach(letter => {
                        if (!letter.dragging && !letter.matched) {
                            letter.x = letterX;
                            letter.width = letterWidth;
                        } else if (letter.matched) {
                            // Keep matched letters relative to words
                            // We need to find the matched word to position correctly, 
                            // but simpler is to just let them stay where they were placed relative to the word
                            // If word moves, letter should move too.
                            // But we don't have a link back to the word easily here without searching.
                            // For now, let's just update width.
                            letter.width = letterWidth;
                        }
                    });
                    
                    words.forEach(word => {
                        word.x = wordX;
                        word.width = wordWidth;
                    });

                    ctx.fillStyle = '#f8fafc';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    
                    ctx.fillStyle = '#1e293b';
                    ctx.font = 'bold 24px Arial';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'top';
                    ctx.fillText(`لعبة المطابقة - الحرف ${currentLetter}`, canvas.width/2, 10);
                    
                    ctx.fillStyle = '#475569';
                    ctx.font = '16px Arial';
                    ctx.fillText('اسحب الحرف إلى الكلمة التي تبدأ به', canvas.width/2, 40);
                    
                    ctx.strokeStyle = '#4cc9f0';
                    ctx.lineWidth = 3;
                    matches.forEach(match => {
                        ctx.beginPath();
                        ctx.moveTo(match.fromX, match.fromY);
                        ctx.lineTo(match.toX, match.toY);
                        ctx.stroke();
                    });
                    
                    words.forEach(word => word.draw());
                    
                    letters.forEach(letter => letter.draw());
                    
                    this.gameAnimationFrame = requestAnimationFrame(gameLoop);
                };
                
                gameLoop();
            }
    };

    window.installLettersMatchGame = function installLettersMatchGame(GameClass) {
        if (!GameClass || !GameClass.prototype) return;
        Object.assign(GameClass.prototype, MatchGameMethods);
    };
})(window);
