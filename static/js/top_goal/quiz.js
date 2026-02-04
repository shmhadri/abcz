/**
 * Top Goal - Quiz JavaScript
 * منطق الاختبارات والأسئلة
 */

// Quiz State
let quizState = {
    currentQuestion: 1,
    score: 0,
    answers: {}
};

// Board Game Questions
const boardGameQuestions = {
    1: {
        questionEn: "Which movie type is funny?",
        questionAr: "أي نوع من الأفلام مضحك؟",
        type: "drag",
       instruction: "Drag the correct answer - اسحب الإجابة الصحيحة",
        items: [
            {id: "comedy", text: "Comedy", textAr: "كوميديا", target: "answer"},
            {id: "action", text: "Action", textAr: "أكشن", target: null},
            {id: "horror", text: "Horror", textAr: "رعب", target: null}
        ],
        dropZones: [
            {id: "answer", label: "Drop Answer Here", labelAr: "أسقط الإجابة هنا", correctItem: "comedy"}
        ],
        explanation: "Comedy movies make people laugh!",
        explanationAr: "أفلام الكوميديا تجعل الناس يضحكون!",
        points: 15
    },
    2: {
        questionEn: "Complete the sentence correctly",
        questionAr: "أكمل الجملة بشكل صحيح",
        type: "drag",
        instruction: "Drag the missing word - اسحب الكلمة الناقصة",
        sentence: "She ___ watching a movie.",
        sentenceAr: "هي كانت تشاهد فيلماً",
        items: [
            {id: "was", text: "was", textAr: "كانت", target: "answer"},
            {id: "were", text: "were", textAr: "كانوا", target: null},
            {id: "is", text: "is", textAr: "هي (مضارع)", target: null}
        ],
        dropZones: [
            {id: "answer", label: "Missing Word", labelAr: "الكلمة الناقصة", correctItem: "was"}
        ],
        explanation: "Use 'was' with 'She' in Past Progressive!",
        explanationAr: "نستخدم 'was' مع 'She' في الماضي المستمر!",
        points: 20
    }
};

function initQuizzes() {
    console.log('📝 Initializing quizzes...');
    
    // Initialize any quiz rendering if needed
    const quizzes = document.querySelectorAll('.quiz-question');
    if (quizzes.length > 0) {
        console.log(`✅ Found ${quizzes.length} quiz questions`);
    }
}

function renderQuizzes() {
    // This function can be used to dynamically render quizzes if needed
    console.log('📋 Rendering quizzes...');
}

// Roll Dice for Board Game
function rollDice() {
    const diceDisplay = document.getElementById('dice-display');
    const resultDiv = document.getElementById('dice-result');
    
    if (!diceDisplay || !resultDiv) return;
    
    // Animate dice roll
    let rolls = 0;
    const diceEmojis = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅'];
    
    const rollInterval = setInterval(() => {
        diceDisplay.textContent = diceEmojis[Math.floor(Math.random() * 6)];
        rolls++;
        
        if (rolls > 10) {
            clearInterval(rollInterval);
            const finalRoll = Math.floor(Math.random() * 6) + 1;
            diceDisplay.textContent = diceEmojis[finalRoll - 1];
            resultDiv.innerHTML = `<span style="color:#7209b7; font-size:1.5rem;">You rolled ${finalRoll}! - حصلت على ${finalRoll}!</span>`;
            
            if (finalRoll >= 1 && finalRoll <= 6) {
                setTimeout(() => openQuestion(finalRoll), 800);
            }
        }
    }, 100);
}

function openQuestion(questionNum) {
    const question = boardGameQuestions[questionNum];
    if (!question) return;
    
    const modal = document.getElementById('question-modal');
    const content = document.getElementById('question-content');
    
    if (!modal || !content) return;
    
    let html = `
        <div style="text-align:center; margin-bottom:25px;">
            <h3 style="color:#7209b7; margin-bottom:15px; font-size:1.3rem;">Question ${questionNum} - سؤال ${questionNum}</h3>
        </div>
        
        <div style="background:#f0f9ff; padding:25px; border-radius:15px; margin-bottom:30px;">
            <div style="font-size:1.4rem; font-weight:bold; color:#1e40af; margin-bottom:12px;">${question.questionEn}</div>
            <div style="font-size:1.3rem; color:#64748b; direction:rtl;">${question.questionAr}</div>
        </div>
    `;
    
    content.innerHTML = html;
    modal.style.display = 'flex';
}

function closeQuestionModal() {
    const modal = document.getElementById('question-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Quiz Functions for Unit Review
function checkQuizAnswer(questionNum, selectedAnswer) {
    const questionEl = document.querySelector(`.quiz-question[data-question="${questionNum}"]`);
    if (!questionEl) return;
    
    const allOptions = questionEl.querySelectorAll('.mcq-opt');
    const feedbackEl = questionEl.querySelector('.quiz-feedback');
    const correctAnswer = questionEl.dataset.correct;
    
    // If already answered, don't allow re-answering
    if (quizState.answers[questionNum]) {
        return;
    }
    
    // Disable all buttons
    allOptions.forEach(btn => btn.disabled = true);
    
    // Store answer
    quizState.answers[questionNum] = selectedAnswer;
    
    const isCorrect = selectedAnswer === correctAnswer;
    
    // Highlight correct answer (green) and wrong answer if selected (red)
    allOptions.forEach(btn => {
        const btnAnswer = btn.dataset.answer;
        if (btnAnswer === correctAnswer) {
            btn.style.background = 'linear-gradient(135deg, #d1fae5, #a7f3d0)';
            btn.style.borderColor = '#10b981';
            btn.style.color = '#065f46';
        } else if (btnAnswer === selectedAnswer && !isCorrect) {
            btn.style.background = 'linear-gradient(135deg, #fee2e2, #fecaca)';
            btn.style.borderColor = '#ef4444';
            btn.style.color = '#991b1b';
        }
    });
    
    // Show feedback
    if (feedbackEl) {
        if (isCorrect) {
            quizState.score++;
            feedbackEl.innerHTML = `
                <div style="background:#d1fae5; padding:20px; border-radius:12px; border:2px solid #10b981;">
                    <div style="font-size:1.4rem; color:#065f46;">✅ صحيح! Correct!</div>
                </div>
            `;
        } else {
            feedbackEl.innerHTML = `
                <div style="background:#fee2e2; padding:20px; border-radius:12px; border:2px solid #ef4444;">
                    <div style="font-size:1.4rem; color:#991b1b;">❌ خطأ - Incorrect</div>
                </div>
            `;
        }
        
        feedbackEl.style.display = 'block';
    }
    
    // Update progress
    updateQuizProgress(questionNum);
    
    // Auto-move to next question after 3 seconds
    setTimeout(() => {
        if (questionNum < 10) {
            moveToNextQuestion(questionNum + 1);
        } else {
            showQuizResults();
        }
    }, 3000);
}

function updateQuizProgress(answeredQuestions) {
    const progressText = document.getElementById('quiz-progress');
    const progressBar = document.getElementById('progress-bar');
    
    if (progressText && progressBar) {
        const percentage = (answeredQuestions / 10) * 100;
        progressText.textContent = `${answeredQuestions}/10`;
        progressBar.style.width = `${percentage}%`;
    }
}

function moveToNextQuestion(nextNum) {
    // Hide current question
    const current = document.querySelector(`.quiz-question[style*="display: block"], .quiz-question[style*="display:block"]`);
    if (current) {
        current.style.display = 'none';
    }
    
    // Show next question
    const nextQuestion = document.querySelector(`.quiz-question[data-question="${nextNum}"]`);
    if (nextQuestion) {
        nextQuestion.style.display = 'block';
        quizState.currentQuestion = nextNum;
        window.scrollTo({ top: 300, behavior: 'smooth' });
    }
}

function showQuizResults() {
    const quizContainer = document.getElementById('quiz-container');
    const resultsDiv = document.getElementById('quiz-results');
    const scoreDisplay = document.getElementById('final-score');
    const messageDisplay = document.getElementById('final-message');
    
    if (quizContainer) quizContainer.style.display = 'none';
    if (!resultsDiv || !scoreDisplay || !messageDisplay) return;
    
    scoreDisplay.textContent = `${quizState.score}/10`;
    
    // Set message based on score
    if (quizState.score === 10) {
        messageDisplay.textContent = 'Perfect! ممتاز جداً! 🌟';
    } else if (quizState.score >= 8) {
        messageDisplay.textContent = 'Excellent! رائع! 👏';
    } else if (quizState.score >= 6) {
        messageDisplay.textContent = 'Good job! أحسنت! 👍';
    } else {
        messageDisplay.textContent = 'Keep trying! استمر! 💪';
    }
    
    resultsDiv.style.display = 'block';
    window.scrollTo({ top: 300, behavior: 'smooth' });
}

function restartQuiz() {
    // Reset state
    quizState = {
        currentQuestion: 1,
        score: 0,
        answers: {}
    };
    
    // Reset all questions
    const allQuestions = document.querySelectorAll('.quiz-question');
    allQuestions.forEach((q, index) => {
        q.style.display = index === 0 ? 'block' : 'none';
        
        // Reset buttons
        const buttons = q.querySelectorAll('.mcq-opt');
        buttons.forEach(btn => {
            btn.disabled = false;
            btn.style.background = 'white';
            btn.style.borderColor = '#cbd5e1';
            btn.style.color = '#334155';
        });
        
        // Hide feedback
        const feedback = q.querySelector('.quiz-feedback');
        if (feedback) {
            feedback.style.display = 'none';
            feedback.innerHTML = '';
        }
    });
    
    // Reset progress
    updateQuizProgress(0);
    
    // Hide results, show quiz
    const results = document.getElementById('quiz-results');
    const container = document.getElementById('quiz-container');
    
    if (results) results.style.display = 'none';
    if (container) container.style.display = 'block';
    
    window.scrollTo({ top: 300, behavior: 'smooth' });
}

// Expose functions globally
window.initQuizzes = initQuizzes;
window.renderQuizzes = renderQuizzes;
window.rollDice = rollDice;
window.openQuestion = openQuestion;
window.closeQuestionModal = closeQuestionModal;
window.checkQuizAnswer = checkQuizAnswer;
window.updateQuizProgress = updateQuizProgress;
window.moveToNextQuestion = moveToNextQuestion;
window.showQuizResults = showQuizResults;
window.restartQuiz = restartQuiz;
window.boardGameQuestions = boardGameQuestions;
