/**
 * Top Goal - Lesson 2 & 3 JavaScript
 * Logic for Past Progressive Grammar & Exercises
 */

console.log('📘 Lesson 2 Script Starting...');

// --- State Management ---
const lesson2State = {
    ex2: { answered: 0, score: 0, total: 3 },
    ex3: { matches: {}, score: 0, total: 4 },
    ex4: { answered: 0, score: 0, total: 9 }, // 9 gaps in the dialogue
    ex5: { answered: 0, score: 0, total: 5 },
    pronunciation: { score: 0, attempts: 0 }
};

// --- Safety Helpers ---
let warned = false;
function warnOnce(msg) {
  if (warned) return;
  warned = true;
  console.warn(msg);
}

function safeSetText(selector, value) {
  const el = document.querySelector(selector);
  if (!el) return false;
  el.textContent = value;
  return true;
}

function safeSetElementText(el, value) {
    if (!el) return false;
    el.textContent = value;
    return true;
}
// ----------------------

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    console.log('✅ DOM Content Loaded for Lesson 2');
    initDragAndDrop();
    initSpeechRecognition();
});

// --- Exercise 1: Read and Circle (Was/Were) ---
window.checkCircleAnswer = function(btn, isCorrect) {
    console.log('checkCircleAnswer called', isCorrect);
    const parent = btn.parentElement;
    const allBtns = parent.querySelectorAll('.circle-btn');
    
    // Disable siblings
    allBtns.forEach(b => b.classList.remove('selected', 'correct', 'wrong'));
    
    btn.classList.add('selected');

    if (isCorrect) {
        btn.classList.add('correct');
        // Avoid duplicate checkmarks
        if (!btn.innerText.includes('✅')) {
             btn.innerHTML += ' ✅';
        }
        playSound('correct');
        // Disable all
        allBtns.forEach(b => b.disabled = true);
    } else {
        btn.classList.add('wrong');
        if (!btn.innerText.includes('❌')) {
            btn.innerHTML += ' ❌';
        }
        playSound('wrong');
    }
}

// Wrapper for checking overall Ex1 status
window.checkGrammarEx1 = function() {
    console.log('checkGrammarEx1 called');
    const correct = document.querySelectorAll('#grammar-ex1-container .correct').length;
    const feedback = document.getElementById('grammar-ex1-feedback');
    if(feedback) {
        feedback.style.display = 'block';
        // Checking for 5 questions
        if (correct === 5) {
            feedback.className = 'alert success';
            feedback.innerHTML = '🎉 Amazing! You got 5/5 correct!';
            playSound('cheer');
        } else {
            feedback.className = 'alert warning';
            feedback.innerHTML = `⚠️ You got ${correct}/5 correct. Try again!`;
        }
    }
}

// --- Exercise 3: MCQ ---
window.checkMcqAnswer = function(btn, isCorrect) {
    console.log('checkMcqAnswer called', isCorrect);
    const parent = btn.parentElement;
    const buttons = parent.querySelectorAll('.mcq-btn');
    buttons.forEach(b => b.disabled = true);
    
    if (isCorrect) {
        btn.style.background = '#10b981';
        btn.style.color = 'white';
        btn.style.borderColor = '#10b981';
        if (!btn.innerText.includes('✔️')) {
            btn.innerHTML += ' ✔️';
        }
        playSound('correct');
    } else {
        btn.style.background = '#ef4444';
        btn.style.color = 'white';
        btn.style.borderColor = '#ef4444';
         if (!btn.innerText.includes('❌')) {
            btn.innerHTML += ' ❌';
        }
        playSound('wrong');
    }
}

// --- Exercise 2: Clickable Sentence Builder Logic ---

window.moveWord = function(btn, targetId) {
    console.log('moveWord called', targetId);
    const currentContainer = btn.parentElement;
    const targetContainer = document.getElementById(targetId);
    
    if (!currentContainer || !targetContainer) {
        console.error('Container not found');
        return;
    }

    // If currently in bank, move to answer zone
    if (currentContainer.classList.contains('word-bank')) {
        targetContainer.appendChild(btn);
        btn.classList.add('in-answer');
        playSound('click'); 
    } 
    // If currently in answer zone, move BACK to specific bank
    else if (currentContainer.classList.contains('answer-zone')) {
        // Find the corresponding bank. ID format: answer-X -> bank-X
        const bankId = targetId.replace('answer', 'bank');
        const bank = document.getElementById(bankId);
        if(bank) {
            bank.appendChild(btn);
            btn.classList.remove('in-answer');
            playSound('click');
        }
    }
}

window.resetScramble = function(id, wordsArray) {
    console.log('resetScramble called');
    const bank = document.getElementById(`bank-${id}`);
    const answer = document.getElementById(`answer-${id}`);
    
    if (!bank || !answer) return;

    // Move all buttons back to bank
    const buttons = answer.querySelectorAll('.word-chip');
    buttons.forEach(btn => {
        bank.appendChild(btn);
        btn.classList.remove('in-answer');
    });
    
    // Clear validation styles
    answer.style.borderColor = '#cbd5e1';
    answer.style.backgroundColor = 'white';
}

window.checkScrambleAnswers = function() {
    console.log('checkScrambleAnswers called');
    let correctCount = 0;
    
    // Hardcoded answers
    const answers = [
        "he was watching tv",
        "they were playing tennis",
        "she was reading a book",
        "we were cooking dinner",
        "i was doing homework"
    ]; // 5 sentences
    
    for (let i = 1; i <= 5; i++) {
        const answerZone = document.getElementById(`answer-${i}`);
        if(answerZone) {
            // Get text of buttons in order
            const userWords = Array.from(answerZone.querySelectorAll('.word-chip')).map(b => b.innerText.toLowerCase());
            const userSentence = userWords.join(' ');
            
            if (userSentence === answers[i-1]) {
                answerZone.style.borderColor = '#10b981';
                answerZone.style.backgroundColor = '#d1fae5';
                correctCount++;
            } else {
                answerZone.style.borderColor = '#ef4444';
                answerZone.style.backgroundColor = '#fee2e2';
            }
        }
    }

    if (correctCount === 5) {
        playSound('cheer');
    } else {
        playSound('wrong');
    }
}

// --- Exercise 4: Read and Match (Drag & Drop) ---
function initDragAndDrop() {
    const draggables = document.querySelectorAll('.draggable-item');
    const droppables = document.querySelectorAll('.drop-zone');

    draggables.forEach(draggable => {
        draggable.addEventListener('dragstart', () => {
            draggable.classList.add('dragging');
        });

        draggable.addEventListener('dragend', () => {
            draggable.classList.remove('dragging');
        });
    });

    droppables.forEach(zone => {
        zone.addEventListener('dragover', e => {
            e.preventDefault();
            const dragging = document.querySelector('.dragging');
            if(dragging) zone.classList.add('drag-over');
        });

        zone.addEventListener('dragleave', () => {
            zone.classList.remove('drag-over');
        });

        zone.addEventListener('drop', e => {
            e.preventDefault();
            zone.classList.remove('drag-over');
            const dragging = document.querySelector('.dragging');
            
            if (dragging) {
                // Check if match is correct
                const expected = zone.getAttribute('data-match');
                const actual = dragging.getAttribute('data-id');
                
                if (expected === actual) {
                    zone.appendChild(dragging);
                    dragging.draggable = false;
                    dragging.classList.add('matched');
                    zone.classList.add('solved');
                    playSound('correct');
                } else {
                    playSound('wrong');
                    dragging.classList.add('shake');
                    setTimeout(() => dragging.classList.remove('shake'), 500);
                }
            }
        });
    });
}

// --- Exercise 5: Read and Complete (Dialogue) ---
window.checkDialogue = function() {
    const inputs = document.querySelectorAll('.dialogue-input, .dialogue-select');
    let correctCount = 0;
    
    inputs.forEach(input => {
        const expected = input.getAttribute('data-answer').toLowerCase();
        const value = input.value.trim().toLowerCase();

        if (value === expected) {
            input.classList.add('correct');
            input.classList.remove('wrong');
            correctCount++;
        } else {
            input.classList.add('wrong');
            input.classList.remove('correct');
        }
    });

    const feedback = document.getElementById('ex4-feedback');
    if (correctCount === inputs.length) {
        feedback.innerHTML = '<div class="alert success">🎉 Amazing! Perfect conversation!</div>';
        playSound('cheer');
    } else {
        feedback.innerHTML = '<div class="alert warning">⚠️ Keep trying! Check the red boxes.</div>';
        playSound('wrong');
    }
}

// --- Exercise 6: Look, Find, and Write ---
window.checkSentence = function(id, expectedKeyWords) {
    const input = document.getElementById(`ex5-input-${id}`);
    const feedback = document.getElementById(`ex5-feedback-${id}`);
    const userText = input.value.toLowerCase().trim();
    
    const missing = expectedKeyWords.filter(word => !userText.includes(word));

    if (missing.length === 0) {
        input.classList.add('correct');
        input.classList.remove('wrong');
        if(feedback) {
             safeSetElementText(feedback, '✅ Correct! Excellent grammar.');
             feedback.className = 'feedback-text success';
        }
        playSound('correct');
    } else {
        input.classList.add('wrong');
        input.classList.remove('correct');
        if(feedback) {
             safeSetElementText(feedback, `⚠️ Try again. Make sure to use: ${expectedKeyWords.join(', ')}`);
             feedback.className = 'feedback-text warning';
        }
        playSound('wrong');
    }
}

// --- Speech Recognition ---
let recognition;
let isRecording = false;

function initSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            handleSpeechResult(transcript);
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error', event.error);
            isRecording = false;
            updateMicButton('error');
        };

        recognition.onend = () => {
            isRecording = false;
            updateMicButton('idle');
        };
    } else {
        console.warn('Speech Recognition not supported');
        const micBtn = document.getElementById('mic-button');
        if(micBtn) micBtn.style.display = 'none';
    }
}

window.toggleRecording = function(targetPhrase) {
    if (!recognition) return;
    
    if (isRecording) {
        recognition.stop();
        return;
    }

    window.currentTargetPhrase = targetPhrase;
    
    recognition.start();
    isRecording = true;
    updateMicButton('recording');
}

function updateMicButton(state) {
    const btn = document.getElementById('mic-button');
    if (!btn) return;
    
    if (state === 'recording') {
        btn.classList.add('recording');
        btn.innerHTML = '<i class="fas fa-stop"></i> Listening...';
    } else if (state === 'idle') {
        btn.classList.remove('recording');
        btn.innerHTML = '<i class="fas fa-microphone"></i> Press to Speak';
    } else if (state === 'error') {
        btn.classList.remove('recording');
        btn.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Error';
    }
}

function handleSpeechResult(transcript) {
    const feedback = document.getElementById('speech-feedback');
    const target = window.currentTargetPhrase.toLowerCase();
    const spoken = transcript.toLowerCase();
    
    if (spoken.includes(target) || target.includes(spoken)) {
        feedback.innerHTML = `
            <div class="speech-result success">
                <strong>You said:</strong> "${transcript}"<br>
                ✅ Perfect Pronunciation! 🌟
            </div>
        `;
        playSound('correct');
    } else {
        feedback.innerHTML = `
            <div class="speech-result warning">
                <strong>You said:</strong> "${transcript}"<br>
                ⚠️ Try again! Target: "${window.currentTargetPhrase}"
            </div>
        `;
        playSound('wrong');
    }
}

// --- Audio Helper ---
window.speakText = function(text) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-GB'; 
        window.speechSynthesis.speak(utterance);
    }
}

window.playSound = function(type) {
    const audio = document.getElementById(`sfx-${type}`);
    if (audio) {
        audio.currentTime = 0;
        audio.play().catch(e => console.log('Audio play blocked', e));
    }
}

console.log('📘 Lesson 2 Script Loaded & Global Functions Attached');
