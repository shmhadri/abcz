(function (window) {
    "use strict";

    // Printable A4 worksheet builder. Extracted verbatim from the inline
    // script in templates/letters.html; the generated layout is unchanged.
    let LETTER_DATA = {};

    class LettersWorksheet {
        generateWorksheet(letter) {
            const letterData = LETTER_DATA[letter];
            if (!letterData) return;

            this.showToast('جاري إعداد ورقة العمل... 📄', 2000);

            // إنشاء حاوية ورقة العمل - نجعلها ظاهرة (Overlay) لضمان التقاطها
            const worksheetContainer = document.createElement('div');
            worksheetContainer.className = 'worksheet-overlay';

            worksheetContainer.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 99999;
                background: rgba(0,0,0,0.8);
                overflow-y: auto;
                padding: 20px;
                box-sizing: border-box;
                display: flex;
                justify-content: center;
                align-items: flex-start;
            `;

            const wordsList = letterData.words;

            // دالة مساعدة لإنشاء خطوط التتبع
            const createTracingLine = (text, count) => {
                return Array(count).fill(text).join('     ');
            };

            // المحتوى الفعلي للورقة (A4) - تصميم احترافي ومضغوط
            const content = document.createElement('div');
            content.id = 'pdf-content';
            content.style.cssText = `
                width: 210mm;
                min-height: 297mm;
                padding: 10mm;
                background: white;
                box-shadow: 0 0 20px rgba(0,0,0,0.5);
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                direction: ltr;
                color: black;
                position: relative;
                margin-bottom: 50px;
            `;

            content.innerHTML = `
                <div style="border: 2px solid #4361ee; border-radius: 15px; height: 100%; padding: 15px; box-sizing: border-box; position: relative; overflow: hidden;">

                    <!-- Decorative Corner -->
                    <div style="position: absolute; top: -20px; right: -20px; width: 80px; height: 80px; background: #4361ee; transform: rotate(45deg); z-index: 0;"></div>

                    <!-- Header -->
                    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px dashed #cbd5e1; padding-bottom: 10px; margin-bottom: 15px; position: relative; z-index: 1;">
                        <div style="display: flex; align-items: center; gap: 15px;">
                            <div style="width: 50px; height: 50px; background: #4361ee; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24pt; font-weight: bold;">${letter}</div>
                            <div>
                                <h1 style="margin: 0; color: #1e293b; font-size: 20pt; font-weight: 800;">Phonics Worksheet</h1>
                                <p style="margin: 0; color: #64748b; font-size: 10pt;">Learn the letter ${letter}</p>
                            </div>
                        </div>
                        <div style="text-align: right; font-size: 10pt; color: #334155;">
                            <div style="margin-bottom: 5px; background: #f1f5f9; padding: 5px 10px; border-radius: 5px; width: 180px; display: flex; justify-content: space-between;">
                                <span>Name:</span>
                                <span style="border-bottom: 1px solid #94a3b8; width: 100px;"></span>
                            </div>
                            <div style="background: #f1f5f9; padding: 5px 10px; border-radius: 5px; width: 180px; display: flex; justify-content: space-between;">
                                <span>Date:</span>
                                <span style="border-bottom: 1px solid #94a3b8; width: 100px;"></span>
                            </div>
                        </div>
                    </div>

                    <!-- 1. Coloring & Introduction -->
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                        <div style="background: #f8fafc; padding: 10px; border-radius: 12px; border: 1px solid #e2e8f0; text-align: center;">
                            <h3 style="color: #f72585; margin: 0 0 5px; font-size: 11pt; text-align: left; display: flex; align-items: center; gap: 5px;"><i class="fas fa-paint-brush"></i> Color:</h3>
                            <div style="display: flex; justify-content: center; gap: 15px; align-items: center; height: 80px;">
                                <div style="font-size: 65pt; font-weight: 900; color: white; -webkit-text-stroke: 2px #1e293b; line-height: 1;">${letter}</div>
                                <div style="font-size: 65pt; font-weight: 900; color: white; -webkit-text-stroke: 2px #1e293b; line-height: 1;">${letter.toLowerCase()}</div>
                            </div>
                        </div>
                        <div style="background: #f0f9ff; padding: 10px; border-radius: 12px; border: 1px solid #bae6fd; display: flex; align-items: center; justify-content: space-around;">
                            <div style="font-size: 50pt;">${wordsList[0].emoji}</div>
                            <div style="text-align: center;">
                                <div style="font-size: 24pt; font-weight: 900; color: white; -webkit-text-stroke: 1.5px #0284c7; font-family: 'Courier New', monospace; letter-spacing: 2px;">${wordsList[0].word.toUpperCase()}</div>
                                <div style="font-size: 10pt; color: #0284c7; margin-top: 5px;">${wordsList[0].word} starts with ${letter}</div>
                            </div>
                        </div>
                    </div>

                    <!-- 2. Tracing Section -->
                    <div style="margin-bottom: 15px; background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 10px 15px;">
                        <h3 style="color: #f72585; margin: 0 0 10px; font-size: 11pt; display: flex; align-items: center; gap: 5px;"><i class="fas fa-pen"></i> Trace and Write:</h3>
                        <div style="font-family: 'Courier New', monospace; font-size: 26pt; color: #cbd5e1; letter-spacing: 8px; line-height: 1.4;">
                            <div style="border-bottom: 1px solid #94a3b8; margin-bottom: 8px; height: 38px; display: flex; align-items: flex-end;">
                                <span style="color: #1e293b; margin-right: 15px; font-weight: bold;">${letter}</span>
                                ${createTracingLine(letter, 7)}
                            </div>
                            <div style="border-bottom: 1px solid #94a3b8; margin-bottom: 8px; height: 38px; display: flex; align-items: flex-end;">
                                <span style="color: #1e293b; margin-right: 15px; font-weight: bold;">${letter.toLowerCase()}</span>
                                ${createTracingLine(letter.toLowerCase(), 7)}
                            </div>
                            <div style="border-bottom: 1px solid #94a3b8; height: 38px; display: flex; align-items: flex-end;">
                                <span style="color: #1e293b; margin-right: 15px; font-weight: bold;">${letter}${letter.toLowerCase()}</span>
                                ${createTracingLine(letter + letter.toLowerCase(), 6)}
                            </div>
                        </div>
                    </div>

                    <!-- 3. Vocabulary Tracing -->
                    <div style="margin-bottom: 15px;">
                        <h3 style="color: #f72585; margin: 0 0 10px; font-size: 11pt; display: flex; align-items: center; gap: 5px;"><i class="fas fa-book"></i> Trace the Words:</h3>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px 15px;">
                            ${wordsList.slice(0, 8).map(w => `
                                <div style="display: flex; align-items: center; gap: 10px; background: #f8fafc; padding: 5px 10px; border-radius: 8px; border: 1px dashed #cbd5e1;">
                                    <span style="font-size: 18pt;">${w.emoji}</span>
                                    <span style="font-family: 'Courier New', monospace; font-size: 18pt; color: #cbd5e1; font-weight: bold; letter-spacing: 1px; flex: 1; text-align: center;">${w.word}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>

                    <!-- 4. Fun Activity: Find & Circle -->
                    <div style="margin-bottom: 10px; background: #fff0f5; padding: 10px 15px; border-radius: 12px; border: 1px solid #fbcfe8;">
                        <h3 style="color: #db2777; margin: 0 0 10px; font-size: 11pt; display: flex; align-items: center; gap: 5px;"><i class="fas fa-search"></i> Find and Circle the letter '${letter}':</h3>
                        <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; font-family: 'Comic Sans MS', cursive; font-size: 16pt; color: #475569;">
                            ${Array(14).fill(0).map(() => {
                                const isTarget = Math.random() > 0.6;
                                const char = isTarget ? letter : String.fromCharCode(65 + Math.floor(Math.random() * 26));
                                return `<span style="width: 30px; height: 30px; display: flex; align-items: center; justify-content: center;">${char}</span>`;
                            }).join('')}
                        </div>
                    </div>

                    <!-- Footer -->
                    <div style="position: absolute; bottom: 10px; left: 0; width: 100%; text-align: center;">
                        <div style="font-size: 9pt; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 5px; margin: 0 20px;">
                            Great Job! ⭐ Phonics Game Lab
                        </div>
                    </div>
                </div>
            `;

            // إضافة رسالة تحميل وزر إغلاق
            const loadingMsg = document.createElement('div');
            loadingMsg.innerHTML = `
                <div style="position: fixed; top: 20px; left: 50%; transform: translateX(-50%); background: #4361ee; color: white; padding: 10px 20px; border-radius: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.2); z-index: 100001; display: flex; align-items: center; gap: 10px;">
                    <i class="fas fa-spinner fa-spin"></i> جاري إنشاء ملف PDF...
                </div>
            `;

            const closeBtn = document.createElement('button');
            closeBtn.innerHTML = '<i class="fas fa-times"></i> إغلاق';
            closeBtn.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 100001;
                padding: 10px 20px;
                background: #ef4444;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.2);
            `;
            closeBtn.onclick = () => document.body.removeChild(worksheetContainer);

            worksheetContainer.appendChild(loadingMsg);
            worksheetContainer.appendChild(closeBtn);
            worksheetContainer.appendChild(content);
            document.body.appendChild(worksheetContainer);

            const opt = {
                margin: 0,
                filename: `Worksheet_Letter_${letter}.pdf`,
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 2, useCORS: true, scrollY: 0 },
                jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
            };

            // تأخير بسيط للسماح للمتصفح برسم العناصر
            setTimeout(() => {
                html2pdf().set(opt).from(content).save().then(() => {
                    document.body.removeChild(worksheetContainer);
                    this.showToast('تم تحميل ورقة العمل بنجاح! 🎉', 3000, 'success');
                }).catch(err => {
                    console.error(err);
                    this.showToast('حدث خطأ أثناء إنشاء الملف', 3000, 'error');
                });
            }, 1000);
        }

        generateRandomLettersString(targetLetter) {
            const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
            let result = [];
            for (let i = 0; i < 30; i++) {
                if (Math.random() < 0.2) {
                    result.push(Math.random() > 0.5 ? targetLetter : targetLetter.toLowerCase());
                } else {
                    result.push(chars.charAt(Math.floor(Math.random() * chars.length)));
                }
            }
            return result.join(' ');
        }
    }

    window.installLettersWorksheet = function installLettersWorksheet(GameClass) {
        if (!GameClass || !GameClass.prototype) return;

        LETTER_DATA = window.LETTER_DATA || LETTER_DATA;

        Object.getOwnPropertyNames(LettersWorksheet.prototype).forEach(name => {
            if (name !== "constructor") {
                GameClass.prototype[name] = LettersWorksheet.prototype[name];
            }
        });
    };
})(window);
