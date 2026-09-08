/* ============================================================
   THE MATCH — handicap maths and the scoreboard
   Depends on data.js being loaded first (both are classic
   scripts with defer, so execution order is guaranteed).

   FORMAT: 36-hole cumulative hole points, best 2 of 3 net
   scores per hole, at a 90% Playing Handicap allowance.

   Nothing here is hard-coded. Every number on the page is
   derived from PLAYERS / COURSES / SCORES, so revising a
   handicap or a tee assignment in data.js propagates
   everywhere automatically.
   ============================================================ */
(function () {
  'use strict';

  /* ---- Pure computation ------------------------------------ */

  function courseHandicap(p, cid) {
    var C = COURSES[cid], t = C.tees[p.tees[cid]];
    return Math.round(p.hi * (t.slope / 113) + (t.cr - C.par));
  }

  function playingHandicap(p, cid) {
    return Math.round(courseHandicap(p, cid) * ALLOWANCE);
  }

  /* Strokes received on a hole: one everywhere for each full 18
     of handicap, plus one more on the hardest (PH mod 18) holes. */
  function strokesOnHole(ph, si) {
    return Math.floor(ph / 18) + (si <= (ph % 18) ? 1 : 0);
  }

  function player(id) {
    for (var i = 0; i < PLAYERS.length; i++) {
      if (PLAYERS[i].id === id) { return PLAYERS[i]; }
    }
    return null;
  }

  function gross(pid, cid, h) {
    var row = SCORES[cid] && SCORES[cid][pid];
    return row ? row[h] : null;
  }

  function net(pid, cid, h) {
    var g = gross(pid, cid, h);
    if (g === null || g === undefined) { return null; }
    var p = player(pid);
    return g - strokesOnHole(playingHandicap(p, cid), COURSES[cid].strokeIndex[h]);
  }

  function teamPlayers(tid) {
    return PLAYERS.filter(function (p) { return p.team === tid; });
  }

  /* Best two of three net scores. Null until at least two of the
     three have posted, so a partial hole never scores. */
  function teamHole(tid, cid, h) {
    var nets = teamPlayers(tid)
      .map(function (p) { return net(p.id, cid, h); })
      .filter(function (n) { return n !== null; })
      .sort(function (a, b) { return a - b; });
    if (nets.length < 2) { return null; }
    return nets[0] + nets[1];
  }

  function holePoints(cid, h) {
    var a = teamHole('laurel', cid, h);
    var b = teamHole('balsam', cid, h);
    if (a === null || b === null) { return null; }
    if (a < b) { return { laurel: POINTS_WIN, balsam: 0 }; }
    if (b < a) { return { laurel: 0, balsam: POINTS_WIN }; }
    return { laurel: POINTS_TIE, balsam: POINTS_TIE };
  }

  function leaderboard() {
    var pts = { laurel: 0, balsam: 0 }, played = 0;
    ['maggie', 'sequoyah'].forEach(function (cid) {
      for (var h = 0; h < 18; h++) {
        var r = holePoints(cid, h);
        if (r) { pts.laurel += r.laurel; pts.balsam += r.balsam; played++; }
      }
    });
    return { points: pts, holesPlayed: played };
  }

  /* ---- Rendering ------------------------------------------- */

  var $ = function (s, r) { return (r || document).querySelector(s); };
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) { n.className = cls; }
    if (text !== undefined && text !== null) { n.textContent = text; }
    return n;
  }

  /* Half points render as a proper vulgar fraction. */
  function fmtPts(v) {
    var whole = Math.floor(v);
    var half = (v - whole) >= 0.5;
    if (half) { return (whole === 0 ? '' : whole) + '½'; }
    return String(whole);
  }

  function isKo() { return document.documentElement.getAttribute('data-lang') !== 'en'; }
  function nameOf(p) { return isKo() && p.nameKo ? p.nameKo : p.name; }
  function teamName(t) { return isKo() && TEAMS[t].nameKo ? TEAMS[t].nameKo : TEAMS[t].name; }

  function buildBoard(cid) {
    var C = COURSES[cid];
    var tbl = el('table', 'board__table');

    // ---- head: hole numbers -------------------------------
    var thead = el('thead');
    var hr = el('tr');
    hr.appendChild(el('th', 'board__rowlab', isKo() ? '홀' : 'Hole'));
    for (var h = 0; h < 18; h++) { hr.appendChild(el('th', 'board__hole', String(h + 1))); }
    hr.appendChild(el('th', 'board__tot', isKo() ? '합계' : 'Tot'));
    thead.appendChild(hr);

    // ---- par and stroke index -----------------------------
    ['par', 'si'].forEach(function (kind) {
      var tr = el('tr', 'board__meta');
      tr.appendChild(el('th', 'board__rowlab',
        kind === 'par' ? (isKo() ? '파' : 'Par') : (isKo() ? '핸디' : 'S.I.')));
      for (var h = 0; h < 18; h++) {
        tr.appendChild(el('td', null, String(kind === 'par' ? C.parByHole[h] : C.strokeIndex[h])));
      }
      tr.appendChild(el('td', null, kind === 'par' ? String(C.par) : '—'));
      thead.appendChild(tr);
    });
    tbl.appendChild(thead);

    // ---- one body per team --------------------------------
    ['laurel', 'balsam'].forEach(function (tid) {
      var tb = el('tbody', 'board__team board__team--' + tid);

      teamPlayers(tid).forEach(function (p) {
        var ph = playingHandicap(p, cid);
        var tr = el('tr');
        var th = el('th', 'board__name');
        th.appendChild(el('span', null, nameOf(p)));
        th.appendChild(el('span', 'board__ph', 'PH ' + ph));
        tr.appendChild(th);

        var tot = 0, any = false;
        for (var h = 0; h < 18; h++) {
          var g = gross(p.id, cid, h);
          var recv = strokesOnHole(ph, C.strokeIndex[h]);
          var td = el('td', 'plate' + (g === null ? ' plate--empty' : ''));
          if (g !== null) {
            any = true; tot += g;
            var n = net(p.id, cid, h), par = C.parByHole[h];
            td.classList.add(n < par ? 'plate--under' : (n === par ? 'plate--even' : 'plate--over'));
            td.appendChild(el('span', 'plate__g', String(g)));
          }
          // Strokes received shown as dots, the way a card is dotted.
          if (recv > 0) {
            td.appendChild(el('span', 'plate__dots', recv === 1 ? '•' : '••'));
          }
          tr.appendChild(td);
        }
        tr.appendChild(el('td', 'board__tot', any ? String(tot) : '—'));
        tb.appendChild(tr);
      });

      // ---- team best-2 row ---------------------------------
      var br = el('tr', 'board__best');
      br.appendChild(el('th', 'board__rowlab', teamName(tid) + (isKo() ? ' 상위 2' : ' best 2')));
      for (var h2 = 0; h2 < 18; h2++) {
        var v = teamHole(tid, cid, h2);
        br.appendChild(el('td', null, v === null ? '—' : String(v)));
      }
      br.appendChild(el('td', 'board__tot', '—'));
      tb.appendChild(br);
      tbl.appendChild(tb);
    });

    // ---- points row ---------------------------------------
    var tf = el('tfoot');
    var pr = el('tr', 'board__points');
    pr.appendChild(el('th', 'board__rowlab', isKo() ? '홀 포인트' : 'Hole point'));
    var sub = { laurel: 0, balsam: 0 };
    for (var h3 = 0; h3 < 18; h3++) {
      var r = holePoints(cid, h3);
      var td2 = el('td');
      if (r) {
        sub.laurel += r.laurel; sub.balsam += r.balsam;
        if (r.laurel === r.balsam) { td2.textContent = '½'; td2.className = 'is-halved'; }
        else if (r.laurel > r.balsam) { td2.textContent = 'L'; td2.className = 'is-laurel'; }
        else { td2.textContent = 'B'; td2.className = 'is-balsam'; }
      } else { td2.textContent = '—'; }
      pr.appendChild(td2);
    }
    pr.appendChild(el('td', 'board__tot', fmtPts(sub.laurel) + '–' + fmtPts(sub.balsam)));
    tf.appendChild(pr);
    tbl.appendChild(tf);
    return tbl;
  }

  /* A plain "where you play from and what you get" table.
     No formula, no Course-versus-Playing distinction -- just the
     tee, the yardage and the number of shots. */
  function renderTeeTable() {
    var host = $('#tee-table');
    if (!host) { return; }
    var k = isKo();
    host.innerHTML = '';
    var tbl = el('table', 'table');

    var thead = el('thead'), hr = el('tr');
    [k ? '선수' : 'Player',
     k ? '매기 밸리' : 'Maggie Valley', k ? '타수' : 'Shots',
     k ? '세쿼이아' : 'Sequoyah',      k ? '타수' : 'Shots'
    ].forEach(function (t, i) { hr.appendChild(el('th', i % 2 === 0 && i ? 'num' : null, t)); });
    thead.appendChild(hr); tbl.appendChild(thead);

    var tb = el('tbody');
    PLAYERS.forEach(function (p) {
      var mv = COURSES.maggie.tees[p.tees.maggie];
      var sq = COURSES.sequoyah.tees[p.tees.sequoyah];
      var tr = el('tr');
      var th = el('th');
      th.appendChild(el('span', null, nameOf(p)));
      th.appendChild(el('span', 'board__ph', teamName(p.team)));
      tr.appendChild(th);
      tr.appendChild(el('td', null, mv.name + ' · ' + mv.yards.toLocaleString()));
      tr.appendChild(el('td', 'num', String(playingHandicap(p, 'maggie'))));
      tr.appendChild(el('td', null, sq.name + ' · ' + sq.yards.toLocaleString()));
      tr.appendChild(el('td', 'num', String(playingHandicap(p, 'sequoyah'))));
      tb.appendChild(tr);
    });
    tbl.appendChild(tb);
    host.appendChild(tbl);
  }

  /* The format proposals, rendered from FORMATS in data.js so a
     new idea is one object away from appearing on the page. */
  function renderOptions() {
    var host = $('#options');
    if (!host || typeof FORMATS === 'undefined') { return; }
    var k = isKo();
    host.innerHTML = '';
    FORMATS.forEach(function (f) {
      var card = el('article', 'option' + (f.recommended ? ' option--pick' : ''));
      if (f.recommended) {
        card.appendChild(el('span', 'option__tag', k ? '추천' : 'Suggested'));
      }
      card.appendChild(el('h3', 'option__name', k ? f.pickKo : f.pick));
      card.appendChild(el('p', 'option__how', k ? f.blurbKo : f.blurb));
      card.appendChild(el('p', 'option__why', k ? f.goodKo : f.good));
      host.appendChild(card);
    });
  }

  function renderSummary() {
    var lb = leaderboard();
    var host = $('#match-summary');
    if (!host) { return; }
    host.innerHTML = '';

    var wrap = el('div', 'tally');
    ['laurel', 'balsam'].forEach(function (tid, i) {
      if (i === 1) { wrap.appendChild(el('span', 'tally__dash', '–')); }
      var side = el('div', 'tally__side tally__side--' + tid);
      side.appendChild(el('p', 'tally__name', teamName(tid)));
      side.appendChild(el('p', 'tally__pts', fmtPts(lb.points[tid])));
      var names = teamPlayers(tid).map(function (p) {
        return nameOf(p) + ' (' + p.hi + ')';
      }).join(' · ');
      side.appendChild(el('p', 'tally__roster', names));
      wrap.appendChild(side);
    });
    host.appendChild(wrap);

    var status = el('p', 'tally__status');
    if (lb.holesPlayed === 0) {
      status.textContent = isKo()
        ? '아직 한 홀도 치지 않았습니다.'
        : 'Nothing played yet.';
    } else {
      status.textContent = (isKo() ? '36홀 중 ' : '') + lb.holesPlayed +
        (isKo() ? '홀 완료' : ' of 36 holes counted');
    }
    host.appendChild(status);
  }

  function renderAll() {
    renderSummary();
    renderTeeTable();
    renderOptions();
    [['maggie', '#board-maggie'], ['sequoyah', '#board-sequoyah']].forEach(function (pair) {
      var host = $(pair[1]);
      if (host) { host.innerHTML = ''; host.appendChild(buildBoard(pair[0])); }
    });
  }

  document.addEventListener('DOMContentLoaded', renderAll);
  if (document.readyState !== 'loading') { renderAll(); }
  // Re-render on a language switch so names and labels follow.
  document.addEventListener('click', function (e) {
    if (e.target.closest && e.target.closest('.lang-toggle__btn')) {
      setTimeout(renderAll, 0);
    }
  });

  // Exposed so the checks in tools/ and the console can exercise them.
  window.SMI_MATCH = {
    courseHandicap: courseHandicap, playingHandicap: playingHandicap,
    strokesOnHole: strokesOnHole, net: net, teamHole: teamHole,
    holePoints: holePoints, leaderboard: leaderboard
  };
})();
