(() => {
  const stepButtons = [...document.querySelectorAll('[data-rich-step]')];
  const panels = [...document.querySelectorAll('[data-rich-panel]')];
  const showPanel = (name) => {
    stepButtons.forEach((button) => { const active = button.dataset.richStep === name; button.classList.toggle('active', active); button.setAttribute('aria-selected', String(active)); button.tabIndex = active ? 0 : -1; });
    panels.forEach((panel) => { const active = panel.dataset.richPanel === name; panel.classList.toggle('active', active); panel.setAttribute('aria-hidden', String(!active)); });
    document.querySelector('.rich-steps')?.scrollIntoView({behavior: 'smooth', block: 'start'});
  };
  stepButtons.forEach((button, index) => { button.setAttribute('role', 'tab'); button.addEventListener('click', () => showPanel(button.dataset.richStep)); button.addEventListener('keydown', (event) => { if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return; event.preventDefault(); const offset = event.key === 'ArrowLeft' ? 1 : -1; const target = stepButtons[(index + offset + stepButtons.length) % stepButtons.length]; showPanel(target.dataset.richStep); target.focus(); }); });
  panels.forEach((panel) => panel.setAttribute('role', 'tabpanel'));
  if (stepButtons[0]) showPanel(stepButtons[0].dataset.richStep);
  document.querySelectorAll('.rich-next').forEach((button) => button.addEventListener('click', () => {
    const current = button.closest('[data-rich-panel]');
    const next = panels[panels.indexOf(current) + 1];
    if (next) showPanel(next.dataset.richPanel);
  }));

  document.querySelectorAll('.mini-check').forEach((activity) => {
    const buttons = [...activity.querySelectorAll('.choice-row button, :scope > button')];
    buttons.forEach((button) => button.addEventListener('click', () => {
      const correct = button.textContent.trim() === activity.dataset.answer;
      buttons.forEach((item) => { item.disabled = true; item.classList.toggle('correct', item.textContent.trim() === activity.dataset.answer); });
      button.classList.toggle('wrong', !correct);
      const feedback = activity.querySelector('.activity-feedback') || activity.nextElementSibling;
      if (feedback) feedback.textContent = correct ? `✓ صحيح. ${activity.dataset.explanation || ''}` : `ليست بعد. الإجابة الصحيحة: ${activity.dataset.answer}. ${activity.dataset.explanation || ''}`;
    }));
  });

  const dialogueNode = document.querySelector('#unit-dialogue, #a1-dialogue');
  document.querySelectorAll('[data-dialogue-play]').forEach((button) => button.addEventListener('click', () => {
    if (!dialogueNode || !('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    JSON.parse(dialogueNode.textContent).forEach((line, index) => {
      const utterance = new SpeechSynthesisUtterance(line);
      utterance.lang = 'en-US'; utterance.rate = .86; utterance.pitch = index % 2 ? 1.08 : .94;
      window.speechSynthesis.speak(utterance);
    });
  }));

  document.querySelectorAll('.save-word').forEach((button) => button.addEventListener('click', () => {
    const saved = button.classList.toggle('saved');
    button.textContent = saved ? '♥ محفوظة' : '♡ احفظها';
  }));
  document.querySelectorAll('.arabic-toggle').forEach((button) => button.addEventListener('click', () => {
    const card = button.closest('.rich-word') || button.parentElement;
    const help = [...card.querySelectorAll('.arabic-help')];
    const shouldShow = help.some((item) => item.hidden);
    help.forEach((item) => { item.hidden = !shouldShow; });
    button.setAttribute('aria-expanded', String(shouldShow));
    button.textContent = shouldShow ? 'أخفِ المساعدة' : (button.closest('.rich-word') ? 'أظهر المساعدة' : 'أظهر الشرح العربي');
  }));
  const textarea = document.querySelector('.writing-area textarea');
  textarea?.addEventListener('input', () => { document.querySelector('[data-char-count]').textContent = textarea.value.length; });

  document.querySelectorAll('[data-game-tab]').forEach((button) => button.addEventListener('click', () => {
    document.querySelectorAll('.skill-game').forEach((game) => game.classList.toggle('active', game.dataset.game === button.dataset.gameTab));
  }));
  let matchKey = '';
  document.querySelectorAll('[data-match-key]').forEach((button) => button.addEventListener('click', () => {
    document.querySelectorAll('[data-match-key]').forEach((item) => item.classList.remove('selected'));
    matchKey = button.dataset.matchKey; button.classList.add('selected');
  }));
  document.querySelectorAll('[data-match-value]').forEach((button) => button.addEventListener('click', () => {
    const feedback = button.closest('.skill-game').querySelector('.game-feedback');
    if (!matchKey) { feedback.textContent = 'اختر كلمة إنجليزية أولًا.'; return; }
    if (button.dataset.matchValue === matchKey) {
      button.classList.add('matched'); document.querySelector(`[data-match-key="${matchKey}"]`).classList.add('matched');
      feedback.textContent = '✓ تطابق صحيح!'; matchKey = '';
    } else { button.classList.add('shake'); feedback.textContent = 'حاول مرة أخرى. انطق الكلمة وابحث عن معناها.'; setTimeout(() => button.classList.remove('shake'), 350); }
  }));
  const built = document.querySelector('.built-sentence');
  const tokenButtons = [...document.querySelectorAll('.token-bank button')];
  tokenButtons.forEach((button) => button.addEventListener('click', () => { button.disabled = true; const token = document.createElement('button'); token.type = 'button'; token.textContent = button.textContent; token.addEventListener('click', () => { button.disabled = false; token.remove(); }); built.append(token); }));
  document.querySelector('[data-reset-builder]')?.addEventListener('click', () => { built.replaceChildren(); tokenButtons.forEach((button) => { button.disabled = false; }); });
  document.querySelector('[data-check-builder]')?.addEventListener('click', (event) => { const answer = [...built.children].map((item) => item.textContent).join(' '); const expected = event.currentTarget.dataset.builderAnswer || 'My name is Sara.'; document.querySelector('[data-game="sentence-builder"] .game-feedback').textContent = answer === expected ? '✓ جملة صحيحة!' : `حاول مرة أخرى. الهدف: ${expected}`; });

  document.querySelector('[data-check-mission]')?.addEventListener('click', () => {
    const checks = [...document.querySelectorAll('.mission-steps input')]; const completed = checks.filter((item) => item.checked).length;
    document.querySelector('.mission-status').textContent = completed === checks.length ? '🏆 أنجزت المهمة كاملة. أنت جاهز للاختبار!' : `أنجزت ${completed} من ${checks.length}. أكمل الخطوات قبل الاختبار.`;
  });

  const quiz = document.querySelector('.unit-quiz');
  const csrf = () => quiz?.querySelector('[name=csrfmiddlewaretoken]').value || '';
  const addText = (parent, tag, className, value) => { const node = document.createElement(tag); node.className = className; node.textContent = value; parent.append(node); return node; };
  const renderSimilar = (container, similar) => {
    const box = document.createElement('div'); box.className = 'similar-question'; addText(box, 'b', '', '🎯 جرّب سؤالًا مشابهًا'); addText(box, 'p', '', similar.prompt);
    const options = document.createElement('div'); options.className = 'choice-row';
    similar.choices.forEach((choice) => { const button = document.createElement('button'); button.type = 'button'; button.textContent = choice; button.addEventListener('click', async () => {
      options.querySelectorAll('button').forEach((item) => { item.disabled = true; });
      const response = await fetch(quiz.dataset.similarUrl, {method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrf()}, body: JSON.stringify({question_id: similar.id, answer: choice})}); const result = await response.json();
      addText(box, 'p', result.correct ? 'correct-note' : 'wrong-note', result.correct ? `✓ صحيح. ${result.explanation}` : `الإجابة الصحيحة: ${result.correct_answer}. ${result.explanation}`);
    }); options.append(button); }); box.append(options); container.append(box);
  };
  quiz?.addEventListener('submit', async (event) => {
    event.preventDefault(); const answers = Object.fromEntries(new FormData(quiz).entries()); delete answers.csrfmiddlewaretoken;
    const submit = quiz.querySelector('[type=submit]'); submit.disabled = true; submit.textContent = 'جاري تحليل مهاراتك…';
    const response = await fetch(quiz.dataset.quizUrl, {method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrf()}, body: JSON.stringify({answers})}); const result = await response.json();
    if (!response.ok) { submit.disabled = false; submit.textContent = 'حاول التصحيح مجددًا'; return; }
    result.feedback.forEach((item) => {
      const fieldset = quiz.querySelector(`[data-question-id="${item.id}"]`); const box = fieldset.querySelector('.why-feedback'); box.replaceChildren(); box.className = `why-feedback ${item.correct ? 'answer-correct' : 'answer-wrong'}`;
      addText(box, 'b', '', item.correct ? '✓ إجابة صحيحة' : `✕ اخترت: ${item.selected || 'لم تختر'}`); if (!item.correct) addText(box, 'p', 'correct-answer', `الصحيح: ${item.correct_answer}`); addText(box, 'p', '', `لماذا؟ ${item.why}`); if (!item.correct && item.clue) addText(box, 'p', '', `🔎 الدليل: ${item.clue}`);
      if (!item.correct) { addText(box, 'p', '', `لماذا اختيارك خطأ؟ ${item.why_wrong}`); renderSimilar(box, item.similar); }
    });
    const summary = document.querySelector('.quiz-summary'); const unitCode = document.querySelector('[data-unit-code]')?.dataset.unitCode || ''; summary.hidden = false; summary.replaceChildren(); addText(summary, 'strong', 'summary-score', `${result.score}%`); addText(summary, 'h2', '', result.mastered ? `أحسنت! أتقنت ${unitCode} وفتحت الوحدة التالية.` : 'محاولة جيدة. راجع نقاط الضعف ثم أعد الاختبار.');
    const skills = document.createElement('div'); skills.className = 'summary-skills'; Object.entries(result.skills).filter(([, score]) => score > 0).forEach(([skill, score]) => addText(skills, 'span', '', `${skill}: ${score}%`)); summary.append(skills); submit.textContent = 'تم حفظ النتيجة'; summary.scrollIntoView({behavior: 'smooth', block: 'center'});
  });
})();
