/**
 * Top Goal - Lessons Navigation
 * التنقل بين الدروس
 */

function initLessonNavigation() {
    console.log('📚 Initializing lesson navigation...');
    
    // Add click handlers to all lesson buttons
    const lessonButtons = document.querySelectorAll('.lesson-btn');
    lessonButtons.forEach((btn, index) => {
        btn.addEventListener('click', function() {
            switchLesson(index + 1);
        });
    });
    
    // Show first lesson by default
    switchLesson(1);
}

function switchLesson(lessonNumber) {
    console.log(`📖 Switching to lesson ${lessonNumber}...`);
    
    // Hide all lesson sections
    const allLessons = document.querySelectorAll('.lesson-section');
    allLessons.forEach(lesson => {
        lesson.classList.remove('active');
        lesson.style.display = 'none';
    });

    // Show selected lesson
    const selectedLesson = document.getElementById(`lesson-${lessonNumber}`);
    if (selectedLesson) {
        selectedLesson.classList.add('active');
        selectedLesson.style.display = 'block';
    } else {
        console.warn(`⚠️ Lesson ${lessonNumber} not found!`);
    }

    // Update button active states
    const allButtons = document.querySelectorAll('.lesson-btn');
    allButtons.forEach((btn, index) => {
        if (index + 1 === lessonNumber) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Expose functions globally
window.initLessonNavigation = initLessonNavigation;
window.switchLesson = switchLesson;
