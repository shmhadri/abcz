/**
 * Top Goal - Main JavaScript
 * التهيئة الرئيسية والمتغيرات العامة
 */

// Global Variables
let score = 0;
let reviewScore = 0;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎮 Top Goal - Initializing...');
    
    // Initialize all components
    initLessonNavigation();
    initGameTabs();
    initMemoryGame();
    initQuizzes();
    initAudio();
    
    console.log('✅ Top Goal - Ready!');
});

// Score Management
function addPoints(points) {
    score += points;
    updateScoreDisplay();
    showPointsFeedback(points);
}

function updateScoreDisplay() {
    const scoreElement = document.getElementById('score-display');
    if (scoreElement) {
        scoreElement.textContent = score;
    }
}

function showPointsFeedback(points) {
    // Create floating points animation
    const feedback = document.createElement('div');
    feedback.textContent = `+${points}`;
    feedback.style.cssText = `
        position: fixed;
        bottom: 100px;
        right: 40px;
        font-size: 2rem;
        font-weight: bold;
        color: #22c55e;
        animation: floatUp 1s ease-out forwards;
        z-index: 9999;
        pointer-events: none;
    `;
    
    document.body.appendChild(feedback);
    
    setTimeout(() => feedback.remove(), 1000);
}

// Add CSS for floating animation
const style = document.createElement('style');
style.textContent = `
    @keyframes floatUp {
        from {
            transform: translateY(0);
            opacity: 1;
        }
        to {
            transform: translateY(-50px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Utility Functions
function shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Expose functions globally
window.addPoints = addPoints;
window.updateScoreDisplay = updateScoreDisplay;
window.showModal = showModal;
window.hideModal = hideModal;
window.shuffle = shuffle;
