/**
 * Top Goal - Audio JavaScript
 * معالجة الصوتيات والنطق
 */

function initAudio() {
    console.log('🔊 Initializing audio...');
    // Audio initialization if needed
}

function speakText(text, lang = 'en-US') {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = lang;
        utterance.rate = 0.9;
        window.speechSynthesis.speak(utterance);
    } else {
        console.warn('⚠️ Speech synthesis not supported');
    }
}

function playSound(soundUrl) {
    const audio = new Audio(soundUrl);
    audio.play().catch(err => {
        console.error('Error playing sound:', err);
    });
}

// Sentence Audio
function playSentence(text) {
    speakText(text, 'en-US');
}

// Word Audio
function playWord(word) {
    speakText(word, 'en-US');
}

// Expose functions globally
window.initAudio = initAudio;
window.speakText = speakText;
window.playSound = playSound;
window.playSentence = playSentence;
window.playWord = playWord;
