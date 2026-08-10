(function () {
    "use strict";

    const questionsNode = document.getElementById("placementQuestions");
    const form = document.querySelector("[data-placement-form]");
    const resultCard = document.querySelector("[data-placement-result]");

    if (!questionsNode || !form || !resultCard) {
        return;
    }

    const questions = JSON.parse(questionsNode.textContent || "[]");
    const questionFields = Array.from(form.querySelectorAll("[data-question-index]"));
    const csrfToken = form.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
    const endpoint = form.dataset.endpoint || window.location.pathname;
    const previousButton = form.querySelector("[data-previous-question]");
    const nextButton = form.querySelector("[data-next-question]");
    const submitButton = form.querySelector("[data-submit-test]");
    const resetButton = form.querySelector("[data-reset-test]");
    const progressTitle = form.querySelector("[data-progress-title]");
    const progressSection = form.querySelector("[data-progress-section]");
    const progressTrack = form.querySelector("[data-progress-track]");
    const progressBar = form.querySelector("[data-progress-bar]");
    const answeredCount = form.querySelector("[data-answered-count]");
    const storageKey = "pgl-placement-test-v2";
    let currentIndex = 0;
    let isSubmitting = false;

    function escapeHtml(value) {
        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    function getQuestionInputs(question) {
        return Array.from(form.querySelectorAll(`input[name="${question.id}"]`));
    }

    function getAnswers() {
        const answers = {};
        questions.forEach((question) => {
            const checked = getQuestionInputs(question).find((input) => input.checked);
            if (checked) {
                answers[question.id] = checked.value;
            }
        });
        return answers;
    }

    function saveProgress() {
        try {
            window.sessionStorage.setItem(storageKey, JSON.stringify({
                answers: getAnswers(),
                currentIndex,
                savedAt: Date.now(),
            }));
        } catch (error) {}
    }

    function restoreProgress() {
        try {
            const saved = JSON.parse(window.sessionStorage.getItem(storageKey) || "null");
            if (!saved || typeof saved.answers !== "object") {
                return;
            }

            questions.forEach((question) => {
                const savedAnswer = saved.answers[question.id];
                const matchingInput = getQuestionInputs(question).find(
                    (input) => input.value === savedAnswer
                );
                if (matchingInput) {
                    matchingInput.checked = true;
                }
            });

            if (Number.isInteger(saved.currentIndex)) {
                currentIndex = Math.min(
                    Math.max(saved.currentIndex, 0),
                    Math.max(questions.length - 1, 0)
                );
            }
        } catch (error) {}
    }

    function updateProgress() {
        const answers = getAnswers();
        const answeredTotal = Object.keys(answers).length;
        const completion = questions.length
            ? Math.round((answeredTotal / questions.length) * 100)
            : 0;
        const question = questions[currentIndex];

        progressTitle.textContent = `السؤال ${currentIndex + 1} من ${questions.length}`;
        progressSection.textContent = question?.section_label || "";
        answeredCount.textContent = `تمت الإجابة عن ${answeredTotal} من ${questions.length}`;
        progressBar.style.width = `${completion}%`;
        progressTrack.setAttribute("aria-valuenow", String(completion));
    }

    function showQuestion(index, options = {}) {
        currentIndex = Math.min(Math.max(index, 0), Math.max(questionFields.length - 1, 0));
        questionFields.forEach((field, fieldIndex) => {
            field.hidden = fieldIndex !== currentIndex;
        });

        previousButton.disabled = currentIndex === 0;
        const isLastQuestion = currentIndex === questionFields.length - 1;
        nextButton.hidden = isLastQuestion;
        submitButton.hidden = !isLastQuestion;
        updateProgress();
        saveProgress();

        if (options.focus) {
            questionFields[currentIndex]?.querySelector("input")?.focus({ preventScroll: true });
            questionFields[currentIndex]?.scrollIntoView({ behavior: "smooth", block: "center" });
        }
    }

    function validateQuestion(index) {
        const field = questionFields[index];
        const question = questions[index];
        const checked = question && getQuestionInputs(question).some((input) => input.checked);
        const errorNode = field?.querySelector("[data-question-error]");

        field?.classList.toggle("has-error", !checked);
        if (errorNode) {
            errorNode.hidden = Boolean(checked);
        }
        return Boolean(checked);
    }

    function clearSavedProgress() {
        try {
            window.sessionStorage.removeItem(storageKey);
        } catch (error) {}
    }

    function resetTest(confirmReset) {
        if (confirmReset && !window.confirm("هل تريد حذف إجاباتك والبدء من جديد؟")) {
            return;
        }

        form.reset();
        questionFields.forEach((field) => {
            field.classList.remove("has-error");
            const errorNode = field.querySelector("[data-question-error]");
            if (errorNode) {
                errorNode.hidden = true;
            }
        });
        resultCard.hidden = true;
        resultCard.innerHTML = "";
        form.hidden = false;
        clearSavedProgress();
        showQuestion(0, { focus: true });
    }

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
                const percentage = Number(score.percentage) || 0;
                return `
                    <li class="result-section-row result-section-${escapeHtml(score.status)}">
                        <div>
                            <strong>${escapeHtml(score.label)}</strong>
                            <span>${escapeHtml(score.feedback)}</span>
                        </div>
                        <div class="result-section-score">${score.correct} / ${score.total}</div>
                        <div class="result-section-track" aria-label="${escapeHtml(score.label)} ${percentage}%">
                            <span style="width: ${Math.min(Math.max(percentage, 0), 100)}%"></span>
                        </div>
                    </li>`;
            })
            .join("");
    }

    function renderInsight(title, items, className) {
        if (!Array.isArray(items) || !items.length) {
            return "";
        }
        return `
            <div class="placement-insight ${className}">
                <h3>${escapeHtml(title)}</h3>
                <p>${items.map(escapeHtml).join("، ")}</p>
            </div>`;
    }

    function showResult(html) {
        resultCard.hidden = false;
        resultCard.innerHTML = html;
        resultCard.focus({ preventScroll: true });
        resultCard.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    function renderResult(result) {
        form.hidden = true;
        clearSavedProgress();
        showResult(`
            <span class="route-badge">نتيجتك وخطتك المقترحة</span>
            <div class="placement-result-heading">
                <div class="placement-score-ring" style="--score: ${Number(result.percentage) || 0}">
                    <strong>${escapeHtml(result.percentage)}%</strong>
                    <span>${escapeHtml(result.score)} من ${escapeHtml(result.total)}</span>
                </div>
                <div>
                    <h2>${escapeHtml(result.recommended_title)}</h2>
                    <p class="result-track">${escapeHtml(result.recommended_track)}</p>
                    <p>${escapeHtml(result.message)}</p>
                </div>
            </div>
            <p class="placement-reason">${escapeHtml(result.reason)}</p>
            <div class="placement-insights">
                ${renderInsight("نقاط قوتك", result.strengths, "is-strength")}
                ${renderInsight("ابدأ بمراجعة", result.focus_areas, "is-focus")}
            </div>
            <h3 class="placement-report-title">تفصيل المهارات</h3>
            <ul class="clean-list result-sections">${renderSectionScores(result.section_scores)}</ul>
            <div class="hero-actions placement-result-actions">
                <a class="btn primary" href="${escapeHtml(result.cta_url)}">${escapeHtml(result.cta_label)}</a>
                <button class="btn" type="button" data-restart-result>إعادة الاختبار</button>
            </div>
        `);

        resultCard.querySelector("[data-restart-result]")?.addEventListener("click", () => {
            resetTest(false);
        });
    }

    function showSubmissionError(message) {
        form.hidden = true;
        showResult(`
            <span class="route-badge">تعذر عرض النتيجة</span>
            <h2>حدث خطأ مؤقت</h2>
            <p>${escapeHtml(message)}</p>
            <button class="btn" type="button" data-return-to-test>العودة إلى الاختبار</button>
        `);
        resultCard.querySelector("[data-return-to-test]")?.addEventListener("click", () => {
            resultCard.hidden = true;
            form.hidden = false;
            showQuestion(currentIndex, { focus: true });
        });
    }

    form.classList.add("is-enhanced");
    restoreProgress();
    showQuestion(currentIndex);

    form.addEventListener("change", (event) => {
        if (!event.target.matches('input[type="radio"]')) {
            return;
        }
        const field = event.target.closest("[data-question-index]");
        field?.classList.remove("has-error");
        const errorNode = field?.querySelector("[data-question-error]");
        if (errorNode) {
            errorNode.hidden = true;
        }
        updateProgress();
        saveProgress();
    });

    nextButton.addEventListener("click", () => {
        if (validateQuestion(currentIndex)) {
            showQuestion(currentIndex + 1, { focus: true });
        }
    });

    previousButton.addEventListener("click", () => {
        showQuestion(currentIndex - 1, { focus: true });
    });

    resetButton.addEventListener("click", () => resetTest(true));

    form.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" || event.target.tagName === "BUTTON") {
            return;
        }
        event.preventDefault();
        if (currentIndex === questionFields.length - 1) {
            form.requestSubmit();
        } else {
            nextButton.click();
        }
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        if (isSubmitting) {
            return;
        }

        const firstMissingIndex = questions.findIndex((question) => (
            !getQuestionInputs(question).some((input) => input.checked)
        ));
        if (firstMissingIndex !== -1) {
            showQuestion(firstMissingIndex, { focus: true });
            validateQuestion(firstMissingIndex);
            return;
        }

        isSubmitting = true;
        submitButton.disabled = true;
        submitButton.textContent = "جاري تحليل النتيجة...";

        try {
            const response = await fetch(endpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify({ answers: getAnswers() }),
            });
            const result = await response.json();
            if (!response.ok) {
                throw new Error("تعذر التحقق من الإجابات. راجع إجاباتك وحاول مرة أخرى.");
            }
            renderResult(result);
        } catch (error) {
            showSubmissionError(error.message || "تحقق من اتصال الإنترنت ثم حاول مرة أخرى.");
        } finally {
            isSubmitting = false;
            submitButton.disabled = false;
            submitButton.textContent = "عرض النتيجة";
        }
    });
}());
