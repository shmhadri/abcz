(function (window, document) {
    "use strict";

    let activeAssistant = null;

    const responses = {
        greeting: "أهلا بك يا بطل! أنا هنا لمساعدتك في رحلة التعلم الممتعة. ماذا تريد أن تتعلم اليوم؟",
        howTo: "الأمر بسيط جدا!\n1. اختر حرفا أو درسا من القائمة.\n2. استمتع بالألعاب والأنشطة التفاعلية.\n3. اجمع النقاط واحصل على الشهادات.\nابدأ باختيار حرف من الأعلى!",
        gradeTwo: "درس الحيوانات البرية للصف الثاني موجود في القائمة الجانبية أو الزر العائم. فيه ألعاب ممتعة مثل Animal Chart و Guessing Game.",
        help: "أكيد! لديك قائمة بالحروف في الأعلى، وقائمة بالصفوف في الجانب. اضغط على أي منها لتبدأ.",
        games: "نحن نحب اللعب! كل حرف ودرس يحتوي على ألعاب ممتعة. جرب درس الحيوانات للعب Find the Animal.",
        thanks: "عفوا يا بطل! استمتع بوقتك!",
        bye: "إلى اللقاء! نراك قريبا!",
        fallback: "سؤال جميل!\nيمكنك تجربة الدروس الموجودة في الصفحة، أو سؤالي عن: كيف أستخدم الموقع، أو أين درس الحيوانات."
    };

    function appendTextWithLineBreaks(element, text) {
        String(text).split("\n").forEach((line, index) => {
            if (index > 0) {
                element.appendChild(document.createElement("br"));
            }

            element.appendChild(document.createTextNode(line));
        });
    }

    function fallbackToggleAssistant() {
        const chatBox = document.getElementById("ai-chat-box");
        const input = document.getElementById("ai-user-input");

        if (!chatBox) return;

        chatBox.classList.toggle("active");
        if (chatBox.classList.contains("active") && input) {
            input.focus();
        }
    }

    const AssistantMethods = {
        initAssistantSystem() {
            activeAssistant = this;

            this.aiButton = document.getElementById("ai-btn");
            this.aiCloseButton = document.getElementById("ai-close-btn");
            this.aiChatBox = document.getElementById("ai-chat-box");
            this.aiChatBody = document.getElementById("ai-chat-body");
            this.aiUserInput = document.getElementById("ai-user-input");
            this.aiSendButton = document.getElementById("ai-send-btn");

            if (this.aiButton && !this.aiButton.dataset.assistantBound) {
                this.aiButton.addEventListener("click", () => this.toggleAssistant());
                this.aiButton.dataset.assistantBound = "true";
            }

            if (this.aiCloseButton && !this.aiCloseButton.dataset.assistantBound) {
                this.aiCloseButton.addEventListener("click", () => this.toggleAssistant());
                this.aiCloseButton.dataset.assistantBound = "true";
            }

            if (this.aiSendButton && !this.aiSendButton.dataset.assistantBound) {
                this.aiSendButton.addEventListener("click", event => {
                    event.preventDefault();
                    this.sendAssistantMessage();
                });
                this.aiSendButton.dataset.assistantBound = "true";
            }

            if (this.aiUserInput && !this.aiUserInput.dataset.assistantBound) {
                this.aiUserInput.addEventListener("keypress", event => {
                    if (event.key === "Enter") {
                        this.sendAssistantMessage();
                    }
                });
                this.aiUserInput.dataset.assistantBound = "true";
            }
        },

        toggleAssistant() {
            const chatBox = this.aiChatBox || document.getElementById("ai-chat-box");
            const input = this.aiUserInput || document.getElementById("ai-user-input");

            if (!chatBox) return;

            chatBox.classList.toggle("active");
            if (chatBox.classList.contains("active") && input) {
                input.focus();
            }
        },

        sendAssistantMessage() {
            const inputField = this.aiUserInput || document.getElementById("ai-user-input");
            if (!inputField) return;

            const message = inputField.value.trim();
            if (message === "") return;

            this.addAssistantMessage(message, "user");
            inputField.value = "";

            this.showAssistantTyping();

            window.setTimeout(() => {
                this.removeAssistantTyping();
                const response = this.getAssistantResponse(message);
                this.addAssistantMessage(response, "bot");
            }, 1000);
        },

        addAssistantMessage(text, sender) {
            const chatBody = this.aiChatBody || document.getElementById("ai-chat-body");
            if (!chatBody) return;

            const msgDiv = document.createElement("div");
            msgDiv.classList.add("ai-msg", sender);

            if (sender === "user") {
                msgDiv.textContent = text;
            } else {
                appendTextWithLineBreaks(msgDiv, text);
            }

            chatBody.appendChild(msgDiv);
            chatBody.scrollTop = chatBody.scrollHeight;
        },

        showAssistantTyping() {
            const chatBody = this.aiChatBody || document.getElementById("ai-chat-body");
            if (!chatBody) return;

            this.removeAssistantTyping();

            const typingDiv = document.createElement("div");
            typingDiv.id = "ai-typing";
            typingDiv.className = "typing-indicator";

            for (let i = 0; i < 3; i++) {
                const dot = document.createElement("span");
                dot.className = "typing-dot";
                typingDiv.appendChild(dot);
            }

            chatBody.appendChild(typingDiv);
            chatBody.scrollTop = chatBody.scrollHeight;
        },

        removeAssistantTyping() {
            const typingDiv = document.getElementById("ai-typing");
            if (typingDiv) typingDiv.remove();
        },

        getAssistantResponse(input) {
            const normalizedInput = String(input).toLowerCase();

            if (
                normalizedInput.includes("مرحبا") ||
                normalizedInput.includes("هلا") ||
                normalizedInput.includes("سلام") ||
                normalizedInput.includes("hi") ||
                normalizedInput.includes("hello")
            ) {
                return responses.greeting;
            }

            if (
                normalizedInput.includes("كيف") ||
                normalizedInput.includes("استخدم") ||
                normalizedInput.includes("عمل") ||
                normalizedInput.includes("اعمل") ||
                normalizedInput.includes("how")
            ) {
                return responses.howTo;
            }

            if (
                normalizedInput.includes("ثاني") ||
                normalizedInput.includes("حيوانات") ||
                normalizedInput.includes("wild") ||
                normalizedInput.includes("animals")
            ) {
                return responses.gradeTwo;
            }

            if (normalizedInput.includes("مساعدة") || normalizedInput.includes("help")) {
                return responses.help;
            }

            if (
                normalizedInput.includes("لعبة") ||
                normalizedInput.includes("game") ||
                normalizedInput.includes("لعب")
            ) {
                return responses.games;
            }

            if (
                normalizedInput.includes("شكرا") ||
                normalizedInput.includes("شكراً") ||
                normalizedInput.includes("thanks")
            ) {
                return responses.thanks;
            }

            if (normalizedInput.includes("باي") || normalizedInput.includes("مع السلامة")) {
                return responses.bye;
            }

            return responses.fallback;
        }
    };

    window.installLettersAssistantSystem = function installLettersAssistantSystem(GameClass) {
        if (!GameClass || !GameClass.prototype) return;

        Object.assign(GameClass.prototype, AssistantMethods);

        if (GameClass.prototype.__lettersAssistantWrapped) return;

        const originalInit = GameClass.prototype.init;
        GameClass.prototype.init = function initWithAssistant(...args) {
            const result = originalInit.apply(this, args);
            this.initAssistantSystem();
            return result;
        };

        GameClass.prototype.__lettersAssistantWrapped = true;
    };

    window.toggleAI = function toggleAI() {
        if (activeAssistant && typeof activeAssistant.toggleAssistant === "function") {
            activeAssistant.toggleAssistant();
            return;
        }

        fallbackToggleAssistant();
    };

    window.sendMessage = function sendMessage() {
        if (activeAssistant && typeof activeAssistant.sendAssistantMessage === "function") {
            activeAssistant.sendAssistantMessage();
        }
    };
})(window, document);
