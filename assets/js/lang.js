/* ============================================================
   LANGUAGE TOGGLE — English / 한국어

   State lives in one place: the data-lang attribute on <html>.
   CSS in i18n.css keys off it; nothing else needs to know.

   The attribute is set by a tiny INLINE script in each page's
   <head> (before any stylesheet) so a returning Korean reader
   never sees a flash of English. This file only wires the
   buttons and persists the choice.
   ============================================================ */
(function () {
  'use strict';

  var KEY = 'smi:lang:v1';

  // localStorage throws SecurityError on file:// in Safari — and an
  // unguarded throw here would kill the toggle entirely. Every access
  // goes through these two wrappers.
  function read()  { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function write(v){ try { localStorage.setItem(KEY, v); } catch (e) { /* no-op */ } }

  // Korean is the default, so 'ko' means REMOVE the attribute and
  // 'en' means set it. Inverted from the usual shape on purpose.
  function apply(lang) {
    var root = document.documentElement;
    if (lang === 'en') {
      root.setAttribute('data-lang', 'en');
      root.setAttribute('lang', 'en');
    } else {
      root.removeAttribute('data-lang');
      root.setAttribute('lang', 'ko');
    }
    // Keep every toggle on the page in sync (nav + any in-page copy).
    var btns = document.querySelectorAll('.lang-toggle__btn');
    for (var i = 0; i < btns.length; i++) {
      btns[i].setAttribute('aria-pressed', String(btns[i].dataset.lang === lang));
    }
    write(lang);
  }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest ? e.target.closest('.lang-toggle__btn') : null;
    if (!btn) return;
    apply(btn.dataset.lang === 'en' ? 'en' : 'ko');
  });

  // Sync button pressed-state on load with whatever the head script chose.
  apply(document.documentElement.getAttribute('data-lang') === 'en' ? 'en' : 'ko');
})();
