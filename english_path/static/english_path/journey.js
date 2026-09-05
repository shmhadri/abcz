(() => {
  const csrf = () => document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
  const buttons = [...document.querySelectorAll('[data-step]')];
  const panels = [...document.querySelectorAll('[data-panel]')];
  const show = (name) => {
    buttons.forEach((button) => button.classList.toggle('active', button.dataset.step === name));
    panels.forEach((panel) => panel.classList.toggle('active', panel.dataset.panel === name));
    document.querySelector('.lesson-steps')?.scrollIntoView({behavior: 'smooth', block: 'start'});
  };
  buttons.forEach((button) => button.addEventListener('click', () => show(button.dataset.step)));
  document.querySelectorAll('.next-step').forEach((button) => button.addEventListener('click', () => {
    const panel = button.closest('[data-panel]');
    const index = panels.indexOf(panel);
    if (panels[index + 1]) show(panels[index + 1].dataset.panel);
  }));
  document.querySelectorAll('[data-speak]').forEach((button) => button.addEventListener('click', () => {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(button.dataset.speak);
    utterance.lang = 'en-US';
    window.speechSynthesis.speak(utterance);
  }));
  const configNode = document.querySelector('#unit-config');
  if (configNode) {
    const config = JSON.parse(configNode.textContent);
    document.querySelectorAll('[data-score]').forEach((button) => button.addEventListener('click', async () => {
      button.disabled = true;
      const score = Number(button.dataset.score);
      const response = await fetch(config.saveUrl, {method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrf()}, body: JSON.stringify({score, skills: {vocabulary: score, grammar: score, listening: score, speaking: score}, mistakes: score < 80 ? [{key: `${config.unit}-grammar`, skill: 'grammar', prompt: 'راجع قاعدة هذه الوحدة', answer: 'ابحث عن الفاعل والزمن ثم اختر شكل الفعل.'}] : []})});
      const result = await response.json();
      document.querySelector('.save-result').textContent = result.ok ? (score >= 80 ? 'أحسنت! أتقنت الوحدة ويمكنك المتابعة. ✓' : 'حُفظت محاولتك. راجع نقطة الضعف ثم أعد التدريب.') : 'تعذر حفظ المحاولة.';
      button.disabled = false;
    }));
  }
  document.querySelectorAll('.review-choice').forEach((button) => button.addEventListener('click', async () => {
    const card = button.closest('.review-card');
    const response = await fetch(card.dataset.answerUrl, {method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrf()}, body: JSON.stringify({correct: button.dataset.correct === 'true'})});
    if (response.ok) { card.style.opacity = '.35'; setTimeout(() => card.remove(), 250); }
  }));
})();
