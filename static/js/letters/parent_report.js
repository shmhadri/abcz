(function (window) {
    "use strict";

    // Parent report modal, sharing, download and print. Extracted verbatim
    // from the inline script in templates/letters.html; wording, WhatsApp
    // formatting and the recommendation rules are unchanged.
    let LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");
    let LETTER_DATA = {};
    let LEVEL_ONE_DISABLED_FEATURES = {};

    class LettersParentReport {
        showParentReport(letter, entry) {
            if (LEVEL_ONE_DISABLED_FEATURES.parentReport) {
                this.showToast('تقرير ولي الأمر غير متاح في هذه الباقة.', 3000, 'info');
                return;
            }
            if (!this.parentReportModal) return;

            const letterData = LETTER_DATA[letter] || { words: [] };
            const practicedWords = Object.keys(entry?.exercises?.words || {}).length || letterData.words.length || 0;
            const currentScore = entry?.score || this.getCurrentLetterTotalScore();
            const practicedWordList = this.getWordsPracticedForLetter ? this.getWordsPracticedForLetter(letter, entry) : [];
            const mistakes = this.getLetterMistakes ? this.getLetterMistakes(letter, entry) : { quiz: [], missing_words: [] };
            const needsPractice = (mistakes.quiz?.length || 0) > 0 || (mistakes.missing_words?.length || 0) > 0;

            if (this.parentReportLetter) this.parentReportLetter.textContent = letter;
            if (this.parentReportWords) this.parentReportWords.textContent = practicedWords;
            if (this.parentReportScore) this.parentReportScore.textContent = currentScore;

            if (this.parentReportChildMessage) {
                this.parentReportChildMessage.textContent = `أحسنت! أكملت حرف ${letter} وتدربت على كلمات جديدة. استمر بنفس الحماس.`;
            }

            if (this.parentReportParentMessage) {
                this.parentReportParentMessage.textContent = `الطالب أنهى حرف ${letter} بنجاح. التقرير الكامل يساعدك على متابعة التقدم، معرفة المهارات التي تحتاج دعمًا، وبناء تدريب يومي قصير.`;
            }

            if (this.parentReportPracticedWords) {
                const wordsText = practicedWordList.length ? practicedWordList.join(' - ') : 'لا توجد كلمات محفوظة بعد.';
                this.parentReportPracticedWords.textContent = `الكلمات التي تدرب عليها: ${wordsText}`;
            }

            if (this.parentReportNeedsPractice) {
                this.parentReportNeedsPractice.textContent = needsPractice
                    ? 'يحتاج مراجعة قصيرة لبعض الكلمات أو أسئلة الاختبار.'
                    : 'لا يحتاج مراجعة إضافية الآن. مراجعة خفيفة تكفي للتثبيت.';
            }

            if (this.parentReportRecommendation) {
                this.parentReportRecommendation.textContent = this.getParentReportRecommendation(entry);
            }

            this.parentReportState = {
                letter,
                entry: entry || this.ensureLetterRecord(letter),
                practicedWords,
                score: currentScore,
                words: practicedWordList,
                needsPractice,
                recommendation: this.parentReportRecommendation?.textContent || this.getParentReportRecommendation(entry)
            };

            this.parentReportModal.style.display = 'flex';
        }

        hideParentReport() {
            if (this.parentReportModal) {
                this.parentReportModal.style.display = 'none';
            }
        }

        backFromParentReport() {
            const state = this.parentReportState || {};
            this.hideParentReport();
            if (state.letter && typeof this.showLetterCompletion === 'function') {
                this.showLetterCompletion(state.letter, state.entry);
            }
        }

        buildCurrentLetterReportText() {
            const state = this.parentReportState || {};
            const letter = state.letter || this.progress.currentLetter || LETTERS[this.currentLetterIndex] || 'A';
            const entry = state.entry || this.ensureLetterRecord(letter);
            const letterData = LETTER_DATA[letter] || { words: [] };
            const words = state.words?.length
                ? state.words
                : (letterData.words || []).map(item => item.word).filter(Boolean);
            const score = state.score ?? entry?.score ?? this.getCurrentLetterTotalScore();
            const practicedCount = state.practicedWords ?? words.length;
            const reviewText = state.needsPractice
                ? 'يحتاج مراجعة قصيرة لبعض الكلمات أو أسئلة الاختبار.'
                : 'لا يحتاج مراجعة إضافية الآن. مراجعة خفيفة تكفي للتثبيت.';
            const recommendation = state.recommendation || this.getParentReportRecommendation(entry);
            const studentName = this.studentName || 'الطالب';
            const today = new Date().toLocaleDateString('ar-SA');

            return [
                'تقرير إنهاء حرف',
                `التاريخ: ${today}`,
                `الطالب: ${studentName}`,
                `الحرف: ${letter}`,
                `الدرجة: ${score}`,
                `عدد الكلمات المتدرب عليها: ${practicedCount}`,
                `الكلمات: ${words.length ? words.join(' - ') : 'لا توجد كلمات محفوظة بعد'}`,
                `حالة المراجعة: ${reviewText}`,
                `توصية قصيرة: ${recommendation}`,
                '',
                'Phonics Game Lab'
            ].join('\n');
        }

        shareCurrentLetterReportWhatsapp() {
            const message = this.buildCurrentLetterReportText();
            const phone = String(this.parentPhone || '').replace(/[^\d]/g, '');
            const target = phone ? `https://wa.me/${phone}?text=${encodeURIComponent(message)}` : `https://wa.me/?text=${encodeURIComponent(message)}`;
            window.open(target, '_blank', 'noopener,noreferrer');
            this.showToast('تم فتح واتساب لمشاركة تقرير الحرف الحالي.', 2500, 'success');
        }

        downloadCurrentLetterReport() {
            const letter = this.parentReportState?.letter || this.progress.currentLetter || 'A';
            const blob = new Blob([this.buildCurrentLetterReportText()], { type: 'text/plain;charset=utf-8' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `letter-${letter}-parent-report.txt`;
            document.body.appendChild(link);
            link.click();
            URL.revokeObjectURL(link.href);
            link.remove();
            this.showToast('تم تنزيل تقرير الحرف الحالي.', 2500, 'success');
        }

        printCurrentLetterReport() {
            const reportText = this.buildCurrentLetterReportText()
                .split('\n')
                .map(line => `<p>${line.replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[char]))}</p>`)
                .join('');
            const printWindow = window.open('', '_blank', 'width=820,height=900');
            if (!printWindow) {
                this.showToast('اسمح بفتح النوافذ المنبثقة لطباعة التقرير.', 3000, 'warning');
                return;
            }
            printWindow.document.write(`
                <!doctype html>
                <html lang="ar" dir="rtl">
                <head>
                    <meta charset="utf-8">
                    <title>تقرير الحرف الحالي</title>
                    <style>
                        body { font-family: Arial, sans-serif; padding: 28px; color: #172033; line-height: 1.7; }
                        .report { border: 2px solid #4361ee; border-radius: 14px; padding: 22px; }
                        p { margin: 8px 0; font-size: 18px; font-weight: 700; }
                        p:first-child { color: #4361ee; font-size: 28px; text-align: center; }
                    </style>
                </head>
                <body><div class="report">${reportText}</div></body>
                </html>
            `);
            printWindow.document.close();
            printWindow.focus();
            printWindow.print();
        }

        getParentReportRecommendation(entry) {
            const writing = entry?.exercises?.writing || {};
            const writingCount = ['capital', 'small', 'dragCapital', 'dragSmall'].reduce((total, key) => {
                return total + Object.keys(writing[key] || {}).length;
            }, 0);
            const quizScore = entry?.exercises?.quiz?.score || 0;

            if (writingCount < (this.MAX_WRITING_SCORE || 14)) {
                return 'ركز اليوم على كتابة الحرف الكبير والصغير 3 مرات ببطء ووضوح.';
            }

            if (quizScore < 4) {
                return 'راجع الكلمات مع الصور ثم أعد الاختبار بعد استراحة قصيرة.';
            }

            return 'راجع نطق الكلمات بصوت عال ثم اكتب الحرف 3 مرات لتعزيز التثبيت.';
        }
    }

    window.installLettersParentReport = function installLettersParentReport(GameClass) {
        if (!GameClass || !GameClass.prototype) return;

        LETTERS = window.LETTERS || LETTERS;
        LETTER_DATA = window.LETTER_DATA || LETTER_DATA;
        LEVEL_ONE_DISABLED_FEATURES = window.LEVEL_ONE_DISABLED_FEATURES || LEVEL_ONE_DISABLED_FEATURES;

        Object.getOwnPropertyNames(LettersParentReport.prototype).forEach(name => {
            if (name !== "constructor") {
                GameClass.prototype[name] = LettersParentReport.prototype[name];
            }
        });
    };
})(window);
