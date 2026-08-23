/**
 * Smart Learning - Modern Landing Page Interactive Scripts
 * Provides micro-interactions, speech synthesis preview, smooth scroll spy, and FAQ accordion
 */

(function () {
  'use strict';

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // 1. Sticky Header Scroll Effect
  const header = document.querySelector('.landing-header');
  if (header) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 20) {
        header.classList.add('is-scrolled');
      } else {
        header.classList.remove('is-scrolled');
      }
    }, { passive: true });
  }

  // 2. Mobile Menu Toggle
  const toggleBtn = document.querySelector('.landing-menu-toggle');
  const navMenu = document.querySelector('.landing-nav');

  function setMobileMenu(isOpen) {
    if (!toggleBtn || !navMenu) return;
    navMenu.classList.toggle('is-open', isOpen);
    toggleBtn.setAttribute('aria-expanded', String(isOpen));
  }

  if (toggleBtn && navMenu) {
    toggleBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      const isOpen = navMenu.classList.contains('is-open');
      setMobileMenu(!isOpen);
    });

    // Close menu when clicking nav links
    navMenu.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        setMobileMenu(false);
      });
    });

    // Close menu when clicking outside
    document.addEventListener('click', function (e) {
      if (!navMenu.contains(e.target) && !toggleBtn.contains(e.target)) {
        setMobileMenu(false);
      }
    });

    // Close on Escape key
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        setMobileMenu(false);
      }
    });

    window.addEventListener('resize', function () {
      if (window.innerWidth > 768) {
        setMobileMenu(false);
      }
    });
  }

  // 3. FAQ Accordion
  const accordionItems = document.querySelectorAll('.landing-accordion-item');
  accordionItems.forEach(function (item) {
    const trigger = item.querySelector('.landing-accordion-trigger');
    if (!trigger) return;

    trigger.addEventListener('click', function () {
      const isAlreadyOpen = item.classList.contains('is-open');

      // Optional: close other open items for cleaner accordion
      accordionItems.forEach(function (otherItem) {
        if (otherItem !== item) {
          otherItem.classList.remove('is-open');
          const otherTrigger = otherItem.querySelector('.landing-accordion-trigger');
          if (otherTrigger) otherTrigger.setAttribute('aria-expanded', 'false');
        }
      });

      item.classList.toggle('is-open', !isAlreadyOpen);
      trigger.setAttribute('aria-expanded', String(!isAlreadyOpen));
    });
  });

  // 4. Scroll Reveal Animations with Stagger
  if (!prefersReducedMotion && 'IntersectionObserver' in window) {
    const revealElements = document.querySelectorAll(
      '.landing-section, .landing-trust-strip, .landing-problem-card, .landing-step-card, .landing-level-card, .landing-showcase-card, .landing-feature-item'
    );

    revealElements.forEach(function (el) {
      el.classList.add('landing-reveal');
    });

    const observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, {
      rootMargin: '0px 0px -60px 0px',
      threshold: 0.08
    });

    revealElements.forEach(function (el) {
      observer.observe(el);
    });
  }

  // 5. Interactive Audio Speech Pronunciation on Preview Cards
  function speakEnglishText(text) {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel(); // stop any previous sound
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = 0.85; // slightly slower for young learners
    utterance.pitch = 1.1;

    // Pick best English voice if available
    const voices = window.speechSynthesis.getVoices();
    const englishVoice = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Google') || v.name.includes('Natural') || v.name.includes('Samantha')));
    if (englishVoice) {
      utterance.voice = englishVoice;
    }

    window.speechSynthesis.speak(utterance);
  }

  // Hook speech to letter & sound cards in hero & showcase
  const letterCards = document.querySelectorAll('[data-speak]');
  letterCards.forEach(function (card) {
    card.addEventListener('click', function () {
      const textToSpeak = this.getAttribute('data-speak') || 'A';
      speakEnglishText(textToSpeak);

      // Micro visual pulse animation
      this.style.transform = 'scale(0.96)';
      setTimeout(() => {
        this.style.transform = '';
      }, 150);
    });
  });

  // 6. Navigation Link Highlighting via Scroll Spy
  const navSectionLinks = Array.from(document.querySelectorAll('.landing-nav-links a[href^="#"]'));
  const targetSections = navSectionLinks
    .map(link => document.querySelector(link.getAttribute('href')))
    .filter(Boolean);

  if (navSectionLinks.length && targetSections.length && 'IntersectionObserver' in window) {
    const scrollSpyObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          const activeId = entry.target.id;
          navSectionLinks.forEach(function (link) {
            link.classList.toggle('is-current', link.getAttribute('href') === '#' + activeId);
          });
        }
      });
    }, {
      rootMargin: '-30% 0px -60% 0px',
      threshold: 0
    });

    targetSections.forEach(function (section) {
      scrollSpyObserver.observe(section);
    });
  }

})();
