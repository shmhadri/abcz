(function () {
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const toggle = document.querySelector('.landing-menu-toggle');
  const nav = document.querySelector('.landing-nav');
  const setMenuState = function (open) {
    if (!toggle || !nav) return;
    nav.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    document.body.classList.toggle('landing-menu-open', open);
  };
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      setMenuState(!nav.classList.contains('is-open'));
    });
    nav.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        setMenuState(false);
      });
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') setMenuState(false);
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth > 730) setMenuState(false);
    });
  }
  document.querySelectorAll('.landing-accordion article').forEach(function (item) {
    const button = item.querySelector('button');
    const symbol = button.querySelector('b');
    button.addEventListener('click', function () {
      const open = item.classList.toggle('is-open');
      button.setAttribute('aria-expanded', String(open));
      if (symbol) symbol.textContent = open ? '−' : '+';
    });
  });

  const animatedSections = document.querySelectorAll(
    '.landing-section, .landing-trust-strip'
  );
  if (!reducedMotion && 'IntersectionObserver' in window) {
    animatedSections.forEach(function (section) {
      section.classList.add('landing-reveal');
    });
    const revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        revealObserver.unobserve(entry.target);
      });
    }, { threshold: 0.12 });
    animatedSections.forEach(function (section) { revealObserver.observe(section); });
  }

  const sectionLinks = Array.from(document.querySelectorAll('.landing-nav a[href^="#"]'));
  const sectionTargets = sectionLinks
    .map(function (link) { return document.querySelector(link.getAttribute('href')); })
    .filter(Boolean);
  if (sectionLinks.length && sectionTargets.length && 'IntersectionObserver' in window) {
    const navObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        sectionLinks.forEach(function (link) {
          link.classList.toggle('is-current', link.getAttribute('href') === '#' + entry.target.id);
        });
      });
    }, { rootMargin: '-30% 0px -60% 0px', threshold: 0 });
    sectionTargets.forEach(function (section) { navObserver.observe(section); });
  }
}());
