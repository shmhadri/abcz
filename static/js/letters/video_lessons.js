(function () {
    "use strict";

    const LETTER_A_VIDEO_URL = "https://res.cloudinary.com/djkftm2cn/video/upload/v1787567647/Aa_zbifxy.mp4";

    function initializeLetterVideoLesson() {
        const button = document.getElementById("letterVideoBtn");
        const modal = document.getElementById("letterVideoModal");
        const closeButton = document.getElementById("closeLetterVideoModal");
        const player = document.getElementById("letterVideoPlayer");
        const currentLetter = document.getElementById("currentLetter");

        if (!button || !modal || !closeButton || !player || !currentLetter) {
            return;
        }

        let previouslyFocusedElement = null;

        function isLetterA() {
            return currentLetter.textContent.trim().toUpperCase() === "A";
        }

        function updateButtonVisibility() {
            button.hidden = !isLetterA();
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
            if (!isLetterA()) {
                return;
            }

            previouslyFocusedElement = document.activeElement;
            player.src = LETTER_A_VIDEO_URL;
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
