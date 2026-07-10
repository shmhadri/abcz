const worksheetsData = [
    {
        id: "vocabulary",
        title: "Vocabulary Worksheet",
        ar: "ورقة مفردات",
        type: "vocabulary",
        typeLabel: "مفردات",
        icon: "VOC",
        url: "/vocabulary-foundation/worksheet/",
        description: "صل الكلمة بالمعنى، اختر الترجمة، وأكمل الجملة.",
        questions: 45,
        time: "20 دقيقة",
        level: "Easy - Medium",
        answers: ["classroom = فصل دراسي", "dictionary = قاموس", "worried = قلق"],
    },
    {
        id: "grammar",
        title: "Grammar Worksheet",
        ar: "ورقة قواعد",
        type: "grammar",
        typeLabel: "قواعد",
        icon: "GR",
        url: "/grammar-foundation/worksheet/",
        description: "اختر الإجابة الصحيحة، أكمل القاعدة، وصحح الخطأ.",
        questions: 40,
        time: "25 دقيقة",
        level: "Easy - Medium",
        answers: ["She is happy.", "They are playing.", "I can swim."],
    },
    {
        id: "conversation",
        title: "Conversation Worksheet",
        ar: "ورقة محادثة",
        type: "conversation",
        typeLabel: "محادثات",
        icon: "CV",
        url: "/conversations/worksheet/",
        description: "أكمل الحوار، اختر الرد المناسب، واكتب حوارا قصيرا.",
        questions: 28,
        time: "20 دقيقة",
        level: "Medium",
        answers: ["Nice to meet you.", "I would like water, please.", "Good morning."],
    },
    {
        id: "common-sentences",
        title: "Common Sentences Worksheet",
        ar: "ورقة الجمل الشائعة",
        type: "sentences",
        typeLabel: "جمل شائعة",
        icon: "CS",
        url: "/common-sentences/worksheet/",
        description: "ترجم الجملة، رتب الكلمات، وحدد صح أو خطأ.",
        questions: 35,
        time: "25 دقيقة",
        level: "Easy - Medium",
        answers: ["How are you today?", "Can you help me, please?", "Never give up."],
    },
    {
        id: "phonics",
        title: "Phonics Worksheet",
        ar: "ورقة فونكس",
        type: "phonics",
        typeLabel: "فونكس",
        icon: "PH",
        url: "/phonics-foundation/worksheet/",
        description: "تتبع الأصوات، صنف المقاطع، واقرأ الكلمات القصيرة.",
        questions: 36,
        time: "25 دقيقة",
        level: "Easy",
        answers: ["ba, be, bi, bo, bu", "cat = short a", "pen = short e"],
    },
    {
        id: "cvc",
        title: "CVC Worksheet",
        ar: "ورقة CVC",
        type: "cvc",
        typeLabel: "CVC",
        icon: "CVC",
        url: "/cvc-reading/worksheet/",
        description: "اقرأ كلمات CVC، صل العائلة الصوتية، وأكمل الكلمة.",
        questions: 50,
        time: "30 دقيقة",
        level: "Easy - Medium",
        answers: ["cat = c-a-t", "dog = -og", "sun = short u"],
    },
    {
        id: "letters",
        title: "Letters Mastery Worksheet",
        ar: "ورقة إتقان الحروف",
        type: "letters",
        typeLabel: "حروف",
        icon: "ABC",
        url: "/letters/worksheet/",
        description: "تتبع الحروف، اكتب الكلمة الأولى، وميز الحرف الكبير والصغير.",
        questions: 52,
        time: "30 دقيقة",
        level: "Easy",
        answers: ["A a", "B b", "C c"],
    },
    {
        id: "mixed-review",
        title: "Mixed Review Worksheet",
        ar: "ورقة مراجعة شاملة",
        type: "review",
        typeLabel: "مراجعة شاملة",
        icon: "MR",
        url: "/worksheets/mixed-review/",
        description: "مراجعة تجمع المفردات والقواعد والجمل والمحادثات.",
        questions: 52,
        time: "45 دقيقة",
        level: "Medium",
        answers: ["Vocabulary matching", "Grammar choices", "Conversation response"],
    },
];

const practiceQuestions = {
    vocabulary: [
        ["What is the meaning of classroom?", "فصل دراسي", ["مطار", "فصل دراسي", "قلق"]],
        ["Choose the translation of dictionary.", "قاموس", ["قاموس", "حاسوب", "مسؤولية"]],
        ["Complete: I use a ___ to write.", "computer", ["airport", "computer", "worried"]],
        ["responsibility means", "مسؤولية", ["مسؤولية", "سفر", "سوق"]],
        ["worried means", "قلق", ["سعيد", "قلق", "سريع"]],
    ],
    grammar: [
        ["She ___ happy.", "is", ["am", "is", "are"]],
        ["They ___ students.", "are", ["is", "are", "am"]],
        ["I ___ swim.", "can", ["can", "is", "are"]],
        ["He ___ a book.", "reads", ["read", "reads", "reading"]],
        ["___ do you live?", "Where", ["Where", "Can", "Is"]],
    ],
    conversation: [
        ["A: Nice to meet you. B: ___", "Nice to meet you too.", ["Good night.", "Nice to meet you too.", "It is red."]],
        ["A: How are you? B: ___", "I am fine.", ["I am fine.", "It is big.", "Open the book."]],
        ["A: Thank you. B: ___", "You are welcome.", ["You are welcome.", "I am ten.", "It is a pen."]],
        ["A: May I have water? B: ___", "Sure.", ["Sure.", "Blue.", "Yesterday."]],
        ["A: Good morning. B: ___", "Good morning.", ["Good morning.", "Goodbye.", "No."]],
    ],
    sentences: [
        ["Can you help me, please? is polite.", "True", ["True", "False"]],
        ["Never give up. means استسلم دائما.", "False", ["True", "False"]],
        ["Good morning. is used in the morning.", "True", ["True", "False"]],
        ["How are you today? is a question.", "True", ["True", "False"]],
        ["I want to improve my reading. is about reading.", "True", ["True", "False"]],
    ],
    phonics: [
        ["Which word has short a?", "cat", ["pen", "cat", "sun"]],
        ["Choose the syllable with b.", "ba", ["ba", "ma", "ta"]],
        ["Which word has short e?", "pen", ["dog", "pen", "cup"]],
        ["c-a-t makes", "cat", ["cat", "cut", "cot"]],
        ["Which is a CVC word?", "dog", ["dog", "cake", "tree"]],
    ],
    cvc: [
        ["d-o-g makes", "dog", ["dig", "dog", "dug"]],
        ["Which family is cat in?", "-at", ["-og", "-at", "-un"]],
        ["Which word has short u?", "sun", ["sun", "pen", "cat"]],
        ["Complete: p_e_n", "pen", ["pan", "pin", "pen"]],
        ["Which is a CVC word?", "cup", ["cup", "green", "play"]],
    ],
    letters: [
        ["Which is uppercase a?", "A", ["A", "b", "c"]],
        ["Which is lowercase B?", "b", ["D", "b", "P"]],
        ["Apple starts with", "A", ["A", "M", "S"]],
        ["Cat starts with", "C", ["B", "C", "T"]],
        ["Zebra starts with", "Z", ["Y", "Z", "X"]],
    ],
    review: [
        ["dictionary means", "قاموس", ["قاموس", "قلق", "سريع"]],
        ["She ___ kind.", "is", ["are", "is", "am"]],
        ["Good morning. is a greeting.", "True", ["True", "False"]],
        ["A: Thank you. B: ___", "You are welcome.", ["You are welcome.", "I am seven.", "It is green."]],
        ["c-a-t makes", "cat", ["cat", "dog", "sun"]],
    ],
};

let activePractice = null;
let activeType = "all";
let state = {
    points: 0,
    actions: 0,
    completed: false,
    completedWorksheets: [],
};

function csrfToken() {
    return document.cookie.split(";").map((value) => value.trim()).find((value) => value.startsWith("csrftoken="))?.split("=")[1] || "";
}

function loadWorksheetProgress() {
    try {
        const local = JSON.parse(localStorage.getItem("worksheetsProgress") || "{}");
        state = {
            points: Number(local.points ?? document.body.dataset.initialPoints ?? 0),
            actions: Number(local.actions ?? document.body.dataset.initialActions ?? 0),
            completed: local.completed ?? document.body.dataset.initialCompleted === "true",
            completedWorksheets: Array.isArray(local.completedWorksheets) ? local.completedWorksheets : [],
        };
    } catch {
        state.points = Number(document.body.dataset.initialPoints || 0);
        state.actions = Number(document.body.dataset.initialActions || 0);
        state.completed = document.body.dataset.initialCompleted === "true";
        state.completedWorksheets = [];
    }
}

function saveWorksheetProgress() {
    localStorage.setItem("worksheetsProgress", JSON.stringify(state));
}

async function awardWorksheetPoints(activityType, points, completed = false, worksheetId = "") {
    state.points += points;
    state.actions += 1;
    if (worksheetId && !state.completedWorksheets.includes(worksheetId) && activityType === "complete") {
        state.completedWorksheets.push(worksheetId);
    }
    if (state.completedWorksheets.length >= 3 && !state.threeBonusAwarded) {
        state.points += 20;
        state.threeBonusAwarded = true;
    }
    if (state.points >= 150 && !state.completed) {
        state.completed = true;
        completed = true;
        state.points += 50;
    }
    saveWorksheetProgress();
    updateWorksheetStats();

    try {
        const response = await fetch(window.WORKSHEETS_PROGRESS_URL || "/api/english-foundation/progress/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken(),
            },
            body: JSON.stringify({
                section: "worksheets",
                activity_type: activityType,
                points,
                completed,
            }),
        });
        const data = await response.json();
        if (data.status === "ok") {
            state.points = data.points;
            state.actions = data.actions_count;
            state.completed = data.completed;
            saveWorksheetProgress();
            updateWorksheetStats();
        }
    } catch {
        // TODO: integrate worksheets progress with StudentActivity leaderboard.
    }
}

function statusFromPoints(points) {
    if (points >= 150) return "متقن";
    if (points >= 80) return "ممتاز";
    if (points >= 30) return "جيد";
    return "قيد التدريب";
}

function updateWorksheetStats() {
    document.getElementById("worksheetPoints").textContent = state.points;
    document.getElementById("worksheetActions").textContent = state.actions;
    document.getElementById("worksheetStatus").textContent = statusFromPoints(state.points);
    document.getElementById("worksheetProgressBar").style.width = `${Math.min(100, Math.round((state.points / 150) * 100))}%`;
}

function cardTemplate(item) {
    return `
        <article class="worksheet-card" data-id="${item.id}" data-type="${item.type}" data-level="${item.level}">
            <div class="card-icon" aria-hidden="true">${item.icon}</div>
            <h2>${item.title}</h2>
            <p class="arabic-title">${item.ar}</p>
            <p class="description">${item.description}</p>
            <div class="meta-grid">
                <div class="meta"><span>النوع</span><strong>${item.typeLabel}</strong></div>
                <div class="meta"><span>عدد الأسئلة</span><strong>${item.questions}</strong></div>
                <div class="meta"><span>الوقت المتوقع</span><strong>${item.time}</strong></div>
                <div class="meta"><span>المستوى</span><strong>${item.level}</strong></div>
            </div>
            <div class="card-actions">
                <a class="view-action" href="${item.url}" target="_blank" rel="noopener" data-action="open" data-id="${item.id}">عرض الورقة</a>
                <button class="print-action" type="button" data-action="print" data-id="${item.id}">طباعة</button>
                <button class="practice-action" type="button" data-action="practice" data-id="${item.id}">حل إلكتروني</button>
                <button class="answers-action" type="button" data-action="answers" data-id="${item.id}">الإجابات</button>
                <button class="pdf-action" type="button" disabled>PDF قريبا</button>
            </div>
        </article>
    `;
}

function renderWorksheetCards(items = worksheetsData) {
    document.getElementById("worksheetsGrid").innerHTML = items.map(cardTemplate).join("");
    document.getElementById("emptyWorksheets").hidden = items.length > 0;
}

function searchWorksheets() {
    const query = document.getElementById("worksheetSearch").value.trim().toLowerCase();
    const level = document.getElementById("worksheetLevelFilter").value;
    const type = document.getElementById("worksheetTypeFilter").value;
    const filtered = worksheetsData.filter((item) => {
        const matchesText = !query || `${item.title} ${item.ar} ${item.typeLabel}`.toLowerCase().includes(query);
        const matchesType = type === "all" || item.type === type;
        const matchesLevel = level === "all" || item.level === level;
        return matchesText && matchesType && matchesLevel;
    });
    renderWorksheetCards(filtered);
}

function filterWorksheets(type) {
    activeType = type;
    document.getElementById("worksheetTypeFilter").value = type;
    document.querySelectorAll("[data-filter-type]").forEach((button) => {
        button.classList.toggle("active", button.dataset.filterType === type);
    });
    searchWorksheets();
}

function openWorksheet(id) {
    awardWorksheetPoints("open", 1, false, id);
}

function printWorksheet(id) {
    const item = worksheetsData.find((worksheet) => worksheet.id === id);
    if (!item) return;
    awardWorksheetPoints("worksheet", 3, false, id);
    const printWindow = window.open(item.url, "_blank", "noopener");
    if (printWindow) {
        printWindow.addEventListener("load", () => printWindow.print(), { once: true });
    }
}

function openElectronicPractice(id) {
    activePractice = worksheetsData.find((worksheet) => worksheet.id === id);
    if (!activePractice) return;
    const questions = practiceQuestions[activePractice.type] || practiceQuestions.review;
    document.getElementById("practiceTitle").textContent = activePractice.title;
    document.getElementById("practiceForm").innerHTML = questions.map((question, index) => `
        <fieldset class="question">
            <p>${index + 1}. ${question[0]}</p>
            <div class="options">
                ${question[2].map((option) => `
                    <label>
                        <input type="radio" name="q${index}" value="${option}">
                        <span>${option}</span>
                    </label>
                `).join("")}
            </div>
        </fieldset>
    `).join("");
    document.getElementById("practiceResult").hidden = true;
    document.getElementById("practiceModal").hidden = false;
}

function checkWorksheetAnswers() {
    if (!activePractice) return;
    const questions = practiceQuestions[activePractice.type] || practiceQuestions.review;
    let score = 0;
    questions.forEach((question, index) => {
        const selected = document.querySelector(`input[name="q${index}"]:checked`);
        if (selected && selected.value === question[1]) score += 1;
    });
    const result = document.getElementById("practiceResult");
    result.hidden = false;
    result.textContent = `النتيجة: ${score} / ${questions.length}`;
    if (score === questions.length) {
        awardWorksheetPoints("exercise", 5, false, activePractice.id);
        awardWorksheetPoints("complete", 10, true, activePractice.id);
    }
}

function showTeacherAnswers(id) {
    const item = worksheetsData.find((worksheet) => worksheet.id === id);
    if (!item) return;
    document.getElementById("answersTitle").textContent = `${item.title} - الإجابات`;
    document.getElementById("answersBody").innerHTML = `
        <div class="answer-row">تنبيه: قسم الإجابات مخصص للمعلم.</div>
        ${item.answers.map((answer, index) => `<div class="answer-row">${index + 1}. ${answer}</div>`).join("")}
    `;
    document.getElementById("answersModal").hidden = false;
}

document.addEventListener("DOMContentLoaded", () => {
    loadWorksheetProgress();
    renderWorksheetCards();
    updateWorksheetStats();
    document.querySelector('[data-filter-type="all"]')?.classList.add("active");

    document.getElementById("worksheetSearch").addEventListener("input", searchWorksheets);
    document.getElementById("worksheetTypeFilter").addEventListener("change", (event) => filterWorksheets(event.target.value));
    document.getElementById("worksheetLevelFilter").addEventListener("change", searchWorksheets);

    document.addEventListener("click", (event) => {
        const filterButton = event.target.closest("[data-filter-type]");
        if (filterButton) {
            filterWorksheets(filterButton.dataset.filterType);
            return;
        }

        const actionControl = event.target.closest("[data-action]");
        if (actionControl) {
            const id = actionControl.dataset.id;
            const action = actionControl.dataset.action;
            if (action === "open") openWorksheet(id);
            if (action === "print") printWorksheet(id);
            if (action === "practice") openElectronicPractice(id);
            if (action === "answers") showTeacherAnswers(id);
        }

        if (event.target.matches("[data-close-modal]") || event.target.classList.contains("modal")) {
            document.querySelectorAll(".modal").forEach((modal) => {
                modal.hidden = true;
            });
        }
    });

    document.getElementById("checkPracticeAnswers").addEventListener("click", checkWorksheetAnswers);
    document.getElementById("retryPractice").addEventListener("click", () => {
        if (activePractice) openElectronicPractice(activePractice.id);
    });
});
