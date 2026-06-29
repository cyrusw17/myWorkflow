(function () {
  'use strict';

  var header = document.querySelector('.site-header');
  var stickyBar = document.querySelector('.sticky-bar');
  var heroSection = document.querySelector('.hero');
  var qualifySection = document.querySelector('#qualify');

  // Sticky header state + floating conversion bar visibility
  var ticking = false;
  function update() {
    var y = window.scrollY;
    if (header) header.classList.toggle('is-scrolled', y > 24);
    if (stickyBar) {
      // Show once the hero CTA has scrolled away; hide while the form is on screen
      var pastHero = heroSection ? (heroSection.getBoundingClientRect().bottom < 80) : (y > 480);
      var formInView = qualifySection ? (qualifySection.getBoundingClientRect().top < window.innerHeight - 60) : false;
      stickyBar.classList.toggle('is-visible', pastHero && !formInView);
    }
    ticking = false;
  }
  function onScroll() {
    if (!ticking) {
      window.requestAnimationFrame(update);
      ticking = true;
    }
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  update();

  // FAQ accordion
  function setPanel(panel, open) {
    if (!panel) return;
    panel.style.maxHeight = open ? panel.scrollHeight + 'px' : null;
  }

  var faqItems = Array.prototype.slice.call(document.querySelectorAll('[data-faq] .faq-item'));
  faqItems.forEach(function (item) {
    var btn = item.querySelector('.faq-trigger');
    var panel = item.querySelector('.faq-panel');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var isOpen = item.classList.contains('is-open');
      faqItems.forEach(function (el) {
        el.classList.remove('is-open');
        var t = el.querySelector('.faq-trigger');
        if (t) t.setAttribute('aria-expanded', 'false');
        setPanel(el.querySelector('.faq-panel'), false);
      });
      if (!isOpen) {
        item.classList.add('is-open');
        btn.setAttribute('aria-expanded', 'true');
        setPanel(panel, true);
      }
    });
  });

  // Keep an open FAQ panel sized correctly after viewport/orientation changes
  var resizeTimer;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      var open = document.querySelector('.faq-item.is-open .faq-panel');
      if (open) {
        open.style.maxHeight = 'none';
        var h = open.scrollHeight;
        open.style.maxHeight = h + 'px';
      }
    }, 150);
  }, { passive: true });

  // Open the first FAQ on load
  var firstOpen = document.querySelector('.faq-item.is-open .faq-panel');
  if (firstOpen) setPanel(firstOpen, true);

  // Scroll reveal via IntersectionObserver (no third-party libraries)
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var reveals = Array.prototype.slice.call(document.querySelectorAll('.reveal'));

  if (reduced || !('IntersectionObserver' in window)) {
    reveals.forEach(function (el) { el.classList.add('is-visible'); });
    return;
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        io.unobserve(entry.target);
      }
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });

  reveals.forEach(function (el) {
    var rect = el.getBoundingClientRect();
    if (rect.top < window.innerHeight) {
      el.classList.add('is-visible'); // already in view on load — show immediately
    } else {
      io.observe(el);
    }
  });
})();
