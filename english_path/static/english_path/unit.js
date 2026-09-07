(() => {
  const stepButtons = [...document.querySelectorAll('[data-rich-step]')];
  const panels = [...document.querySelectorAll('[data-rich-panel]')];
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const localStateNode = document.querySelector('.a1-local-state');
  const unitSlug = localStateNode?.dataset.unitSlug || '';
  const stateKey = localStateNode ? `englishPath:a1:${localStateNode.dataset.storageScope}` : '';
  const sectionNames = stepButtons.map((button) => button.dataset.richStep);
  const sectionLabels = Object.fromEntries(stepButtons.map((button) => [button.dataset.richStep, button.textContent.replace(/^\d+\s*/, '').trim()]));
  const persistentStorage = (() => { try { return window.localStorage; } catch (_) { return null; } })();
  const tabStorage = (() => { try { return window.sessionStorage; } catch (_) { return null; } })();
  const readStorage = (storage, key, fallback) => { try { return JSON.parse(storage.getItem(key)) || fallback; } catch (_) { return fallback; } };
  const writeStorage = (storage, key, value) => { try { storage.setItem(key, JSON.stringify(value)); return true; } catch (_) { return false; } };
  const localState = stateKey && persistentStorage ? readStorage(persistentStorage, stateKey, {units: {}}) : {units: {}};
  if (!localState.units || typeof localState.units !== 'object') localState.units = {};
  const unitState = localState.units[unitSlug] || {visited: [], completed: [], savedWords: []};
  unitState.visited = unitState.visited.filter((name) => sectionNames.includes(name));
  unitState.completed = unitState.completed.filter((name) => sectionNames.includes(name));
  unitState.savedWords = Array.isArray(unitState.savedWords) ? unitState.savedWords : [];
  localState.units[unitSlug] = unitState;
  const saveLocalState = () => { if (stateKey && persistentStorage) { localState.lastUnit = unitSlug; localState.lastSection = unitState.current; writeStorage(persistentStorage, stateKey, localState); } };
  const renderSectionProgress = () => {
    const completed = new Set(unitState.completed);
    const visited = new Set(unitState.visited);
    stepButtons.forEach((button) => {
      const name = button.dataset.richStep;
      button.classList.toggle('completed', completed.has(name));
      button.classList.toggle('visited', visited.has(name));
      button.dataset.status = completed.has(name) ? '✓' : visited.has(name) ? '•' : '';
    });
    const count = completed.size;
    const countNode = document.querySelector('[data-section-count]');
    if (countNode) countNode.textContent = `${count} / ${sectionNames.length} completed`;
    const track = document.querySelector('.section-progress-track');
    track?.setAttribute('aria-valuenow', String(count));
    const bar = document.querySelector('[data-section-progress-bar]');
    if (bar) bar.style.width = `${count / sectionNames.length * 100}%`;
  };
  const markComplete = (name) => {
    if (!localStateNode || unitState.completed.includes(name)) return;
    unitState.completed.push(name); renderSectionProgress(); saveLocalState();
  };
  const showPanel = (name, {focusPanel = false, updateLocation = true} = {}) => {
    if (!sectionNames.includes(name)) name = 'discover';
    stepButtons.forEach((button) => { const active = button.dataset.richStep === name; button.classList.toggle('active', active); button.setAttribute('aria-selected', String(active)); if (active) button.setAttribute('aria-current', 'step'); else button.removeAttribute('aria-current'); button.tabIndex = active ? 0 : -1; });
    panels.forEach((panel) => { const active = panel.dataset.richPanel === name; panel.classList.toggle('active', active); panel.setAttribute('aria-hidden', String(!active)); });
    if (localStateNode) { unitState.current = name; if (!unitState.visited.includes(name)) unitState.visited.push(name); saveLocalState(); renderSectionProgress(); }
    const currentNode = document.querySelector('[data-current-section]'); if (currentNode) currentNode.textContent = sectionLabels[name];
    if (updateLocation && localStateNode) history.replaceState(null, '', `#section-${name}`);
    document.querySelector('.rich-steps')?.scrollIntoView({behavior: reducedMotion ? 'auto' : 'smooth', block: 'start'});
    stepButtons.find((button) => button.dataset.richStep === name)?.scrollIntoView({behavior: reducedMotion ? 'auto' : 'smooth', block: 'nearest', inline: 'center'});
    if (focusPanel) { const panel = panels.find((item) => item.dataset.richPanel === name); const heading = panel?.querySelector('h2,h3'); if (heading) { heading.tabIndex = -1; heading.focus({preventScroll: true}); } }
    const index = sectionNames.indexOf(name);
    const previousControl = document.querySelector('[data-section-previous]'); const nextControl = document.querySelector('[data-section-next]');
    if (previousControl) previousControl.disabled = index === 0;
    if (nextControl) nextControl.disabled = index === sectionNames.length - 1;
  };
  stepButtons.forEach((button, index) => { const panelId = `unit-panel-${button.dataset.richStep}`; button.id = `unit-tab-${button.dataset.richStep}`; button.setAttribute('role', 'tab'); button.setAttribute('aria-controls', panelId); button.addEventListener('click', () => showPanel(button.dataset.richStep)); button.addEventListener('keydown', (event) => { if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return; event.preventDefault(); const offset = event.key === 'ArrowLeft' ? 1 : -1; const target = stepButtons[(index + offset + stepButtons.length) % stepButtons.length]; showPanel(target.dataset.richStep); target.focus(); }); });
  panels.forEach((panel) => { panel.id = `unit-panel-${panel.dataset.richPanel}`; panel.setAttribute('role', 'tabpanel'); panel.setAttribute('aria-labelledby', `unit-tab-${panel.dataset.richPanel}`); });
  const hashSection = location.hash.startsWith('#section-') ? location.hash.slice(9) : '';
  const restoredSection = sectionNames.includes(hashSection) ? hashSection : sectionNames.includes(unitState.current) ? unitState.current : sectionNames[0];
  if (stepButtons[0]) showPanel(restoredSection, {updateLocation: false});
  const advance = (current, direction = 1) => {
    const next = panels[panels.indexOf(current) + direction];
    if (next) showPanel(next.dataset.richPanel, {focusPanel: true});
  };
  document.querySelectorAll('.rich-next').forEach((button) => button.addEventListener('click', () => {
    const current = button.closest('[data-rich-panel]');
    if (current.dataset.richPanel === 'discover' || (current.dataset.richPanel === 'grammar' && !localStateNode)) markComplete(current.dataset.richPanel);
    advance(current);
  }));
  document.querySelector('[data-section-previous]')?.addEventListener('click', () => advance(document.querySelector('.rich-panel.active'), -1));
  document.querySelector('[data-section-next]')?.addEventListener('click', () => advance(document.querySelector('.rich-panel.active')));

  document.querySelectorAll('.mini-check').forEach((activity) => {
    const buttons = [...activity.querySelectorAll('.choice-row button, :scope > button')];
    buttons.forEach((button) => button.addEventListener('click', () => {
      const correct = button.textContent.trim() === activity.dataset.answer;
      buttons.forEach((item) => { item.disabled = true; item.classList.toggle('correct', item.textContent.trim() === activity.dataset.answer); });
      button.classList.toggle('wrong', !correct);
      const feedback = activity.querySelector('.activity-feedback') || activity.nextElementSibling;
      if (feedback) feedback.textContent = correct ? `✓ صحيح. ${activity.dataset.explanation || ''}` : `ليست بعد. الإجابة الصحيحة: ${activity.dataset.answer}. ${activity.dataset.explanation || ''}`;
      activity.dataset.answered = 'true';
      const panel = activity.closest('[data-rich-panel]');
      if (panel?.dataset.richPanel === 'listen') {
        const transcript = panel.querySelector('[data-transcript-locked]');
        if (transcript?.classList.contains('transcript-locked')) {
          transcript.classList.remove('transcript-locked');
          const summary = transcript.querySelector('summary');
          if (summary) { summary.removeAttribute('aria-disabled'); summary.textContent = '📄 افتح النص بعد المحاولة'; }
        }
      }
      const requiredActivities = panel?.dataset.richPanel === 'grammar' ? [...panel.querySelectorAll('.mini-check,.grammar-builder')] : panel ? [...panel.querySelectorAll('.mini-check')] : [];
      if (panel && (panel.dataset.richPanel !== 'games' || correct) && requiredActivities.length && requiredActivities.every((item) => item.dataset.answered === 'true')) markComplete(panel.dataset.richPanel);
    }));
  });

  const dialogueNode = document.querySelector('#unit-dialogue, #a1-dialogue');
  const applyA1Voice = (utterance) => {
    utterance.lang = localStateNode ? 'en-GB' : 'en-US';
    if (!localStateNode) return;
    const voices = window.speechSynthesis.getVoices();
    utterance.voice = voices.find((voice) => voice.lang.toLowerCase() === 'en-gb') || voices.find((voice) => voice.lang.toLowerCase().startsWith('en')) || null;
  };
  document.querySelectorAll('[data-dialogue-play]').forEach((button) => button.addEventListener('click', () => {
    if (!dialogueNode || !('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    JSON.parse(dialogueNode.textContent).forEach((line, index) => {
      const utterance = new SpeechSynthesisUtterance(line);
      applyA1Voice(utterance); utterance.rate = .86; utterance.pitch = index % 2 ? 1.08 : .94;
      window.speechSynthesis.speak(utterance);
    });
  }));

  const wordCards = [...document.querySelectorAll('.rich-word')];
  const touchedWords = new Set();
  const renderSavedWord = (button, saved) => { button.classList.toggle('saved', saved); button.textContent = saved ? '♥ محفوظة' : '♡ احفظها'; button.setAttribute('aria-pressed', String(saved)); };
  wordCards.forEach((card) => {
    const word = card.querySelector('strong')?.textContent.trim(); const saveButton = card.querySelector('.save-word');
    if (!word || !saveButton) return;
    renderSavedWord(saveButton, unitState.savedWords.includes(word));
    card.querySelectorAll('[data-speak],.arabic-toggle,.save-word').forEach((control) => control.addEventListener('click', () => { touchedWords.add(word); if (touchedWords.size >= Math.min(3, wordCards.length)) markComplete('words'); }));
    saveButton.addEventListener('click', () => {
      const saved = !unitState.savedWords.includes(word);
      unitState.savedWords = saved ? [...unitState.savedWords, word] : unitState.savedWords.filter((item) => item !== word);
      renderSavedWord(saveButton, saved); saveLocalState();
    });
  });
  document.querySelectorAll('.arabic-toggle').forEach((button) => button.addEventListener('click', () => {
    const card = button.closest('.rich-word') || button.parentElement;
    const help = [...card.querySelectorAll('.arabic-help')];
    const shouldShow = help.some((item) => item.hidden);
    help.forEach((item) => { item.hidden = !shouldShow; });
    button.setAttribute('aria-expanded', String(shouldShow));
    button.textContent = shouldShow ? 'أخفِ المساعدة' : (button.closest('.rich-word') ? 'أظهر المساعدة' : 'أظهر الشرح العربي');
  }));
  const textarea = document.querySelector('.writing-area textarea');
  const draftKey = localStateNode ? `${stateKey}:draft:${unitSlug}` : '';
  const draftStatus = document.querySelector('[data-draft-status]');
  if (textarea && draftKey) {
    try { textarea.value = tabStorage?.getItem(draftKey) || ''; } catch (_) { /* Storage may be blocked. */ }
    document.querySelector('[data-char-count]').textContent = textarea.value.length;
    if (textarea.value && draftStatus) draftStatus.textContent = 'تمت استعادة المسودة المؤقتة من هذا التبويب. لا تكتب معلومات شخصية حساسة.';
  }
  textarea?.addEventListener('input', () => {
    document.querySelector('[data-char-count]').textContent = textarea.value.length;
    if (draftKey) { try { if (!tabStorage) throw new Error('storage'); tabStorage.setItem(draftKey, textarea.value); if (draftStatus) draftStatus.textContent = 'تم حفظ المسودة مؤقتًا في هذا التبويب. لا تكتب معلومات شخصية حساسة.'; } catch (_) { if (draftStatus) draftStatus.textContent = 'تعذر حفظ المسودة على هذا الجهاز.'; } }
    if (textarea.value.trim().length >= 20) markComplete('write');
  });
  document.querySelector('[data-clear-draft]')?.addEventListener('click', () => {
    if (!textarea) return; textarea.value = ''; document.querySelector('[data-char-count]').textContent = '0';
    try { tabStorage?.removeItem(draftKey); } catch (_) { /* The visible draft is still cleared. */ }
    if (draftStatus) draftStatus.textContent = 'تم مسح المسودة.'; textarea.focus();
  });
  const speakingRubric = document.querySelector('.speaking-rubric');
  document.querySelectorAll('.shadow-list input').forEach((checkbox) => checkbox.addEventListener('change', () => {
    const checks = [...document.querySelectorAll('.shadow-list input')]; if (!speakingRubric && checks.length && checks.every((item) => item.checked)) markComplete('speak');
  }));
  speakingRubric?.querySelectorAll('input').forEach((checkbox) => checkbox.addEventListener('change', () => {
    const checks = [...speakingRubric.querySelectorAll('input')];
    if (checks.length && checks.every((item) => item.checked)) markComplete('speak');
  }));

  document.querySelectorAll('[data-transcript-locked]').forEach((details) => {
    const blockWhileLocked = (event) => {
      if (!details.classList.contains('transcript-locked')) return;
      event.preventDefault();
    };
    details.querySelector('summary')?.addEventListener('click', blockWhileLocked);
    details.querySelector('summary')?.addEventListener('keydown', (event) => {
      if (['Enter', ' '].includes(event.key)) blockWhileLocked(event);
    });
  });

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
      if ([...button.closest('.skill-game').querySelectorAll('[data-match-value]')].every((item) => item.classList.contains('matched'))) markComplete('games');
    } else { button.classList.add('shake'); feedback.textContent = 'حاول مرة أخرى. انطق الكلمة وابحث عن معناها.'; setTimeout(() => button.classList.remove('shake'), 350); }
  }));
  const gameBuilder = document.querySelector('[data-game="sentence-builder"]');
  if (gameBuilder) {
    const built = gameBuilder.querySelector('.built-sentence');
    const tokenButtons = [...gameBuilder.querySelectorAll('.token-bank button')];
    tokenButtons.forEach((button) => button.addEventListener('click', () => { button.disabled = true; const token = document.createElement('button'); token.type = 'button'; token.textContent = button.textContent; token.addEventListener('click', () => { button.disabled = false; token.remove(); }); built.append(token); }));
    gameBuilder.querySelector('[data-reset-builder]')?.addEventListener('click', () => { built.replaceChildren(); tokenButtons.forEach((button) => { button.disabled = false; }); });
    gameBuilder.querySelector('[data-check-builder]')?.addEventListener('click', (event) => { const answer = [...built.children].map((item) => item.textContent).join(' '); const expected = event.currentTarget.dataset.builderAnswer || 'My name is Sara.'; gameBuilder.querySelector('.game-feedback').textContent = answer === expected ? '✓ جملة صحيحة!' : `حاول مرة أخرى. الهدف: ${expected}`; if (answer === expected) markComplete('games'); });
  }
  document.querySelectorAll('.grammar-builder').forEach((builder) => {
    const built = builder.querySelector('.built-sentence');
    const tokenButtons = [...builder.querySelectorAll('.token-bank button')];
    tokenButtons.forEach((button) => button.addEventListener('click', () => {
      button.disabled = true;
      const token = document.createElement('button'); token.type = 'button'; token.textContent = button.textContent;
      token.addEventListener('click', () => { button.disabled = false; token.remove(); }); built.append(token);
    }));
    builder.querySelector('[data-reset-grammar-builder]')?.addEventListener('click', () => { built.replaceChildren(); tokenButtons.forEach((button) => { button.disabled = false; }); });
    builder.querySelector('[data-check-grammar-builder]')?.addEventListener('click', () => {
      const answer = [...built.children].map((item) => item.textContent).join(' ');
      const feedback = builder.querySelector('.activity-feedback'); const correct = answer === builder.dataset.answer;
      feedback.textContent = correct ? '✓ ترتيب صحيح.' : `حاول مرة أخرى. الهدف: ${builder.dataset.answer}`;
      if (correct) { builder.dataset.answered = 'true'; const practices = [...builder.closest('[data-rich-panel]').querySelectorAll('.mini-check,.grammar-builder')]; if (practices.every((item) => item.dataset.answered === 'true')) markComplete('grammar'); }
    });
  });

  document.querySelector('[data-check-mission]')?.addEventListener('click', () => {
    const checks = [...document.querySelectorAll('.mission-steps input')]; const completed = checks.filter((item) => item.checked).length;
    document.querySelector('.mission-status').textContent = completed === checks.length ? '🏆 أنجزت المهمة كاملة. أنت جاهز للاختبار!' : `أنجزت ${completed} من ${checks.length}. أكمل الخطوات قبل الاختبار.`;
    if (checks.length && completed === checks.length) markComplete('mission');
  });

  const quiz = document.querySelector('.unit-quiz');
  const csrf = () => quiz?.querySelector('[name=csrfmiddlewaretoken]').value || '';
  const addText = (parent, tag, className, value) => { const node = document.createElement(tag); node.className = className; node.textContent = value; parent.append(node); return node; };
  const speak = (value) => {
    if (!value || !('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(value); applyA1Voice(utterance); utterance.rate = .86;
    window.speechSynthesis.speak(utterance);
  };
  const fetchJson = async (url, options, timeout = 12000) => {
    const controller = new AbortController(); const timer = setTimeout(() => controller.abort(), timeout);
    try {
      const response = await fetch(url, {...options, signal: controller.signal});
      let result = {};
      try { result = await response.json(); } catch (_) { /* Never expose an HTML error response. */ }
      if (!response.ok) throw new Error('server');
      return result;
    } finally { clearTimeout(timer); }
  };
  const requestErrorMessage = (error) => error?.name === 'AbortError' ? 'استغرق الاتصال وقتًا طويلًا. تحقق من الشبكة وحاول مرة أخرى.' : 'تعذر إكمال الطلب الآن. تحقق من الاتصال ثم حاول مرة أخرى.';
  const renderSimilar = (container, similar) => {
    const box = document.createElement('div'); box.className = 'similar-question'; addText(box, 'b', '', '🎯 جرّب سؤالًا مشابهًا'); addText(box, 'p', 'english-content', similar.prompt);
    if (similar.spoken) { const listen = document.createElement('button'); listen.type = 'button'; listen.className = 'listen-inline'; listen.textContent = '🔊 استمع'; listen.setAttribute('aria-label', 'استمع إلى السؤال المشابه'); listen.addEventListener('click', () => speak(similar.spoken)); box.append(listen); }
    const options = document.createElement('div'); options.className = 'choice-row';
    similar.choices.forEach((choice) => { const button = document.createElement('button'); button.type = 'button'; button.textContent = choice; button.addEventListener('click', async () => {
      options.querySelectorAll('button').forEach((item) => { item.disabled = true; });
      if (!localStateNode) {
        const response = await fetch(quiz.dataset.similarUrl, {method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrf()}, body: JSON.stringify({question_id: similar.id, answer: choice})}); const result = await response.json();
        addText(box, 'p', result.correct ? 'correct-note' : 'wrong-note', result.correct ? `✓ صحيح. ${result.explanation}` : `الإجابة الصحيحة: ${result.correct_answer}. ${result.explanation}`); return;
      }
      try {
        const result = await fetchJson(quiz.dataset.similarUrl, {method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrf()}, body: JSON.stringify({question_id: similar.id, answer: choice})});
        addText(box, 'p', result.correct ? 'correct-note' : 'wrong-note', result.correct ? `✓ صحيح. ${result.explanation}` : `الإجابة الصحيحة: ${result.correct_answer}. ${result.explanation}`);
      } catch (error) {
        options.querySelectorAll('button').forEach((item) => { item.disabled = false; });
        addText(box, 'p', 'request-error', requestErrorMessage(error));
      }
    }); options.append(button); }); box.append(options); container.append(box);
  };
  quiz?.addEventListener('submit', async (event) => {
    event.preventDefault(); const answers = Object.fromEntries(new FormData(quiz).entries()); delete answers.csrfmiddlewaretoken;
    const submit = quiz.querySelector('[type=submit]'); submit.disabled = true; submit.textContent = 'جاري تحليل مهاراتك…';
    if (!localStateNode) {
      const response = await fetch(quiz.dataset.quizUrl, {method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrf()}, body: JSON.stringify({answers})}); const result = await response.json();
      if (!response.ok) { submit.disabled = false; submit.textContent = 'حاول التصحيح مجددًا'; return; }
      result.feedback.forEach((item) => {
        const fieldset = quiz.querySelector(`[data-question-id="${item.id}"]`); const box = fieldset.querySelector('.why-feedback'); box.replaceChildren(); box.className = `why-feedback ${item.correct ? 'answer-correct' : 'answer-wrong'}`;
        addText(box, 'b', '', item.correct ? '✓ إجابة صحيحة' : `✕ اخترت: ${item.selected || 'لم تختر'}`); if (!item.correct) addText(box, 'p', 'correct-answer', `الصحيح: ${item.correct_answer}`); addText(box, 'p', '', `لماذا؟ ${item.why}`); if (!item.correct && item.clue) addText(box, 'p', '', `🔎 الدليل: ${item.clue}`);
        if (!item.correct) { addText(box, 'p', '', `لماذا اختيارك خطأ؟ ${item.why_wrong}`); renderSimilar(box, item.similar); }
      });
      const summary = document.querySelector('.quiz-summary'); const unitCode = document.querySelector('[data-unit-code]')?.dataset.unitCode || ''; summary.hidden = false; summary.replaceChildren(); addText(summary, 'strong', 'summary-score', `${result.score}%`); addText(summary, 'h2', '', result.mastered ? `أحسنت! أتقنت ${unitCode} وفتحت الوحدة التالية.` : 'محاولة جيدة. راجع نقاط الضعف ثم أعد الاختبار.');
      const skills = document.createElement('div'); skills.className = 'summary-skills'; Object.entries(result.skills).filter(([, score]) => score > 0).forEach(([skill, score]) => addText(skills, 'span', '', `${skill}: ${score}%`)); summary.append(skills); submit.textContent = 'تم حفظ النتيجة'; summary.scrollIntoView({behavior: 'smooth', block: 'center'}); return;
    }
    quiz.querySelector('.request-error')?.remove();
    try {
      const result = await fetchJson(quiz.dataset.quizUrl, {method: 'POST', headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrf()}, body: JSON.stringify({answers})});
      result.feedback.forEach((item) => {
        const fieldset = quiz.querySelector(`[data-question-id="${item.id}"]`); const box = fieldset.querySelector('.why-feedback'); box.replaceChildren(); box.className = `why-feedback ${item.correct ? 'answer-correct' : 'answer-wrong'}`;
        addText(box, 'b', '', item.correct ? '✓ إجابة صحيحة' : `✕ اخترت: ${item.selected || 'لم تختر'}`); if (!item.correct) addText(box, 'p', 'correct-answer', `الصحيح: ${item.correct_answer}`); addText(box, 'p', '', `لماذا؟ ${item.why}`); if (!item.correct && item.clue) addText(box, 'p', '', `🔎 الدليل: ${item.clue}`);
        if (!item.correct) { addText(box, 'p', '', `لماذا اختيارك خطأ؟ ${item.why_wrong}`); renderSimilar(box, item.similar); }
      });
      const summary = document.querySelector('.quiz-summary'); const unitCode = document.querySelector('[data-unit-code]')?.dataset.unitCode || ''; summary.hidden = false; summary.replaceChildren(); addText(summary, 'strong', 'summary-score', `${result.score}%`); addText(summary, 'h2', '', result.mastered ? (localStateNode ? 'Unit Completed' : `أحسنت! أتقنت ${unitCode} وفتحت الوحدة التالية.`) : 'محاولة جيدة. راجع نقاط الضعف ثم أعد الاختبار.');
      if (result.mastered && localStateNode) { addText(summary, 'p', '', `أحسنت! أتقنت ${unitCode}.`); markComplete('quiz'); }
      const skills = document.createElement('div'); skills.className = 'summary-skills'; Object.entries(result.skills).filter(([, score]) => score > 0).forEach(([skill, score]) => addText(skills, 'span', '', `${skill}: ${score}%`)); summary.append(skills);
      if (result.next_unit?.url) { const link = addText(summary, 'a', 'journey-button primary completion-next', `Continue to Next Unit · ${result.next_unit.title}`); link.href = result.next_unit.url; }
      submit.textContent = 'تم حفظ النتيجة'; summary.scrollIntoView({behavior: reducedMotion ? 'auto' : 'smooth', block: 'center'});
    } catch (error) {
      const message = document.createElement('p'); message.className = 'request-error'; message.setAttribute('role', 'alert'); message.textContent = requestErrorMessage(error); submit.before(message); submit.textContent = 'حاول التصحيح مجددًا';
    } finally { submit.disabled = false; }
  });
})();
