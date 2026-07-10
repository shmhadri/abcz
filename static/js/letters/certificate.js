(function (window) {
    "use strict";

    const defaultStudentName = "\u0627\u0644\u0637\u0627\u0644\u0628 \u0627\u0644\u0645\u062A\u0645\u064A\u0632";

    const messages = {
        completeAllLetters: "\u064A\u062C\u0628 \u0625\u0643\u0645\u0627\u0644 \u062C\u0645\u064A\u0639 \u0627\u0644\u062D\u0631\u0648\u0641 \u0623\u0648\u0644\u0627!",
        certificateNotFound: "Certificate not found",
        emailPrompt: "\u0623\u062F\u062E\u0644 \u0639\u0646\u0648\u0627\u0646 \u0627\u0644\u0628\u0631\u064A\u062F \u0627\u0644\u0625\u0644\u0643\u062A\u0631\u0648\u0646\u064A:",
        emailSubject: "\u0634\u0647\u0627\u062F\u0629 \u0625\u062A\u0642\u0627\u0646 \u0627\u0644\u062D\u0631\u0648\u0641 \u0627\u0644\u0625\u0646\u062C\u0644\u064A\u0632\u064A\u0629",
        emailOpened: "\u062A\u0645 \u0641\u062A\u062D \u0628\u0631\u0646\u0627\u0645\u062C \u0627\u0644\u0628\u0631\u064A\u062F \u0644\u0625\u0631\u0633\u0627\u0644 \u0627\u0644\u0634\u0647\u0627\u062F\u0629",
        whatsappPrompt: "\u0623\u062F\u062E\u0644 \u0631\u0642\u0645 \u0627\u0644\u0648\u0627\u062A\u0633\u0627\u0628 \u0645\u0639 \u0631\u0645\u0632 \u0627\u0644\u062F\u0648\u0644\u0629:",
        whatsappOpened: "\u062A\u0645 \u0641\u062A\u062D \u0648\u0627\u062A\u0633\u0627\u0628 \u0644\u0645\u0634\u0627\u0631\u0643\u0629 \u0627\u0644\u0634\u0647\u0627\u062F\u0629"
    };

    function buildCertificateId() {
        const stored = localStorage.getItem("lettersCertificateId");
        if (stored) return stored;

        const datePart = new Date().toISOString().slice(0, 10).replace(/-/g, "");
        const randomPart = String(Math.floor(1000 + Math.random() * 9000));
        const certificateId = `PGL-LETTERS-${datePart}-${randomPart}`;
        localStorage.setItem("lettersCertificateId", certificateId);
        return certificateId;
    }

    const CertificateMethods = {
        showCertificate() {
            if (window.LEVEL_ONE_DISABLED_FEATURES?.certificate) {
                this.showToast("\u0627\u0644\u0634\u0647\u0627\u062f\u0629 \u0645\u062a\u0627\u062d\u0629 \u0628\u0639\u062f \u0625\u0643\u0645\u0627\u0644 \u0627\u0644\u062d\u0631\u0648\u0641 \u0641\u064a \u0628\u0627\u0642\u0629 Basic \u0623\u0648 Silver \u0623\u0648 \u0623\u0639\u0644\u0649.");
                return;
            }
            if (this.completedLetters.length !== LETTERS.length) {
                this.showToast(messages.completeAllLetters);
                return;
            }

            const totalStars = this.calculateTotalStars();
            const completionDate = new Date().toLocaleDateString("ar-SA");

            if (this.certificateName) {
                this.certificateName.textContent = this.studentName || defaultStudentName;
            }

            const dateEl = document.getElementById("certificate-date");
            const starsEl = document.getElementById("certificate-stars");
            const countEl = document.getElementById("certificate-letters-count");
            const certificateIdEl = document.getElementById("certificate-id");
            const certificateId = buildCertificateId();

            if (dateEl) dateEl.textContent = completionDate;
            if (starsEl) starsEl.textContent = totalStars;
            if (countEl) countEl.textContent = LETTERS.length;
            if (certificateIdEl) certificateIdEl.textContent = certificateId;

            if (this.certificateModal) {
                this.certificateModal.style.display = "flex";
            }

            localStorage.setItem("certificateEarned", "true");
            localStorage.setItem("certificateDate", completionDate);
            localStorage.setItem("certificateStars", totalStars);
            localStorage.setItem("certificateId", certificateId);
            this.soundManager.playSound("win");
        },

        calculateTotalStars() {
            let totalStars = 0;
            LETTERS.forEach(letter => {
                const letterGames = this.passedGames[letter] || [];
                totalStars += letterGames.length;
            });
            return totalStars;
        },

        printCertificate() {
            const modal = this.certificateModal;
            if (!modal) return;

            const originalDisplay = modal.style.display;
            modal.style.display = "none";

            const certificate = document.querySelector(".certificate-content") || document.querySelector(".certificate-container");
            if (!certificate) {
                this.showToast(messages.certificateNotFound, 3000, "error");
                modal.style.display = originalDisplay;
                return;
            }

            const originalBody = document.body.innerHTML;

            document.body.innerHTML = certificate.outerHTML;
            window.print();

            document.body.innerHTML = originalBody;
            this.init();
            modal.style.display = originalDisplay;
        },

        sendCertificateEmail() {
            const email = prompt(messages.emailPrompt);
            if (!email) return;

            const studentName = this.studentName || defaultStudentName;
            const subject = `${messages.emailSubject} - ${studentName}`;
            const body = `\u062A\u0647\u0627\u0646\u064A\u0646\u0627! \u0644\u0642\u062F \u0623\u0643\u0645\u0644 ${studentName} \u062C\u0645\u064A\u0639 \u0627\u0644\u062D\u0631\u0648\u0641 \u0627\u0644\u0625\u0646\u062C\u0644\u064A\u0632\u064A\u0629 \u0628\u0646\u062C\u0627\u062D!\n\n\u0639\u062F\u062F \u0627\u0644\u0646\u062C\u0648\u0645: ${this.calculateTotalStars()}\n\u062A\u0627\u0631\u064A\u062E \u0627\u0644\u0625\u0646\u062C\u0627\u0632: ${new Date().toLocaleDateString("ar-SA")}`;
            const mailtoLink = `mailto:${email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;

            window.open(mailtoLink);
            this.showToast(messages.emailOpened, 3000, "success");
        },

        sendCertificateWhatsApp() {
            const phone = prompt(messages.whatsappPrompt);
            if (!phone) return;

            const studentName = this.studentName || defaultStudentName;
            const message = `\uD83C\uDF89 \u062A\u0647\u0627\u0646\u064A\u0646\u0627! \u0644\u0642\u062F \u0623\u0643\u0645\u0644 ${studentName} \u062C\u0645\u064A\u0639 \u0627\u0644\u062D\u0631\u0648\u0641 \u0627\u0644\u0625\u0646\u062C\u0644\u064A\u0632\u064A\u0629 \u0628\u0646\u062C\u0627\u062D!\n\n\u2B50 \u0639\u062F\u062F \u0627\u0644\u0646\u062C\u0648\u0645: ${this.calculateTotalStars()}\n\uD83D\uDCC5 \u062A\u0627\u0631\u064A\u062E \u0627\u0644\u0625\u0646\u062C\u0627\u0632: ${new Date().toLocaleDateString("ar-SA")}\n\n\uD83C\uDF93 \u0634\u0647\u0627\u062F\u0629 \u0625\u062A\u0642\u0627\u0646 \u0627\u0644\u062D\u0631\u0648\u0641 \u0627\u0644\u0625\u0646\u062C\u0644\u064A\u0632\u064A\u0629`;
            const whatsappLink = `https://wa.me/${phone.replace(/[^\d]/g, "")}?text=${encodeURIComponent(message)}`;

            window.open(whatsappLink, "_blank");
            this.showToast(messages.whatsappOpened, 3000, "success");
        },

        showCompletionAnimation() {
            if (!this.completionAnimation) return;

            for (let i = 0; i < 150; i++) {
                const confetti = document.createElement("div");
                confetti.className = "confetti";
                confetti.style.left = Math.random() * 100 + "vw";
                confetti.style.animationDuration = (Math.random() * 3 + 2) + "s";
                confetti.style.animationDelay = Math.random() * 5 + "s";
                confetti.style.backgroundColor = `hsl(${Math.random() * 360}, 70%, 60%)`;

                this.completionAnimation.appendChild(confetti);
            }

            setTimeout(() => {
                this.completionAnimation.innerHTML = "";
            }, 7000);
        }
    };

    window.installCertificateSystem = function installCertificateSystem(GameClass) {
        if (!GameClass || !GameClass.prototype) return;
        Object.assign(GameClass.prototype, CertificateMethods);
    };
})(window);
