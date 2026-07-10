(function () {
    "use strict";

    const rawWords = [
        ["classroom","فصل دراسي","School","Easy","🏫","I study English in the classroom.","أدرس الإنجليزية في الفصل الدراسي.","مكان يتعلم فيه الطلاب داخل المدرسة."],
        ["teacher","معلم","School","Easy","👩‍🏫","The teacher explains the lesson.","يشرح المعلم الدرس.","الشخص الذي يشرح ويساعد الطلاب على التعلم."],
        ["student","طالب","School","Easy","🎒","The student writes in the notebook.","يكتب الطالب في الدفتر.","الشخص الذي يتعلم في المدرسة أو الصف."],
        ["notebook","دفتر","Classroom","Easy","📓","I write notes in my notebook.","أكتب الملاحظات في دفتري.","دفتر يستخدمه الطالب للكتابة والمراجعة."],
        ["pencil","قلم رصاص","Classroom","Easy","✏️","I use a pencil to draw.","أستخدم قلم رصاص للرسم.","أداة كتابة يمكن مسحها بالممحاة."],
        ["ruler","مسطرة","Classroom","Easy","📏","Use a ruler to draw a straight line.","استخدم مسطرة لرسم خط مستقيم.","أداة لقياس ورسم الخطوط المستقيمة."],
        ["board","سبورة","Classroom","Easy","🧑‍🏫","The answer is on the board.","الإجابة على السبورة.","سطح يكتب عليه المعلم داخل الفصل."],
        ["lesson","درس","School","Easy","📖","The English lesson starts now.","يبدأ درس الإنجليزية الآن.","جزء تعليمي يتعلم فيه الطالب مهارة أو فكرة."],
        ["homework","واجب منزلي","School","Easy","📝","I do my homework after school.","أحل واجبي المنزلي بعد المدرسة.","عمل ينجزه الطالب في البيت للمراجعة."],
        ["dictionary","قاموس","School","Medium","📘","I use a dictionary to find new words.","أستخدم قاموسًا للعثور على كلمات جديدة.","كتاب أو تطبيق يشرح معنى الكلمات."],
        ["computer","حاسوب","Technology","Easy","💻","I use a computer to write my project.","أستخدم الحاسوب لكتابة مشروعي.","جهاز إلكتروني للعمل والتعلم والبحث."],
        ["keyboard","لوحة مفاتيح","Technology","Easy","⌨️","The keyboard has many letters.","لوحة المفاتيح فيها حروف كثيرة.","أداة نكتب بها على الحاسوب."],
        ["screen","شاشة","Technology","Easy","🖥️","Look at the screen carefully.","انظر إلى الشاشة بعناية.","جزء يعرض الصور والكلمات في الجهاز."],
        ["internet","الإنترنت","Technology","Medium","🌐","The internet helps us learn quickly.","يساعدنا الإنترنت على التعلم بسرعة.","شبكة عالمية للبحث والتواصل والتعلم."],
        ["password","كلمة مرور","Technology","Medium","🔐","Do not share your password.","لا تشارك كلمة المرور الخاصة بك.","كلمة سر تحمي حسابك ومعلوماتك."],
        ["message","رسالة","Technology","Easy","💬","I sent a message to my friend.","أرسلت رسالة إلى صديقي.","كلام مكتوب أو صوتي ترسله لشخص آخر."],
        ["website","موقع إلكتروني","Technology","Medium","🕸️","This website teaches English.","هذا الموقع يعلّم الإنجليزية.","صفحة أو مجموعة صفحات على الإنترنت."],
        ["application","تطبيق","Technology","Challenge","📱","This application helps me practice English.","هذا التطبيق يساعدني على ممارسة الإنجليزية.","برنامج على الهاتف أو الحاسوب يقدم خدمة."],
        ["happy","سعيد","Feelings","Easy","😊","I feel happy today.","أشعر بالسعادة اليوم.","شعور بالفرح والراحة."],
        ["sad","حزين","Feelings","Easy","🙁","She feels sad after the story.","تشعر بالحزن بعد القصة.","شعور بعدم الفرح أو الضيق."],
        ["tired","متعب","Feelings","Easy","😴","I am tired after football practice.","أنا متعب بعد تدريب كرة القدم.","شعور بالحاجة إلى الراحة."],
        ["worried","قلق","Feelings","Medium","😟","I feel worried before the exam.","أشعر بالقلق قبل الاختبار.","شعور بالخوف أو التفكير الزائد."],
        ["excited","متحمس","Feelings","Medium","🤩","I am excited about the trip.","أنا متحمس للرحلة.","شعور بالحماس والانتظار الجميل."],
        ["angry","غاضب","Feelings","Easy","😠","He is angry because he lost the game.","هو غاضب لأنه خسر اللعبة.","شعور بالضيق الشديد."],
        ["proud","فخور","Feelings","Medium","🏅","I am proud of my progress.","أنا فخور بتقدمي.","شعور جميل عند تحقيق إنجاز."],
        ["nervous","متوتر","Feelings","Medium","😬","I feel nervous before speaking.","أشعر بالتوتر قبل التحدث.","شعور بالارتباك قبل موقف مهم."],
        ["breakfast","فطور","Food","Easy","🥣","I eat breakfast before school.","أتناول الفطور قبل المدرسة.","وجبة الصباح الأولى."],
        ["lunch","غداء","Food","Easy","🍱","We eat lunch at noon.","نتناول الغداء وقت الظهيرة.","وجبة منتصف اليوم."],
        ["dinner","عشاء","Food","Easy","🍽️","My family eats dinner together.","تتناول عائلتي العشاء معًا.","وجبة المساء."],
        ["fruit","فاكهة","Food","Easy","🍎","Fruit is good for your body.","الفاكهة مفيدة لجسمك.","طعام طبيعي مثل التفاح والموز."],
        ["vegetables","خضروات","Food","Medium","🥦","Vegetables make meals healthy.","تجعل الخضروات الوجبات صحية.","نباتات تؤكل وتفيد الجسم."],
        ["healthy","صحي","Food","Medium","💪","Fruits are healthy food.","الفواكه طعام صحي.","شيء مفيد للجسم والعقل."],
        ["water","ماء","Food","Easy","💧","We should drink enough water.","يجب أن نشرب ماءً كافيًا.","شراب أساسي يحتاجه الجسم."],
        ["restaurant","مطعم","Food","Medium","🍽️","My family ate dinner at a restaurant.","تناولت عائلتي العشاء في مطعم.","مكان نشتري ونتناول فيه الطعام."],
        ["airport","مطار","Travel","Easy","✈️","We arrived early at the airport.","وصلنا مبكرًا إلى المطار.","مكان تسافر منه الطائرات."],
        ["ticket","تذكرة","Travel","Easy","🎫","I bought a ticket for the bus.","اشتريت تذكرة للحافلة.","ورقة أو رمز يسمح لك بالركوب أو الدخول."],
        ["suitcase","حقيبة سفر","Travel","Medium","🧳","My suitcase is heavy.","حقيبتي ثقيلة.","حقيبة نضع فيها الملابس عند السفر."],
        ["passport","جواز سفر","Travel","Medium","🛂","You need a passport to travel.","تحتاج إلى جواز سفر للسفر.","وثيقة رسمية للسفر بين الدول."],
        ["taxi","سيارة أجرة","Travel","Easy","🚕","I need a taxi to the hotel.","أحتاج سيارة أجرة إلى الفندق.","سيارة تدفع لها لتوصلك إلى مكان."],
        ["hotel","فندق","Travel","Easy","🏨","We stayed at a hotel.","أقمنا في فندق.","مكان للإقامة أثناء السفر."],
        ["direction","اتجاه","Travel","Challenge","🧭","Can you give me directions to the museum?","هل يمكنك إعطائي الاتجاهات إلى المتحف؟","إرشادات تساعدك للوصول إلى مكان."],
        ["station","محطة","Travel","Medium","🚉","The train stops at the station.","يتوقف القطار في المحطة.","مكان انتظار القطار أو الحافلة."],
        ["doctor","طبيب","Health","Easy","🩺","The doctor helped the sick child.","ساعد الطبيب الطفل المريض.","شخص يعالج المرضى."],
        ["nurse","ممرضة","Health","Easy","👩‍⚕️","The nurse gave me water.","أعطتني الممرضة ماءً.","شخص يساعد الطبيب ويعتني بالمرضى."],
        ["hospital","مستشفى","Health","Easy","🏥","The hospital is near my house.","المستشفى قريب من بيتي.","مكان لعلاج المرضى."],
        ["medicine","دواء","Health","Medium","💊","Take this medicine after lunch.","خذ هذا الدواء بعد الغداء.","شيء يساعد الجسم على الشفاء."],
        ["headache","صداع","Health","Medium","🤕","I have a headache today.","لدي صداع اليوم.","ألم في الرأس."],
        ["exercise","تمرين","Health","Medium","🏃","Exercise keeps your body strong.","التمرين يحافظ على قوة جسمك.","نشاط بدني يقوي الجسم."],
        ["clean","نظيف","Health","Easy","🧼","Keep your room clean.","حافظ على غرفتك نظيفة.","خالي من الأوساخ."],
        ["rest","راحة","Health","Easy","🛌","You should rest after school.","يجب أن ترتاح بعد المدرسة.","توقف عن التعب لتستعيد نشاطك."],
        ["mountain","جبل","Nature","Easy","⛰️","The mountain is very high.","الجبل عالٍ جدًا.","مكان طبيعي مرتفع جدًا."],
        ["river","نهر","Nature","Easy","🏞️","The river flows through the city.","يجري النهر عبر المدينة.","مجرى ماء طبيعي طويل."],
        ["sea","بحر","Nature","Easy","🌊","The sea is blue and wide.","البحر أزرق وواسع.","مساحة كبيرة من الماء المالح."],
        ["desert","صحراء","Nature","Medium","🏜️","The desert is hot and dry.","الصحراء حارة وجافة.","مكان واسع قليل الماء والنبات."],
        ["weather","الطقس","Nature","Medium","☀️","The weather is sunny today.","الطقس مشمس اليوم.","حالة الجو مثل الحرارة والمطر."],
        ["animal","حيوان","Nature","Easy","🦁","The lion is a wild animal.","الأسد حيوان بري.","كائن حي مثل القطة أو الأسد."],
        ["tree","شجرة","Nature","Easy","🌳","The tree is tall and green.","الشجرة طويلة وخضراء.","نبات كبير له جذع وأغصان."],
        ["flower","زهرة","Nature","Easy","🌸","The flower smells nice.","رائحة الزهرة جميلة.","نبات صغير جميل وله ألوان."],
        ["morning","صباح","Daily Life","Easy","🌅","I wake up in the morning.","أستيقظ في الصباح.","بداية اليوم."],
        ["evening","مساء","Daily Life","Easy","🌆","I read in the evening.","أقرأ في المساء.","وقت بعد العصر وقبل الليل."],
        ["schedule","جدول","Daily Life","Medium","🗓️","I checked my school schedule.","راجعت جدولي المدرسي.","ترتيب للأوقات والمهام."],
        ["family","عائلة","Daily Life","Easy","👨‍👩‍👧","My family eats dinner together.","تتناول عائلتي العشاء معًا.","الأب والأم والأبناء والأقارب."],
        ["friend","صديق","Daily Life","Easy","🤝","This is my best friend.","هذا صديقي المفضل.","شخص تحبه وتثق به."],
        ["responsibility","مسؤولية","Daily Life","Challenge","🎯","Cleaning your desk is your responsibility.","تنظيف مكتبك مسؤوليتك.","واجب يجب عليك الاهتمام به."],
        ["polite","مهذب","Daily Life","Medium","🙏","A polite student says please and thank you.","الطالب المهذب يقول من فضلك وشكرًا.","شخص يتكلم ويتصرف باحترام."],
        ["honest","صادق","Daily Life","Medium","✅","An honest person tells the truth.","الشخص الصادق يقول الحقيقة.","شخص لا يكذب."],
        ["market","سوق","Shopping","Easy","🛒","We bought vegetables from the market.","اشترينا خضروات من السوق.","مكان نشتري منه الأشياء."],
        ["customer","زبون","Shopping","Medium","🧑‍💼","The customer asked about the price.","سأل الزبون عن السعر.","شخص يشتري من متجر."],
        ["price","سعر","Shopping","Easy","🏷️","The price is ten riyals.","السعر عشرة ريالات.","المبلغ المطلوب لشراء شيء."],
        ["expensive","غالي","Shopping","Medium","💎","This phone is expensive.","هذا الهاتف غالي.","شيء سعره مرتفع."],
        ["cheap","رخيص","Shopping","Easy","💰","This pen is cheap.","هذا القلم رخيص.","شيء سعره منخفض."],
        ["card","بطاقة","Shopping","Easy","💳","Can I pay by card?","هل يمكنني الدفع بالبطاقة؟","بطاقة تستخدم للدفع أو التعريف."],
        ["team","فريق","Sports","Easy","⚽","Our team won the match.","فاز فريقنا بالمباراة.","مجموعة تلعب أو تعمل معًا."],
        ["goal","هدف","Sports","Easy","🥅","My goal is to improve my English.","هدفي أن أحسن لغتي الإنجليزية.","شيء تريد تحقيقه أو نقطة في اللعبة."],
        ["match","مباراة","Sports","Easy","🏟️","The match starts at five.","تبدأ المباراة الساعة الخامسة.","لعبة أو منافسة بين فريقين."],
        ["player","لاعب","Sports","Easy","🏃","The player scored a goal.","سجل اللاعب هدفًا.","شخص يلعب رياضة أو لعبة."],
        ["engineer","مهندس","Jobs","Medium","👷","The engineer designs bridges.","يصمم المهندس الجسور.","شخص يصمم ويبني أو يحل مشكلات تقنية."],
        ["doctor job","مهنة طبيب","Jobs","Challenge","🩺","A doctor helps sick people.","الطبيب يساعد المرضى.","مهنة تهتم بعلاج الناس."],
        ["future","المستقبل","Jobs","Challenge","🚀","I want to be a doctor in the future.","أريد أن أكون طبيبًا في المستقبل.","الوقت القادم في حياة الإنسان."],
        ["improve","يتحسن / يحسن","Jobs","Challenge","📈","I practice every day to improve my English.","أتدرب كل يوم لأحسن لغتي الإنجليزية.","تصبح أفضل أو تجعل الشيء أفضل."]
    ];

    const categories = ["School","Classroom","Technology","Feelings","Food","Travel","Health","Nature","Daily Life","Shopping","Sports","Jobs","Home","Time","Challenge Words"];
    const reviewKey = "abcz-vocabulary-foundation-progress-v1";
    let activeReviewOnly = false;
    let activeMasteredOnly = false;
    let gameState = {};

    const vocabularyData = rawWords.map((row, index) => {
        const [word, arabic, category, level, emoji, example, exampleAr, explanationAr] = row;
        const decoys = rawWords.filter(item => item[0] !== word).slice(index + 1, index + 4).map(item => item[0]);
        while (decoys.length < 3) decoys.push(rawWords[decoys.length][0]);
        const choices = shuffle([word, ...decoys]).slice(0, 4);
        return {
            id: `vocab-${index + 1}`,
            word,
            arabic,
            category,
            level,
            emoji,
            image_hint: emoji,
            example,
            example_ar: exampleAr,
            explanation_ar: explanationAr,
            question: `Which word matches: ${arabic}?`,
            choices,
            correct_answer: word,
            fill_blank_sentence: example.replace(new RegExp(`\\b${escapeRegExp(word)}\\b`, "i"), "____"),
            fill_blank_answer: word,
            true_false_sentence: `${word} means ${arabic}.`,
            true_false_answer: true
        };
    });

    const els = {};
    let progress = loadProgress();

    function escapeRegExp(value) {
        return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    }

    function escapeHtml(value) {
        return String(value ?? "").replace(/[&<>"']/g, char => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        }[char]));
    }

    function shuffle(items) {
        const copy = [...items];
        for (let i = copy.length - 1; i > 0; i -= 1) {
            const j = Math.floor(Math.random() * (i + 1));
            [copy[i], copy[j]] = [copy[j], copy[i]];
        }
        return copy;
    }

    function loadProgress() {
        const initial = window.VOCABULARY_INITIAL_PROGRESS || {};
        const fallback = {
            points: Number(initial.points || 0),
            actions: Number(initial.actions || 0),
            mastered: [],
            review: [],
            completed: Boolean(initial.completed)
        };
        try {
            return { ...fallback, ...JSON.parse(localStorage.getItem(reviewKey) || "{}") };
        } catch {
            return fallback;
        }
    }

    function saveProgress() {
        localStorage.setItem(reviewKey, JSON.stringify(progress));
    }

    function csrfToken() {
        return document.cookie.split(";").map(v => v.trim()).find(v => v.startsWith("csrftoken="))?.split("=")[1] || "";
    }

    async function addPoints(activityType, points, options = {}) {
        progress.points = Math.max(0, Number(progress.points || 0) + points);
        progress.actions = Math.max(0, Number(progress.actions || 0) + 1);
        if (options.masteredWord && !progress.mastered.includes(options.masteredWord)) {
            progress.mastered.push(options.masteredWord);
            progress.review = progress.review.filter(word => word !== options.masteredWord);
        }
        if (options.reviewWord && !progress.review.includes(options.reviewWord) && !progress.mastered.includes(options.reviewWord)) {
            progress.review.push(options.reviewWord);
        }
        if (progress.mastered.length >= 10 && !progress.tenBonus) {
            progress.tenBonus = true;
            progress.points += 20;
        }
        if (options.completed) progress.completed = true;
        saveProgress();
        updateStats();

        try {
            await fetch(window.VOCABULARY_PROGRESS_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
                body: JSON.stringify({
                    section: "vocabulary",
                    activity_type: activityType,
                    points,
                    completed: Boolean(options.completed)
                })
            });
        } catch {
            // localStorage remains the active fallback.
        }
    }

    function statusFromPoints(points) {
        if (points >= 150) return "متقن";
        if (points >= 80) return "ممتاز";
        if (points >= 30) return "جيد";
        return "قيد التدريب";
    }

    function updateStats() {
        els.points.textContent = progress.points || 0;
        els.actions.textContent = progress.actions || 0;
        els.status.textContent = progress.completed ? "متقن" : statusFromPoints(progress.points || 0);
        els.mastered.textContent = `${progress.mastered.length} / ${vocabularyData.length}`;
        const percent = Math.min(100, Math.round((progress.mastered.length / vocabularyData.length) * 100));
        els.progressFill.style.width = `${Math.max(percent, Math.min(100, Math.round((progress.points || 0) / 2)))}%`;
    }

    function renderCategoryOptions() {
        const present = [...new Set(vocabularyData.map(item => item.category))];
        els.category.innerHTML = `<option value="">كل التصنيفات</option>${present.map(category => `<option value="${escapeHtml(category)}">${escapeHtml(category)}</option>`).join("")}`;
    }

    function renderVocabularyCards() {
        const query = els.search.value.trim().toLowerCase();
        const category = els.category.value;
        const level = els.level.value;
        const filtered = vocabularyData.filter(item => {
            const text = `${item.word} ${item.arabic} ${item.category}`.toLowerCase();
            if (query && !text.includes(query)) return false;
            if (category && item.category !== category) return false;
            if (level && item.level !== level) return false;
            if (activeReviewOnly && !progress.review.includes(item.word)) return false;
            if (activeMasteredOnly && !progress.mastered.includes(item.word)) return false;
            return true;
        });

        els.grid.innerHTML = filtered.map(renderCard).join("");
        els.empty.hidden = filtered.length > 0;
    }

    function renderCard(item) {
        const mastered = progress.mastered.includes(item.word);
        const review = progress.review.includes(item.word);
        return `
            <article class="vf-card" data-word="${escapeHtml(item.word)}">
                <div class="vf-card-top">
                    <div class="vf-emoji" aria-hidden="true">${escapeHtml(item.emoji)}</div>
                    <div class="vf-badges">
                        <span class="vf-badge">${escapeHtml(item.category)}</span>
                        <span class="vf-badge level-${item.level}">${escapeHtml(item.level)}</span>
                    </div>
                </div>
                <div class="vf-word">${escapeHtml(item.word)}</div>
                <div class="vf-arabic">${escapeHtml(item.arabic)}</div>
                <div class="vf-explain">${escapeHtml(item.explanation_ar)}</div>
                <div class="vf-example">${escapeHtml(item.example)}</div>
                <div class="vf-example-ar">${escapeHtml(item.example_ar)}</div>
                <small>${mastered ? "تم الإتقان" : review ? "تحتاج مراجعة" : "جاهزة للتدريب"}</small>
                <div class="vf-actions">
                    <button class="vf-action train" type="button" data-action="open" data-word="${escapeHtml(item.word)}">ابدأ</button>
                    <button class="vf-action listen" type="button" data-action="listen" data-word="${escapeHtml(item.word)}">استماع</button>
                    <button class="vf-action train" type="button" data-action="training" data-word="${escapeHtml(item.word)}">حل تدريب</button>
                    <button class="vf-action mic" type="button" data-action="mic" data-word="${escapeHtml(item.word)}">مايك</button>
                    <button class="vf-action gold" type="button" data-action="flash" data-word="${escapeHtml(item.word)}">بطاقة</button>
                    <button class="vf-action review" type="button" data-action="review" data-word="${escapeHtml(item.word)}">أضف للمراجعة</button>
                </div>
            </article>
        `;
    }

    function findWord(word) {
        return vocabularyData.find(item => item.word === word);
    }

    function speakText(text, rate = 0.9) {
        try {
            if (!("speechSynthesis" in window)) {
                alert("النطق غير مدعوم في هذا المتصفح.");
                return;
            }
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = "en-US";
            utterance.rate = rate;
            window.speechSynthesis.speak(utterance);
        } catch {
            alert("تعذر تشغيل النطق الآن.");
        }
    }

    function openModal(html) {
        els.modalContent.innerHTML = html;
        els.modal.hidden = false;
    }

    function closeModal() {
        els.modal.hidden = true;
        els.modalContent.innerHTML = "";
    }

    function openWordModal(item) {
        openModal(`
            <div class="vf-emoji">${escapeHtml(item.emoji)}</div>
            <h2 id="vfModalTitle" class="vf-word">${escapeHtml(item.word)}</h2>
            <p class="vf-arabic">${escapeHtml(item.arabic)}</p>
            <p>${escapeHtml(item.explanation_ar)}</p>
            <p class="vf-example">${escapeHtml(item.example)}</p>
            <p class="vf-example-ar">${escapeHtml(item.example_ar)}</p>
            <div class="vf-actions">
                <button class="vf-action listen" type="button" data-modal-speak="${escapeHtml(item.word)}">نطق الكلمة</button>
                <button class="vf-action listen" type="button" data-modal-speak-example="${escapeHtml(item.example)}">نطق المثال</button>
                <button class="vf-action train" type="button" data-modal-training="${escapeHtml(item.word)}">سؤال سريع</button>
            </div>
        `);
        addPoints("open", 1);
    }

    function openTraining(item) {
        openModal(`
            <h2 id="vfModalTitle">تدريب: ${escapeHtml(item.word)}</h2>
            <p class="vf-explain">${escapeHtml(item.explanation_ar)}</p>
            <h3>${escapeHtml(item.question)}</h3>
            <div class="vf-options">
                ${item.choices.map(choice => `<button class="vf-option" type="button" data-answer="${escapeHtml(choice)}" data-correct="${escapeHtml(item.correct_answer)}" data-word="${escapeHtml(item.word)}">${escapeHtml(choice)}</button>`).join("")}
            </div>
            <h3>أكمل الفراغ</h3>
            <p class="vf-example">${escapeHtml(item.fill_blank_sentence)}</p>
            <input id="vfBlankAnswer" type="text" placeholder="اكتب الكلمة" style="width:100%;min-height:42px;border:1px solid var(--vf-line);border-radius:8px;padding:0 12px;">
            <button class="vf-btn primary" type="button" data-check-blank="${escapeHtml(item.word)}">تحقق</button>
            <h3>صح أو خطأ</h3>
            <p>${escapeHtml(item.true_false_sentence)}</p>
            <button class="vf-btn" type="button" data-tf="true" data-word="${escapeHtml(item.word)}">صح</button>
            <button class="vf-btn" type="button" data-tf="false" data-word="${escapeHtml(item.word)}">خطأ</button>
            <div id="vfTrainingFeedback" class="vf-explain" style="margin-top:12px;"></div>
        `);
    }

    function normalizeText(text) {
        return String(text || "").toLowerCase().replace(/[^a-z0-9\s]/g, "").replace(/\s+/g, " ").trim();
    }

    function similarityScore(original, spoken) {
        const a = normalizeText(original);
        const b = normalizeText(spoken);
        if (!a || !b) return 0;
        const aw = a.split(" ");
        const bw = new Set(b.split(" "));
        const hits = aw.filter(word => bw.has(word)).length;
        return Math.round((hits / Math.max(aw.length, 1)) * 100);
    }

    function startMicPractice(item) {
        openModal(`
            <h2 id="vfModalTitle">تدريب المايك</h2>
            <p class="vf-example">${escapeHtml(item.word)}</p>
            <div id="vfSpeechResult"></div>
        `);
        SpeechService.startRecognition({
            targetText: item.word,
            type: "word",
            section: "vocabulary",
            level: item.level || "",
            onStart: () => SpeechService.renderResult("#vfSpeechResult", { expected: item.word, spoken: SpeechService.messages.listening, score: 0, status: "retry" }),
            onResult: result => {
                SpeechService.renderResult("#vfSpeechResult", result);
                addPoints("mic", 3, { masteredWord: result.status === "excellent" ? item.word : "", reviewWord: result.status === "retry" ? item.word : "" });
                renderVocabularyCards();
            },
            onError: result => SpeechService.renderResult("#vfSpeechResult", result)
        });
        return;
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            openModal(`
                <h2 id="vfModalTitle">تدريب المايك</h2>
                <p>الميكروفون غير مدعوم في هذا المتصفح، جرّب Google Chrome.</p>
                <p class="vf-example">اقرأ الكلمة بصوت واضح: ${escapeHtml(item.word)}</p>
            `);
            return;
        }
        const recognition = new SpeechRecognition();
        recognition.lang = "en-US";
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.onresult = event => {
            const spoken = event.results[0][0].transcript;
            const score = similarityScore(item.word, spoken);
            const label = score >= 85 ? "ممتاز" : score >= 60 ? "جيد" : "حاول مرة أخرى";
            openModal(`
                <h2 id="vfModalTitle">نتيجة المايك: ${escapeHtml(label)}</h2>
                <p>الكلمة المطلوبة: <strong>${escapeHtml(item.word)}</strong></p>
                <p>قلت: <strong>${escapeHtml(spoken)}</strong></p>
                <p>نسبة التطابق: <strong>${score}%</strong></p>
            `);
            addPoints("mic", 3, { masteredWord: score >= 85 ? item.word : "", reviewWord: score < 60 ? item.word : "" });
            renderVocabularyCards();
        };
        recognition.onerror = () => openModal(`
            <h2 id="vfModalTitle">تعذر تشغيل المايك</h2>
            <p>اسمح للمتصفح باستخدام الميكروفون ثم جرّب مرة أخرى.</p>
            <p class="vf-example">الكلمة: ${escapeHtml(item.word)}</p>
        `);
        openModal(`
            <h2 id="vfModalTitle">استعد للنطق</h2>
            <p>اقرأ الكلمة بصوت واضح بعد السماح للميكروفون.</p>
            <p class="vf-example">${escapeHtml(item.word)}</p>
        `);
        recognition.start();
    }

    function handleCardAction(action, item) {
        if (action === "open") openWordModal(item);
        if (action === "listen") {
            speakText(item.word, 0.9);
            addPoints("open", 1);
        }
        if (action === "training") openTraining(item);
        if (action === "mic") startMicPractice(item);
        if (action === "flash") {
            openModal(`<h2>${escapeHtml(item.word)}</h2><p class="vf-arabic">${escapeHtml(item.arabic)}</p><p>${escapeHtml(item.example)}</p>`);
            addPoints("game", 2);
        }
        if (action === "review") {
            addPoints("open", 0, { reviewWord: item.word });
            renderVocabularyCards();
        }
    }

    function renderGame(name) {
        const sample = shuffle(vocabularyData).slice(0, name === "memory" ? 6 : 4);
        els.gamePanel.hidden = false;
        if (name === "flashcards") {
            els.gamePanel.innerHTML = `<h2>Flashcards</h2><div class="vf-game-grid">${sample.map(item => `<button class="vf-game-card" type="button" data-flip="${item.word}">${item.word}<br><small>اضغط للقلب</small></button>`).join("")}</div>`;
            return;
        }
        if (name === "match") {
            els.gamePanel.innerHTML = `<h2>Word Match</h2><p>اختر الكلمة ثم معناها. عند إكمال اللعبة تحصل على +7.</p><div class="vf-game-grid">${sample.map(item => `<button class="vf-game-card" data-match-word="${item.word}">${item.word}</button><button class="vf-game-card" data-match-meaning="${item.word}">${item.arabic}</button>`).join("")}</div>`;
            gameState.match = { selected: "", done: 0, total: sample.length };
            return;
        }
        if (name === "emoji") {
            const target = sample[0];
            els.gamePanel.innerHTML = `<h2>Emoji Choice</h2><div style="font-size:60px;">${target.emoji}</div><div class="vf-options">${sample.map(item => `<button class="vf-option" data-game-answer="${item.word}" data-game-correct="${target.word}">${item.word}</button>`).join("")}</div>`;
            return;
        }
        if (name === "listen") {
            const target = sample[0];
            speakText(target.word);
            els.gamePanel.innerHTML = `<h2>Listen and Choose</h2><p>استمع واختر المعنى الصحيح.</p><div class="vf-options">${sample.map(item => `<button class="vf-option" data-game-answer="${item.word}" data-game-correct="${target.word}">${item.arabic}</button>`).join("")}</div>`;
            return;
        }
        if (name === "blank") {
            const target = sample[0];
            els.gamePanel.innerHTML = `<h2>Fill in the Blank</h2><p class="vf-example">${target.fill_blank_sentence}</p><input id="vfGameBlank" style="width:100%;min-height:42px;border:1px solid var(--vf-line);border-radius:8px;padding:0 12px;"><button class="vf-btn primary" data-game-blank="${target.word}">تحقق</button>`;
            return;
        }
        if (name === "speed") {
            gameState.speed = { score: 0, end: Date.now() + 60000, word: sample[0] };
            els.gamePanel.innerHTML = `<h2>Speed Vocabulary Challenge</h2><p>اختر معنى أكبر عدد من الكلمات خلال 60 ثانية.</p><div id="vfSpeedBox"></div>`;
            renderSpeedQuestion();
            return;
        }
        if (name === "memory") {
            const cards = shuffle(sample.flatMap(item => [{ word: item.word, label: item.word }, { word: item.word, label: item.arabic }]));
            els.gamePanel.innerHTML = `<h2>Memory Game</h2><div class="vf-game-grid">${cards.map((card, index) => `<button class="vf-game-card" data-memory="${card.word}" data-label="${escapeHtml(card.label)}" data-index="${index}">?</button>`).join("")}</div>`;
            gameState.memory = { first: null, pairs: 0, total: sample.length };
            return;
        }
        const target = sample[0];
        els.gamePanel.innerHTML = `<h2>Word Builder</h2><p>رتب حروف الكلمة:</p><p class="vf-word">${shuffle(target.word.split("")).join(" / ")}</p><input id="vfBuilderInput" style="width:100%;min-height:42px;border:1px solid var(--vf-line);border-radius:8px;padding:0 12px;"><button class="vf-btn primary" data-builder="${target.word}">تحقق</button>`;
    }

    function renderSpeedQuestion() {
        if (Date.now() > gameState.speed.end) {
            els.gamePanel.querySelector("#vfSpeedBox").innerHTML = `<h3>النتيجة: ${gameState.speed.score}</h3>`;
            addPoints("game", 7);
            return;
        }
        const target = shuffle(vocabularyData)[0];
        const options = shuffle([target, ...shuffle(vocabularyData.filter(item => item.word !== target.word)).slice(0, 3)]);
        gameState.speed.word = target;
        els.gamePanel.querySelector("#vfSpeedBox").innerHTML = `<h3>${target.word}</h3><div class="vf-options">${options.map(item => `<button class="vf-option" data-speed="${item.word}" data-correct="${target.word}">${item.arabic}</button>`).join("")}</div><p>Score: ${gameState.speed.score}</p>`;
    }

    function handleModalClick(event) {
        const option = event.target.closest("[data-answer]");
        if (option) {
            const correct = option.dataset.answer === option.dataset.correct;
            option.classList.add(correct ? "correct" : "wrong");
            addPoints("exercise", correct ? 5 : 0, { masteredWord: correct ? option.dataset.word : "", reviewWord: correct ? "" : option.dataset.word });
            document.getElementById("vfTrainingFeedback").textContent = correct ? "إجابة صحيحة +5" : "راجع الكلمة مرة أخرى.";
            renderVocabularyCards();
        }
        const blank = event.target.closest("[data-check-blank]");
        if (blank) {
            const word = blank.dataset.checkBlank;
            const answer = document.getElementById("vfBlankAnswer").value.trim().toLowerCase();
            const correct = answer === word.toLowerCase();
            addPoints("exercise", correct ? 5 : 0, { masteredWord: correct ? word : "", reviewWord: correct ? "" : word });
            document.getElementById("vfTrainingFeedback").textContent = correct ? "ممتاز، إجابة صحيحة." : `الإجابة الصحيحة: ${word}`;
            renderVocabularyCards();
        }
        const tf = event.target.closest("[data-tf]");
        if (tf) {
            addPoints("exercise", 5, { masteredWord: tf.dataset.word });
            document.getElementById("vfTrainingFeedback").textContent = "صحيح، هذه الجملة صحيحة.";
            renderVocabularyCards();
        }
        const speak = event.target.closest("[data-modal-speak]");
        if (speak) speakText(speak.dataset.modalSpeak);
        const speakExample = event.target.closest("[data-modal-speak-example]");
        if (speakExample) speakText(speakExample.dataset.modalSpeakExample, 0.85);
        const training = event.target.closest("[data-modal-training]");
        if (training) openTraining(findWord(training.dataset.modalTraining));
    }

    function handleGameClick(event) {
        const flip = event.target.closest("[data-flip]");
        if (flip) {
            const item = findWord(flip.dataset.flip);
            flip.innerHTML = `${item.arabic}<br><small>${item.example}</small>`;
            addPoints("game", 1);
        }
        const answer = event.target.closest("[data-game-answer]");
        if (answer) {
            const correct = answer.dataset.gameAnswer === answer.dataset.gameCorrect;
            answer.classList.add(correct ? "correct" : "wrong");
            if (correct) addPoints("game", 7, { masteredWord: answer.dataset.gameCorrect });
        }
        const blank = event.target.closest("[data-game-blank]");
        if (blank) {
            const correct = document.getElementById("vfGameBlank").value.trim().toLowerCase() === blank.dataset.gameBlank.toLowerCase();
            alert(correct ? "ممتاز +7" : `الإجابة: ${blank.dataset.gameBlank}`);
            if (correct) addPoints("game", 7, { masteredWord: blank.dataset.gameBlank });
        }
        const builder = event.target.closest("[data-builder]");
        if (builder) {
            const correct = document.getElementById("vfBuilderInput").value.trim().toLowerCase() === builder.dataset.builder.toLowerCase();
            alert(correct ? "ممتاز +7" : `الإجابة: ${builder.dataset.builder}`);
            if (correct) addPoints("game", 7, { masteredWord: builder.dataset.builder });
        }
        const speed = event.target.closest("[data-speed]");
        if (speed) {
            if (speed.dataset.speed === speed.dataset.correct) gameState.speed.score += 1;
            renderSpeedQuestion();
        }
        const matchWord = event.target.closest("[data-match-word]");
        if (matchWord) {
            gameState.match.selected = matchWord.dataset.matchWord;
            matchWord.classList.add("done");
        }
        const matchMeaning = event.target.closest("[data-match-meaning]");
        if (matchMeaning && gameState.match?.selected) {
            const correct = gameState.match.selected === matchMeaning.dataset.matchMeaning;
            matchMeaning.classList.add(correct ? "done" : "wrong");
            if (correct) {
                gameState.match.done += 1;
                if (gameState.match.done >= gameState.match.total) addPoints("game", 7);
            }
            gameState.match.selected = "";
        }
        const memory = event.target.closest("[data-memory]");
        if (memory && gameState.memory) {
            memory.textContent = memory.dataset.label;
            if (!gameState.memory.first) {
                gameState.memory.first = memory;
            } else {
                const first = gameState.memory.first;
                const correct = first.dataset.memory === memory.dataset.memory && first.dataset.index !== memory.dataset.index;
                if (correct) {
                    first.classList.add("done");
                    memory.classList.add("done");
                    gameState.memory.pairs += 1;
                    if (gameState.memory.pairs >= gameState.memory.total) addPoints("game", 7);
                } else {
                    setTimeout(() => {
                        first.textContent = "?";
                        memory.textContent = "?";
                    }, 700);
                }
                gameState.memory.first = null;
            }
        }
    }

    function bindEvents() {
        els.search.addEventListener("input", renderVocabularyCards);
        els.category.addEventListener("change", renderVocabularyCards);
        els.level.addEventListener("change", renderVocabularyCards);
        document.querySelectorAll("[data-filter-level]").forEach(button => {
            button.addEventListener("click", () => {
                els.level.value = button.dataset.filterLevel;
                activeReviewOnly = false;
                activeMasteredOnly = false;
                renderVocabularyCards();
            });
        });
        document.getElementById("vfReviewOnly").addEventListener("click", () => {
            activeReviewOnly = !activeReviewOnly;
            activeMasteredOnly = false;
            renderVocabularyCards();
        });
        document.getElementById("vfMasteredOnly").addEventListener("click", () => {
            activeMasteredOnly = !activeMasteredOnly;
            activeReviewOnly = false;
            renderVocabularyCards();
        });
        els.grid.addEventListener("click", event => {
            const button = event.target.closest("[data-action]");
            if (!button) return;
            handleCardAction(button.dataset.action, findWord(button.dataset.word));
        });
        els.modal.addEventListener("click", event => {
            if (event.target === els.modal) closeModal();
            handleModalClick(event);
        });
        document.getElementById("vfModalClose").addEventListener("click", closeModal);
        document.querySelectorAll("[data-game]").forEach(button => {
            button.addEventListener("click", () => renderGame(button.dataset.game));
        });
        els.gamePanel.addEventListener("click", handleGameClick);
        document.getElementById("vfCompleteSection").addEventListener("click", () => {
            addPoints("complete", 50, { completed: true });
        });
    }

    document.addEventListener("DOMContentLoaded", () => {
        els.grid = document.getElementById("vfGrid");
        els.empty = document.getElementById("vfEmpty");
        els.search = document.getElementById("vfSearch");
        els.category = document.getElementById("vfCategory");
        els.level = document.getElementById("vfLevel");
        els.points = document.getElementById("vfPoints");
        els.actions = document.getElementById("vfActions");
        els.status = document.getElementById("vfStatus");
        els.mastered = document.getElementById("vfMastered");
        els.progressFill = document.getElementById("vfProgressFill");
        els.modal = document.getElementById("vfModal");
        els.modalContent = document.getElementById("vfModalContent");
        els.gamePanel = document.getElementById("vfGamePanel");
        renderCategoryOptions();
        updateStats();
        renderVocabularyCards();
        bindEvents();
    });
})();
