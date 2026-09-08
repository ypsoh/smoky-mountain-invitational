/* ============================================================
   ENVELOPE STATE MACHINE — index.html

   sealed -> unsealing -> opening -> rising -> open

   Design constraints, all of them load-bearing:

   1. CONTENT IS NEVER GATED. The invitation markup is in the DOM
      unconditionally and envelope.css defaults to the open state.
      If this file fails to load or throws on line one, the page
      is still a complete, readable invitation.

   2. REDUCED MOTION JUMPS TO THE END. We set state directly to
      'open' rather than running the sequence quickly, so no
      transition is ever registered and there is nothing to
      accelerate.

   3. SKIP IS AVAILABLE FROM FRAME ONE. It is a real <button>,
      first in tab order, never revealed on a delay.

   4. STORAGE IS ALWAYS GUARDED. Safari throws SecurityError on
      sessionStorage from file:// URLs. An unguarded access here
      would kill the whole script.
   ============================================================ */
(function () {
  'use strict';

  var root  = document.documentElement;
  var KEY   = 'smi:envelope:v1';
  var timers = [];

  function seen()     { try { return sessionStorage.getItem(KEY) === '1'; } catch (e) { return false; } }
  function markSeen() { try { sessionStorage.setItem(KEY, '1'); } catch (e) { /* no-op */ } }

  function setState(s) { root.setAttribute('data-envelope', s); }

  function clearTimers() {
    for (var i = 0; i < timers.length; i++) { clearTimeout(timers[i]); }
    timers = [];
  }

  /* Terminal state. Reachable from the sequence, the skip button,
     Escape, reduced motion, a return visit, or a thrown error. */
  function open(instant) {
    clearTimers();
    if (instant) {
      // Kill transitions for exactly one frame so this is a jump,
      // not a 2.9-second fast-forward.
      root.classList.add('env-instant');
      var style = document.createElement('style');
      style.id = 'env-instant-style';
      style.textContent = '.env-instant *{transition:none!important;animation:none!important}';
      document.head.appendChild(style);
      requestAnimationFrame(function () {
        requestAnimationFrame(function () {
          root.classList.remove('env-instant');
          var s = document.getElementById('env-instant-style');
          if (s) { s.remove(); }
        });
      });
    }
    setState('open');
    markSeen();

    var stage = document.querySelector('.env-stage');
    if (stage) { stage.setAttribute('aria-hidden', 'true'); }

    // Move focus to the invitation heading so keyboard and screen
    // reader users land on the content, not on a dead envelope.
    var h = document.getElementById('invite-title');
    if (h) { h.focus({ preventScroll: true }); }
  }

  function run() {
    setState('sealed');
    timers.push(setTimeout(function () { setState('unsealing'); }, 1200));
    timers.push(setTimeout(function () { setState('opening');   }, 1580));
    timers.push(setTimeout(function () { setState('rising');    }, 2100));
    timers.push(setTimeout(function () { open(false);           }, 2900));
  }

  function start() {
    var mq = window.matchMedia('(prefers-reduced-motion: reduce)');

    // Reduced motion, or already seen this tab session: final state.
    if (mq.matches || seen()) {
      open(true);
    } else {
      run();
    }

    // Honour a change of preference mid-visit.
    var onChange = function (e) { if (e.matches) { open(true); } };
    if (mq.addEventListener) { mq.addEventListener('change', onChange); }
    else if (mq.addListener) { mq.addListener(onChange); }

    // Seal click advances immediately rather than waiting out the
    // auto-advance -- it is the only thing that looks clickable.
    var seal = document.querySelector('.env-seal');
    if (seal) {
      seal.addEventListener('click', function () {
        if (root.getAttribute('data-envelope') === 'sealed') {
          clearTimers();
          setState('unsealing');
          timers.push(setTimeout(function () { setState('opening'); }, 380));
          timers.push(setTimeout(function () { setState('rising');  }, 900));
          timers.push(setTimeout(function () { open(false);         }, 1700));
        }
      });
    }

    var skip = document.querySelector('.env-skip');
    if (skip) { skip.addEventListener('click', function () { open(true); }); }

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && root.getAttribute('data-envelope') !== 'open') {
        open(true);
      }
    });
  }

  // Any unexpected failure must still leave a readable page.
  try { start(); } catch (e) { setState('open'); }
})();
