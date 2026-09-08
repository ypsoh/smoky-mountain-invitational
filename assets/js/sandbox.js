/* ============================================================
   THE TEAM BUILDER — a what-if tool.

   Tap players between the two sides and it tells you, in plain
   words, how even the match would be. Nothing here is saved and
   nothing here is binding; it exists so an argument over dinner
   can be settled in about ten seconds.

   Deliberately NOT a handicap calculator. It shows you the shots
   each side gets and how far apart they are, and it stops there.
   ============================================================ */
(function () {
  'use strict';

  var host = document.getElementById('builder');
  if (!host || typeof PLAYERS === 'undefined') { return; }

  // Working copy, so fiddling here never touches the real teams.
  var picks = {};
  PLAYERS.forEach(function (p) { picks[p.id] = p.team; });
  var SIDES = ['laurel', 'balsam'];

  function ko() { return document.documentElement.getAttribute('data-lang') !== 'en'; }
  function nameOf(p) { return ko() && p.nameKo ? p.nameKo : p.name; }
  function teamName(t) { return ko() && TEAMS[t].nameKo ? TEAMS[t].nameKo : TEAMS[t].name; }

  // Strokes a player gets on a course. The arithmetic stays under
  // the hood -- the page never shows a formula.
  function strokes(p, cid) {
    var C = COURSES[cid], t = C.tees[p.tees[cid]];
    return Math.round((p.hi * (t.slope / 113) + (t.cr - C.par)) * ALLOWANCE);
  }
  function side(t) { return PLAYERS.filter(function (p) { return picks[p.id] === t; }); }
  function total(t, cid) {
    return side(t).reduce(function (a, p) { return a + strokes(p, cid); }, 0);
  }

  /* How even is it? Judged on the 36-hole total, described in
     words rather than numbers, because "two shots apart" means
     nothing to most people and "as good as even" means a lot. */
  function verdict(gap) {
    if (gap <= 2) {
      return { cls: 'is-even',  en: 'As even as it gets. Play it straight up.',
               kr: '이보다 더 공평할 수 없습니다. 그대로 붙으세요.' };
    }
    if (gap <= 6) {
      return { cls: 'is-close', en: 'Close enough. Nobody will complain.',
               kr: '충분히 비슷합니다. 아무도 불평하지 않을 겁니다.' };
    }
    if (gap <= 12) {
      return { cls: 'is-tilt',  en: 'A bit lopsided. Fun, but somebody is getting a head start.',
               kr: '조금 기울었습니다. 재미는 있겠지만 한 팀이 유리합니다.' };
    }
    return { cls: 'is-off', en: 'That is a mismatch. Try again, or play it for laughs.',
             kr: '차이가 큽니다. 다시 짜거나, 그냥 웃자고 치세요.' };
  }

  function render() {
    var k = ko();
    var d1 = { laurel: total('laurel', 'maggie'),   balsam: total('balsam', 'maggie') };
    var d2 = { laurel: total('laurel', 'sequoyah'), balsam: total('balsam', 'sequoyah') };
    var t36 = { laurel: d1.laurel + d2.laurel, balsam: d1.balsam + d2.balsam };
    var gap = Math.abs(t36.laurel - t36.balsam);
    var ahead = t36.laurel > t36.balsam ? 'laurel' : 'balsam';
    var v = verdict(gap);
    var bad = SIDES.some(function (t) { return side(t).length !== 3; });

    var h = '<div class="builder__sides">';
    SIDES.forEach(function (t) {
      var mates = side(t);
      h += '<div class="builder__side builder__side--' + t + '">' +
             '<p class="builder__team">' + teamName(t) + '</p>' +
             '<ul class="builder__roster">';
      if (!mates.length) {
        h += '<li class="builder__empty">' + (k ? '비어 있음' : 'Empty') + '</li>';
      }
      mates.forEach(function (p) {
        h += '<li><button type="button" class="chip" data-move="' + p.id + '">' +
               '<span class="chip__name">' + nameOf(p) + '</span>' +
               '<span class="chip__hi">' + p.hi + '</span>' +
             '</button></li>';
      });
      h += '</ul><p class="builder__shots">' +
             (k ? '받는 타수 ' : 'Shots ') +
             '<strong>' + d1[t] + '</strong>' + (k ? ' (1일차)' : ' day one') +
             ' &middot; <strong>' + d2[t] + '</strong>' + (k ? ' (2일차)' : ' day two') +
           '</p></div>';
    });
    h += '</div>';

    h += '<p class="builder__verdict ' + (bad ? 'is-off' : v.cls) + '">';
    if (bad) {
      h += (k ? '팀당 세 명씩 맞춰 주세요.' : 'Put three on each side.');
    } else {
      h += (k ? v.kr : v.en);
      if (gap > 2) {
        h += ' <span class="builder__gap">' +
             (k ? teamName(ahead) + ' 쪽이 36홀 기준 ' + gap + '타 더 받습니다.'
                : teamName(ahead) + ' get ' + gap + ' more shots over the two rounds.') +
             '</span>';
      }
    }
    h += '</p>';

    h += '<p class="builder__actions">' +
         '<button type="button" class="btn btn--ghost" id="builder-balance">' +
           (k ? '가장 균형 잡힌 조합 찾기' : 'Find the evenest split') + '</button> ' +
         '<button type="button" class="btn btn--ghost" id="builder-reset">' +
           (k ? '원래대로' : 'Back to how it stands') + '</button></p>';

    host.innerHTML = h;
  }

  /* Brute force every way of splitting six people three-and-three.
     Ten distinct splits, so there is no need to be clever. */
  function balance() {
    var ids = PLAYERS.map(function (p) { return p.id; });
    var best = null;
    for (var m = 0; m < 64; m++) {
      var group = [], n = 0, i;
      for (i = 0; i < 6; i++) { if (m & (1 << i)) { group.push(ids[i]); n++; } }
      if (n !== 3 || group.indexOf(ids[0]) === -1) { continue; }  // fix player 0 to skip mirrors
      var trial = {};
      ids.forEach(function (id) { trial[id] = group.indexOf(id) > -1 ? 'laurel' : 'balsam'; });
      var save = picks; picks = trial;
      var g = Math.abs((total('laurel','maggie') + total('laurel','sequoyah')) -
                       (total('balsam','maggie') + total('balsam','sequoyah')));
      picks = save;
      if (!best || g < best.gap) { best = { gap: g, split: trial }; }
    }
    if (best) { picks = best.split; render(); }
  }

  host.addEventListener('click', function (e) {
    var chip = e.target.closest('[data-move]');
    if (chip) {
      var id = chip.getAttribute('data-move');
      picks[id] = picks[id] === 'laurel' ? 'balsam' : 'laurel';
      return render();
    }
    if (e.target.closest('#builder-balance')) { return balance(); }
    if (e.target.closest('#builder-reset')) {
      PLAYERS.forEach(function (p) { picks[p.id] = p.team; });
      return render();
    }
  });

  document.addEventListener('click', function (e) {
    if (e.target.closest && e.target.closest('.lang-toggle__btn')) { setTimeout(render, 0); }
  });

  render();
})();
