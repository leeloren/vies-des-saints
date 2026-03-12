/* ============================================================
   Navigation dropdown behaviour
   ============================================================ */
(function () {
  'use strict';

  var items = document.querySelectorAll('.nav-item--dropdown');

  items.forEach(function (li) {
    var toggle = li.querySelector('.nav-dropdown-toggle');
    if (!toggle) return;

    /* ── Mouse: open/close on hover ─────────────────────── */
    li.addEventListener('mouseenter', function () {
      toggle.setAttribute('aria-expanded', 'true');
    });
    li.addEventListener('mouseleave', function () {
      toggle.setAttribute('aria-expanded', 'false');
    });

    /* ── Click: prevent navigation for href="#" toggles;
           toggle open/close for touch devices ──────────── */
    toggle.addEventListener('click', function (e) {
      if (toggle.getAttribute('href') === '#') {
        e.preventDefault();
      }
      var isOpen = toggle.getAttribute('aria-expanded') === 'true';
      /* Close all others */
      items.forEach(function (other) {
        var t = other.querySelector('.nav-dropdown-toggle');
        if (t && t !== toggle) t.setAttribute('aria-expanded', 'false');
      });
      toggle.setAttribute('aria-expanded', isOpen ? 'false' : 'true');
    });
  });

  /* ── Close all when clicking outside ──────────────────── */
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.nav-item--dropdown')) {
      items.forEach(function (li) {
        var t = li.querySelector('.nav-dropdown-toggle');
        if (t) t.setAttribute('aria-expanded', 'false');
      });
    }
  });

  /* ── Close all on Escape ───────────────────────────────── */
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      items.forEach(function (li) {
        var t = li.querySelector('.nav-dropdown-toggle');
        if (t) t.setAttribute('aria-expanded', 'false');
      });
    }
  });
}());
