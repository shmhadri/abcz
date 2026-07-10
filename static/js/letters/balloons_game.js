(function (window) {
    "use strict";

    const BalloonsGameMethods = {
            initBalloonsGame(ctx, canvas) {
                const currentLetter = LETTERS[this.currentLetterIndex];
                const app = this;
                
                // Responsive configuration
                const isMobile = canvas.width < 600;
                const balloonCount = isMobile ? 15 : 20;
                
                // Timer Setup
                const gameDuration = 60; // 60 seconds
                let timeLeft = gameDuration;
                let lastTime = Date.now();
                
                const balloons = [];
                for (let i = 0; i < balloonCount; i++) {
                    this.addNewBalloon(balloons, canvas, currentLetter);
                }
                
                const clickHandler = (e) => {
                    const rect = canvas.getBoundingClientRect();
                    const mouseX = e.clientX - rect.left;
                    const mouseY = e.clientY - rect.top;
                    
                    // Iterate backwards to handle overlapping balloons (top one first)
                    for (let i = balloons.length - 1; i >= 0; i--) {
                        if (balloons[i].checkClick(mouseX, mouseY)) {
                            break; // Stop after clicking one balloon
                        }
                    }
                };
                
                canvas.addEventListener('click', clickHandler);
                canvas.addEventListener('touchstart', (e) => {
                    e.preventDefault();
                    const rect = canvas.getBoundingClientRect();
                    // Use changedTouches for better touch handling
                    const touch = e.changedTouches[0] || e.touches[0];
                    const mouseX = touch.clientX - rect.left;
                    const mouseY = touch.clientY - rect.top;
                    
                    for (let i = balloons.length - 1; i >= 0; i--) {
                        if (balloons[i].checkClick(mouseX, mouseY)) {
                            break;
                        }
                    }
                }, { passive: false });

                this.currentClickHandler = clickHandler;
                
                const gameLoop = () => {
                    if (!this.gameRunning || this.isGameEnding) {
                        return;
                    }
                    
                    if (this.isPaused) {
                        this.gameAnimationFrame = requestAnimationFrame(gameLoop);
                        return;
                    }
                    
                    try {
                        // Timer Logic
                        const now = Date.now();
                        if (now - lastTime >= 1000) {
                            timeLeft--;
                            lastTime = now;
                            app.gameTimerEl.textContent = timeLeft;
                        }

                        if (timeLeft <= 0) {
                            app.showWinGame();
                            app.showToast('🎉 انتهى الوقت! أحسنت!', 3000, 'success');
                            return;
                        }

                        // Apply FPS limiting
                        const perfNow = performance.now();
                        const deltaTime = perfNow - this.lastFrameTime;
                        
                        if (deltaTime >= this.frameInterval) {
                            this.lastFrameTime = perfNow - (deltaTime % this.frameInterval);
                            
                            ctx.clearRect(0, 0, canvas.width, canvas.height);
                            
                            const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
                            gradient.addColorStop(0, '#4cc9f0');
                            gradient.addColorStop(1, '#4895ef');
                            ctx.fillStyle = gradient;
                            ctx.fillRect(0, 0, canvas.width, canvas.height);
                            
                            // Reduced cloud animation frequency for performance
                            if (Math.floor(perfNow / 200) % 2 === 0) {
                                ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
                                for (let i = 0; i < 2; i++) {
                                    const x = (perfNow/1000 * 15 + i * 120) % (canvas.width + 200) - 100;
                                    ctx.beginPath();
                                    ctx.arc(x, 100 + i * 40, 30, 0, Math.PI * 2);
                                    ctx.arc(x + 25, 90 + i * 40, 25, 0, Math.PI * 2);
                                    ctx.fill();
                                }
                            }
                            
                            // Update and draw balloons efficiently
                            for (let i = balloons.length - 1; i >= 0; i--) {
                                if (this.gameRunning && !this.isGameEnding) {
                                    const balloon = balloons[i];
                                    balloon.update();
                                    balloon.draw();
                                }
                            }
                        }
                        
                        if (this.gameRunning && !this.isGameEnding) {
                            this.gameAnimationFrame = requestAnimationFrame(gameLoop);
                        }
                    } catch (error) {
                        console.error('Error in balloon game loop:', error);
                        this.gameRunning = false;
                    }
                };
                
                gameLoop();
            },
            
            addNewBalloon(balloons, canvas, currentLetter) {
                const isCorrect = Math.random() > 0.2;
                const letter = isCorrect ? 
                    (Math.random() > 0.5 ? currentLetter : currentLetter.toLowerCase()) : 
                    LETTERS[Math.floor(Math.random() * LETTERS.length)];
                const colors = ['#f72585', '#4361ee', '#4cc9f0', '#4ade80', '#f59e0b'];
                
                const app = this; // Capture this context
                
                // Responsive size
                const isMobile = canvas.width < 600;
                const baseRadius = isMobile ? 35 : 25;

                balloons.push({
                    x: Math.random() * canvas.width,
                    y: canvas.height + Math.random() * 100,
                    radius: baseRadius + Math.random() * 20,
                    speed: 2 + Math.random() * 3,
                    color: colors[Math.floor(Math.random() * colors.length)],
                    letter: letter,
                    isCorrect: isCorrect || letter.toLowerCase() === currentLetter.toLowerCase(),
                    popped: false,
                    popTime: 0,
                    draw: function() {
                        // Same draw function as before
                        const ctx = canvas.getContext('2d');
                        if (this.popped) {
                            ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
                            for (let i = 0; i < 8; i++) {
                                const angle = (i / 8) * Math.PI * 2;
                                const distance = this.radius * 1.5;
                                ctx.beginPath();
                                ctx.arc(
                                    this.x + Math.cos(angle) * distance,
                                    this.y + Math.sin(angle) * distance,
                                    5,
                                    0,
                                    Math.PI * 2
                                );
                                ctx.fill();
                            }
                            return;
                        }
                        
                        ctx.fillStyle = this.color;
                        ctx.beginPath();
                        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                        ctx.fill();
                        
                        ctx.strokeStyle = this.color;
                        ctx.lineWidth = 2;
                        ctx.beginPath();
                        ctx.moveTo(this.x, this.y + this.radius);
                        ctx.lineTo(this.x, this.y + this.radius + 30);
                        ctx.stroke();
                        
                        ctx.fillStyle = 'white';
                        ctx.font = `bold ${Math.floor(this.radius * 0.8)}px Arial`;
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillText(this.letter, this.x, this.y);
                    },
                    update: function() {
                        if (this.popped) {
                            this.popTime++;
                            if (this.popTime > 30) {
                                const index = balloons.indexOf(this);
                                if (index > -1) {
                                    balloons.splice(index, 1);
                                    app.addNewBalloon(balloons, canvas, currentLetter);
                                }
                            }
                            return;
                        }
                        
                        this.y -= this.speed;
                        
                        // Handle resize
                        if (this.x > canvas.width) this.x = Math.random() * canvas.width;
                        
                        if (this.y < -this.radius) {
                            const index = balloons.indexOf(this);
                            if (index > -1) {
                                balloons.splice(index, 1);
                                app.addNewBalloon(balloons, canvas, currentLetter);
                            }
                        }
                    },
                    checkClick: function(mouseX, mouseY) {
                        if (this.popped) return false;
                        
                        const dx = mouseX - this.x;
                        const dy = mouseY - this.y;
                        const distance = Math.sqrt(dx * dx + dy * dy);
                        
                        // Increased hit area slightly (radius * 1.2) for better touch
                        if (distance < this.radius * 1.2) {
                            this.popped = true;
                            
                            if (this.isCorrect) {
                                // Chain Reaction: Pop all balloons with the same letter
                                let extraPopped = 0;
                                balloons.forEach(b => {
                                    if (!b.popped && b.letter === this.letter && b !== this) {
                                        b.popped = true;
                                        extraPopped++;
                                    }
                                });
                                
                                app.gameStats.successCount += (1 + extraPopped);
                                app.gameStats.totalAttempts++;
                                app.gameScoreEl.textContent = parseInt(app.gameScoreEl.textContent) + 10 + (extraPopped * 5);
                                app.soundManager.playSound('success');
                                
                                // Win condition: 16 correct pops
                                if (app.gameStats.successCount >= 16) {
                                    app.showWinGame();
                                    app.showToast('🎉 أحسنت! لقد فجرت 16 بالوناً صحيحاً!', 3000, 'success');
                                    return true;
                                }
                            } else {
                                app.gameStats.totalAttempts++;
                                app.gameScoreEl.textContent = Math.max(0, parseInt(app.gameScoreEl.textContent) - 5);
                                app.soundManager.playSound('error');
                            }
                            
                            app.updateGameStats();
                            return true;
                        }
                        return false;
                    }
                });
            }
    };

    window.installLettersBalloonsGame = function installLettersBalloonsGame(GameClass) {
        if (!GameClass || !GameClass.prototype) return;
        Object.assign(GameClass.prototype, BalloonsGameMethods);
    };
})(window);
