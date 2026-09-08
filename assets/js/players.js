/* ============================================================
   PLAYERS — six cards, rendered from data.js so handicaps and
   tee assignments can never drift from the match page.

   Bios are deliberately NOT in here: they live as plain markup
   inside each card in players.html, so they can be edited by
   hand without touching any JavaScript.
   ============================================================ */
(function () {
  'use strict';
  var host = document.getElementById('field');
  if (!host || typeof PLAYERS === 'undefined') { return; }

  function isKo() { return document.documentElement.getAttribute('data-lang') !== 'en'; }
  function ch(p, cid) {
    var C = COURSES[cid], t = C.tees[p.tees[cid]];
    return Math.round(p.hi * (t.slope / 113) + (t.cr - C.par));
  }
  function ph(p, cid) { return Math.round(ch(p, cid) * ALLOWANCE); }

  function render() {
    var ko = isKo();
    host.innerHTML = '';
    ['laurel', 'balsam'].forEach(function (tid) {
      var sec = document.createElement('section');
      sec.className = 'team team--' + tid;

      var h = document.createElement('h2');
      h.className = 'team__name';
      h.textContent = ko ? TEAMS[tid].nameKo : TEAMS[tid].name;
      sec.appendChild(h);

      var mates = PLAYERS.filter(function (p) { return p.team === tid; });
      var sum = mates.reduce(function (a, p) { return a + p.hi; }, 0);
      var sub = document.createElement('p');
      sub.className = 'team__sum';
      sub.textContent = (ko ? '핸디캡 합계 ' : 'Combined handicap ') + sum;
      sec.appendChild(sub);

      var grid = document.createElement('div');
      grid.className = 'field-grid';
      mates.forEach(function (p) {
        var card = document.createElement('article');
        card.className = 'pcard';
        card.innerHTML =
          '<p class="pcard__name">' + (ko && p.nameKo ? p.nameKo : p.name) + '</p>' +
          '<p class="pcard__hi"><span>' + (ko ? '핸디캡 인덱스' : 'Handicap index') +
            '</span><strong>' + p.hi + '</strong></p>' +
          '<dl class="pcard__rows">' +
            '<div><dt>' + (ko ? '매기 밸리' : 'Maggie Valley') + '</dt>' +
            '<dd>' + COURSES.maggie.tees[p.tees.maggie].name + ' &middot; ' +
              ph(p, 'maggie') + (ko ? '타' : ' shots') + '</dd></div>' +
            '<div><dt>' + (ko ? '세쿼이아' : 'Sequoyah') + '</dt>' +
            '<dd>' + COURSES.sequoyah.tees[p.tees.sequoyah].name + ' &middot; ' +
              ph(p, 'sequoyah') + (ko ? '타' : ' shots') + '</dd></div>' +
          '</dl>' +
          '<p class="pcard__slot">' +
            (ko ? '한 줄 소개를 넣을 자리입니다.' : 'Room for a line about them.') +
          '</p>';
        grid.appendChild(card);
      });
      sec.appendChild(grid);
      host.appendChild(sec);
    });
  }

  document.addEventListener('DOMContentLoaded', render);
  if (document.readyState !== 'loading') { render(); }
  document.addEventListener('click', function (e) {
    if (e.target.closest && e.target.closest('.lang-toggle__btn')) { setTimeout(render, 0); }
  });
})();
