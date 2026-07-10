(function () {
    const questionsNode = document.getElementById("placementQuestions");
    const form = document.querySelector("[data-placement-form]");
    const resultCard = document.querySelector("[data-placement-result]");

    if (!questionsNode || !form || !resultCard) {
        return;
    }

    const questions = JSON.parse(questionsNode.textContent || "[]");
    const csrfToken = form.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
    const endpoint = form.dataset.endpoint || window.location.pathname;

    function renderSectionScores(sectionScores) {
        const orderedSections = [];
        questions.forEach((question) => {
            if (!orderedSections.includes(question.section)) {
                orderedSections.push(question.section);
            }
        });

        return orderedSections
            .filter((section) => sectionScores[section])
            .map((section) => {
                const score = sectionScores[section];
                return `<li><strong>${score.label}</strong><span>${score.correct} / ${score.total}</span></li>`;
            })
            .join("");
    }

    function showResult(html) {
        resultCard.hidden = false;
        resultCard.innerHTML = html;
        resultCard.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    function renderResult(result) {
        showResult(`
            <span class="route-badge">نتيجتك</span>
            <h2>${result.recommended_title}: ${result.recommended_track}</h2>
            <p class="result-score">${result.percentage}% - ${result.score} من ${result.total}</p>
            <p>${result.message}</p>
            <p class="legal-note">${result.reason}</p>
            <ul class="clean-list result-sections">${renderSectionScores(result.section_scores)}</ul>
            <div class="hero-actions">
                <a class="btn primary" href="${result.cta_url}">${result.cta_label}</a>
                <a class="btn" href="${window.location.pathname}">إعادة الاختبار</a>
            </div>
        `);
    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const answers = {};
        questions.forEach((question) => {
            const checked = form.querySelector(`input[name="${question.id}"]:checked`);
            if (checked) {
                answers[question.id] = checked.value;
            }
        });

        if (Object.keys(answers).length < questions.length) {
            showResult(`
                <span class="route-badge">تنبيه</span>
                <h2>أكمل كل الأسئلة قبل عرض النتيجة</h2>
                <p>المتبقي ${questions.length - Object.keys(answers).length} سؤال.</p>
            `);
            return;
        }

        const response = await fetch(endpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify({ answers }),
        });

        if (!response.ok) {
            showResult(`
                <span class="route-badge">تعذر عرض النتيجة</span>
                <h2>حدث خطأ مؤقت</h2>
                <p>حاول مرة أخرى بعد لحظات.</p>
            `);
            return;
        }

        renderResult(await response.json());
    });
}());
