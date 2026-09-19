(() => {
  const card = document.querySelector('.continue-learning');
  if (!card) return;
  const key = `englishPath:a1:${card.dataset.storageScope}`;
  let state = {};
  try { state = JSON.parse(window.localStorage.getItem(key)) || {}; } catch (_) { return; }
  if (!state.lastUnit) return;
  const unitNode = [...document.querySelectorAll('.unit-node[data-unit-slug]')]
    .find((node) => node.dataset.unitSlug === state.lastUnit);
  const safeLink = unitNode?.querySelector('a[href]');
  if (!safeLink) return;
  const sections = ['discover', 'words', 'grammar', 'listen', 'speak', 'read', 'write', 'games', 'mission', 'quiz'];
  const section = sections.includes(state.lastSection) ? state.lastSection : 'discover';
  const link = card.querySelector('[data-continue-link]');
  link.href = `${safeLink.href}#section-${section}`;
  card.querySelector('[data-continue-label]').textContent = `${unitNode.dataset.unitCode} · ${unitNode.dataset.unitTitle}`;
  const labels = {discover: 'اكتشف', words: 'الكلمات', grammar: 'القاعدة', listen: 'الاستماع', speak: 'التحدث', read: 'القراءة', write: 'الكتابة', games: 'الألعاب', mission: 'المهمة', quiz: 'الاختبار'};
  card.querySelector('[data-continue-section]').textContent = ` · القسم: ${labels[section]}`;
})();
