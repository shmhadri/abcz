(function () {
    "use strict";

    const VIDEO_LESSONS = Object.freeze({
        A: {
            title: "طريقة كتابة حرف A",
            url: "https://res.cloudinary.com/djkftm2cn/video/upload/v1787567647/Aa_zbifxy.mp4",
        },
        B: {
            title: "طريقة كتابة حرف B",
            url: "https://res.cloudinary.com/djkftm2cn/video/upload/v1787567647/Bb_keapwq.mp4",
        },
        C: {
            title: "طريقة كتابة حرف C",
            url: "https://res.cloudinary.com/djkftm2cn/video/upload/v1787568258/doc_2026-08-24_12-27-45_f9b45o.mp4",
        },
    });

    function initializeLetterVideoLesson() {
        const button = document.getElementById("letterVideoBtn");
        const modal = document.getElementById("letterVideoModal");
        const closeButton = document.getElementById("closeLetterVideoModal");
        const player = document.getElementById("letterVideoPlayer");
        const currentLetter = document.getElementById("currentLetter");
        const title = document.getElementById("letterVideoTitle");

        if (!button || !modal || !closeButton || !player || !currentLetter || !title) {
            return;
        }

        let previouslyFocusedElement = null;

        function currentVideoLesson() {
            const letter = currentLetter.textContent.trim().toUpperCase();
            return VIDEO_LESSONS[letter] || null;
        }

        function updateButtonVisibility() {
            button.hidden = !currentVideoLesson();
        }

        function closeModal() {
            if (modal.style.display === "none") {
                return;
            }

            player.pause();
            player.removeAttribute("src");
            player.load();
            modal.style.display = "none";
            modal.setAttribute("aria-hidden", "true");

            if (previouslyFocusedElement) {
                previouslyFocusedElement.focus();
            }
        }

        function openModal() {
            const lesson = currentVideoLesson();
            if (!lesson) {
                return;
            }

            previouslyFocusedElement = document.activeElement;
            title.textContent = lesson.title;
            player.src = lesson.url;
            modal.style.display = "flex";
            modal.setAttribute("aria-hidden", "false");
            closeButton.focus();
        }

        button.addEventListener("click", openModal);
        closeButton.addEventListener("click", closeModal);
        modal.addEventListener("click", function (event) {
            if (event.target === modal) {
                closeModal();
            }
        });
        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape" && modal.style.display === "flex") {
                closeModal();
            }
        });

        new MutationObserver(updateButtonVisibility).observe(currentLetter, {
            childList: true,
            characterData: true,
            subtree: true,
        });
        updateButtonVisibility();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initializeLetterVideoLesson, { once: true });
    } else {
        initializeLetterVideoLesson();
    }
}());
