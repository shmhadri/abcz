/**
 * Top Goal - Games JavaScript
 * منطق الألعاب وإصلاح القوائم المنسدلة
 */

// ============================================
// FIX: Game Tabs Initialization
// ============================================
function initGameTabs() {
    console.log('🎮 Initializing game tabs...');
    
    const gameTabs = document.querySelectorAll('.game-tab');
    const gamePanels = document.querySelectorAll('.game-panel');
    
    if (gameTabs.length === 0) {
        console.warn('⚠️ No game tabs found!');
        return;
    }
    
    // Add click handlers to ALL game tabs
    gameTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            console.log(`🎯 Clicked tab: ${this.dataset.game}`);
            
            // Remove active from all tabs
            gameTabs.forEach(t => t.classList.remove('active'));
            
            // Hide all game panels
            gamePanels.forEach(panel => panel.classList.remove('active'));
            
            // Activate clicked tab
            this.classList.add('active');
            
            // Show corresponding game panel
            const gameId = this.dataset.game;
            const targetPanel = document.getElementById(gameId);
            
            if (targetPanel) {
                targetPanel.classList.add('active');
                console.log(`✅ Activated panel: ${gameId}`);
                
                // Initialize game if needed
                initializeGame(gameId);
            } else {
                console.error(`❌ Panel not found: ${gameId}`);
            }
        });
    });
    
    console.log(`✅ Game tabs initialized: ${gameTabs.length} tabs`);
}

function initializeGame(gameId) {
    switch(gameId) {
        case 'memory-game':
            if (typeof initMemoryGame === 'function') {
                initMemoryGame();
            }
            break;
        case 'scramble-game':
            if (typeof initScrambleGame === 'function') {
                initScrambleGame();
            }
            break;
        case 'listening-game':
            if (typeof initListeningGame === 'function') {
                initListeningGame();
            }
            break;
        case 'picture-game':
            if (typeof initPictureGame === 'function') {
                initPictureGame();
            }
            break;
        case 'gap-game':
            if (typeof initGapFillGame === 'function') {
                initGapFillGame();
            }
            break;
        case 'missing-game':
            if (typeof initMissingLettersGame === 'function') {
                initMissingLettersGame();
            }
            break;
    }
}

// ============================================
// Memory Game
// ============================================
const memoryData = [
    {en: "movie", ar: "فيلم", emoji: "🎬"},
    {en: "watch", ar: "يشاهد", emoji: "👀"},
    {en: "comedy", ar: "كوميديا", emoji: "😄"},
    {en: "action", ar: "حركة", emoji: "💥"},
    {en: "adventure", ar: "مغامرة", emoji: "🗺️"},
    {en: "ability", ar: "قدرة", emoji: "⚡"}
];

let flippedCards = [];
let matchedPairs = 0;

function initMemoryGame() {
    console.log('🧠 Initializing memory game...');
    
    const grid = document.getElementById('memory-grid');
    const feedback = document.getElementById('memory-feedback');
    
    if (!grid) {
        console.warn('⚠️ Memory grid not found');
        return;
    }
    
    grid.innerHTML = '';
    feedback.textContent= '';
    flippedCards = [];
    matchedPairs = 0;

    // Create pairs (English + Arabic for each word)
    let cards = [];
    memoryData.forEach(item => {
        cards.push({type: 'en', word: item.en, match: item.ar});
        cards.push({type: 'ar', word: item.ar, match: item.en});
    });
    
    // Shuffle cards
    cards = shuffle(cards);

    cards.forEach((card, index) => {
        const cardDiv = document.createElement('div');
        cardDiv.className = 'memory-card';
        cardDiv.dataset.index = index;
        cardDiv.dataset.word = card.word;
        cardDiv.dataset.match = card.match;
        
        cardDiv.innerHTML = `
            <div class="front">❓</div>
            <div class="back">${card.word}</div>
        `;
        
        cardDiv.addEventListener('click', () => flipCard(cardDiv));
        grid.appendChild(cardDiv);
    });
    
    console.log('✅ Memory game ready!');
}

function flipCard(card) {
    if (card.classList.contains('flip') || card.classList.contains('matched') || flippedCards.length >= 2) {
        return;
    }

    card.classList.add('flip');
    flippedCards.push(card);

    if (flippedCards.length === 2) {
        setTimeout(checkMatch, 600);
    }
}

function checkMatch() {
    const [card1, card2] = flippedCards;
    const feedback = document.getElementById('memory-feedback');
    
    const word1 = card1.dataset.word;
    const match1 = card1.dataset.match;
    const word2 = card2.dataset.word;

    if (word1 === match1 && word2 === match1) {
        // Match found
        card1.classList.add('matched');
        card2.classList.add('matched');
        matchedPairs++;
        
        feedback.textContent = '✅ Match! - تطابق!';
        feedback.style.color = '#22c55e';
        
        if (typeof addPoints === 'function') {
            addPoints(10);
        }

        if (matchedPairs === memoryData.length) {
            setTimeout(() => {
                feedback.textContent = '🎉 You won! - فزت!';
                if (typeof addPoints === 'function') {
                    addPoints(50);
                }
            }, 500);
        }
    } else {
        // No match
        feedback.textContent = '❌ Try again - حاول مرة أخرى';
        feedback.style.color = '#ef4444';
        
        setTimeout(() => {
            card1.classList.remove('flip');
            card2.classList.remove('flip');
        }, 800);
    }

    flippedCards = [];
}

// ============================================
// Wheel Game
// ============================================
function spinWheel() {
    const genres = ['Action 💥', 'Comedy 😄', 'Adventure 🗺️', 'Superhero 🦸'];
    const result = genres[Math.floor(Math.random() * genres.length)];
    const wheelResult = document.getElementById('wheel-result');
    
    if (wheelResult) {
        wheelResult.textContent = result;
        if (typeof addPoints === 'function') {
            addPoints(5);
        }
    }
}

// ============================================
// Gap Fill Game
// ============================================
const gapSentences = [
    {
        sentence: "She ___ watching a movie.",
        sentenceAr: "هي كانت تشاهد فيلماً",
        options: ["was", "were", "is"],
        correct: "was"
    },
    {
        sentence: "They ___ playing football.",
        sentenceAr: "هم كانوا يلعبون كرة القدم",
        options: ["was", "were", "is"],
        correct: "were"
    },
    {
        sentence: "I ___ reading a book.",
        sentenceAr: "أنا كنت أقرأ كتاباً",
        options: ["was", "were", "am"],
        correct: "was"
    }
];

let currentGapIndex = 0;

function initGapFillGame() {
    if (currentGapIndex >= gapSentences.length) {
        currentGapIndex = 0;
    }
    
    const current = gapSentences[currentGapIndex];
    const sentenceBox = document.getElementById('gap-sentence');
    const sentenceArBox = document.getElementById('gap-sentence-ar');
    const optionsBox = document.getElementById('gap-options');
    const feedback = document.getElementById('gap-feedback');
    
    if (!sentenceBox || !optionsBox) return;
    
    sentenceBox.innerHTML = current.sentence.replace('___', '<span style="color:#f72585; font-weight:900;">___</span>');
    sentenceArBox.textContent = current.sentenceAr;
    feedback.textContent = '';
    optionsBox.innerHTML = '';
    
    current.options.forEach(option => {
        const btn = document.createElement('button');
        btn.className = 'spin-btn';
        btn.textContent = option;
        btn.style.fontSize = '1.5rem';
        btn.style.padding = '15px 40px';
        btn.onclick = () => checkGapAnswer(option, current.correct, btn);
        optionsBox.appendChild(btn);
    });
    
    currentGapIndex++;
}

function checkGapAnswer(selected, correct, btn) {
    const feedback = document.getElementById('gap-feedback');
    const allBtns = document.querySelectorAll('#gap-options button');
    
    allBtns.forEach(b => b.disabled = true);
    
    if (selected === correct) {
        feedback.textContent = '✅ Correct! - صحيح!';
        feedback.style.color = '#22c55e';
        btn.style.background = 'linear-gradient(to right, #22c55e, #16a34a)';
        if (typeof addPoints === 'function') {
            addPoints(10);
        }
    } else {
        feedback.textContent = '❌ Wrong! - خطأ!';
        feedback.style.color = '#ef4444';
        btn.style.background = 'linear-gradient(to right, #ef4444, #dc2626)';
    }
}

// ============================================
// Missing Letters Game
// ============================================
const missingWords = [
    {word: "movie", hint: "🎬", ar: "فيلم", missing: 1}, // m_ovie -> o
    {word: "watch", hint: "👀", ar: "يشاهد", missing: 1}, // w_atch -> a
    {word: "comedy", hint: "😄", ar: "كوميديا", missing: 2}, // co_medy -> m
    {word: "action", hint: "💥", ar: "حركة", missing: 0} // _action -> a
];

let currentMissingIndex = 0;

function initMissingLettersGame() {
    if (currentMissingIndex >= missingWords.length) {
        currentMissingIndex = 0;
    }
    
    const current = missingWords[currentMissingIndex];
    const wordBox = document.getElementById('missing-word');
    const arabicBox = document.getElementById('missing-arabic');
    const emojiBox = document.getElementById('missing-emoji');
    const optionsBox = document.getElementById('missing-options');
    const feedback = document.getElementById('missing-feedback');
    
    if (!wordBox || !optionsBox) return;
    
    // Display word with missing letter
    const missingIndex = current.missing;
    const displayWord = current.word.split('').map((letter, i) => 
        i === missingIndex ? '_' : letter
    ).join('');
    
    wordBox.textContent = displayWord.toUpperCase();
    arabicBox.textContent = current.ar;
    emojiBox.textContent = current.hint;
    feedback.textContent = '';
    optionsBox.innerHTML = '';
    
    // Create letter options (correct + 2 random)
    const correctLetter = current.word[missingIndex];
    const wrongLetters = ['a', 'e', 'i', 'o', 'u', 'b', 'c', 'd', 'f', 'g'].filter(l => l !== correctLetter);
    const options = shuffle([correctLetter, wrongLetters[0], wrongLetters[1]]);
    
    options.forEach(letter => {
        const btn = document.createElement('button');
        btn.className = 'spin-btn';
        btn.textContent = letter.toUpperCase();
        btn.style.fontSize = '2rem';
        btn.style.width = '80px';
        btn.style.height = '80px';
        btn.onclick = () => checkMissingLetter(letter, correctLetter, btn);
        optionsBox.appendChild(btn);
    });
    
    currentMissingIndex++;
}

function checkMissingLetter(selected, correct, btn) {
    const feedback = document.getElementById('missing-feedback');
    const allBtns = document.querySelectorAll('#missing-options button');
    
    allBtns.forEach(b => b.disabled = true);
    
    if (selected === correct) {
        feedback.textContent = '✅ Excellent! - ممتاز!';
        feedback.style.color = '#22c55e';
        btn.style.background = 'linear-gradient(to right, #22c55e, #16a34a)';
        if (typeof addPoints === 'function') {
            addPoints(15);
        }
    } else {
        feedback.textContent = '❌ Try again! - حاول مرة أخرى!';
        feedback.style.color = '#ef4444';
        btn.style.background = 'linear-gradient(to right, #ef4444, #dc2626)';
    }
}

// Expose functions globally
window.initGameTabs = initGameTabs;
window.initMemoryGame = initMemoryGame;
window.flipCard = flipCard;
window.spinWheel = spinWheel;
window.initGapFillGame = initGapFillGame;
window.checkGapAnswer = checkGapAnswer;
window.initMissingLettersGame = initMissingLettersGame;
window.checkMissingLetter = checkMissingLetter;
