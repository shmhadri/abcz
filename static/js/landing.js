(function () {
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
}());
